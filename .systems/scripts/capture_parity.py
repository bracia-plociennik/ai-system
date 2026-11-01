"""Canonical AI System collection validation, shared by inventory and consumers."""

import json
from pathlib import Path
import re

from orchestration_compatibility import require, Blocked, contained, fingerprint, inspect_plan, integration_confirm
from qa_source_binding import git, verify_qa_binding, quality_gate, current_qa


def fields(path):
    values = {}
    for key, value in re.findall(r"^- ([^\n:]+):\s*([^\n]*)$", path.read_text(), re.M):
        require(key not in values, "duplicate capture field")
        values[key] = value.strip().strip("`")
    return values


def population(workspace, owner):
    workspace = Path(workspace).absolute()
    parts = owner.split("/")
    slug = r"[a-z0-9]+(?:-[a-z0-9]+)*"
    valid = owner == "capture-state" or bool(re.fullmatch(
        rf"(?:project-state/{slug}|(?:clients|owned-assets)/{slug}(?:/project-state/{slug})?)/capture-state", owner))
    require(valid, "foreign canonical capture namespace")
    root = contained(workspace, owner)
    result = []
    for path in sorted(root.glob("*.md")):
        if path.name in {"README.md", "capture-state.md"}:
            continue
        contained(workspace, path.relative_to(workspace).as_posix())
        result.append(path)
    return result


def proof(path):
    matches = re.findall(r"^## Capture Verification\s*\n```json\n(.*?)\n```", path.read_text(), re.M | re.S)
    require(len(matches) == 1, "missing/duplicate capture verification")
    return json.loads(matches[0])


def workflow_source_root(source):
    """Resolve policy evidence separately from the assessed product source."""
    import os
    import durable_runtime
    official = ((source / '.systems/scripts/resolve-workflow-env').is_file()
                and (source / '.systems/ai/core/repository-modes.md').is_file())
    if official and os.environ.get('AI_WORKFLOW_MODE') == 'official':
        durable_runtime.identity(source)
        return source  # Preserve explicit product-source test mode.
    system = durable_runtime.registered_system()
    shared = durable_runtime.shared_installation(system, source) if system else None
    if shared is not None:
        return shared
    if official:
        durable_runtime.identity(source)
        return source  # Explicit official Workflow source, not an inner clone.
    return source / 'ai-workflow'  # Existing standalone proof format.


def validate_formal(path, workspace):
    value = fields(path)
    require(value.get("Capture schema") in {"2", "3"}, "unsupported formal capture schema")
    state = value.get("State")
    require(state in {"pending-quality", "ready", "completed", "deferred", "owner-skipped", "blocked", "not-applicable"}, "invalid capture state")
    require(value.get("Privacy/scope check") == "pass", "formal capture privacy unresolved")
    require(value.get("`is_distilled` derived value") == ("true" if state == "completed" else "false"), "incorrect derived capture state")
    if state not in {"ready", "completed"}:
        return {"state": state, "current_quality": False}
    p = proof(path)
    require(p.get("work_id") == value.get("Work ID") and isinstance(p.get("project"), str) and p["project"], "capture identity mismatch")
    source = Path(p["source_root"]).absolute()
    evidence = contained(workspace, p["evidence_root"])
    require(p["source_head"] == git(source, "rev-parse", "HEAD") or value["Capture schema"] == "3", "capture source HEAD stale")
    qa = p.get("qa_refs")
    require(isinstance(qa, list) and qa and len({q["path"] for q in qa}) == len(qa), "missing/duplicate QA references")
    require(isinstance(p.get("task_ids"), list) and p["task_ids"]
            and len(p["task_ids"]) == len(set(p["task_ids"])), "missing/duplicate owning task identity")
    seen = set()
    for item in qa:
        qpath = contained(evidence, item["path"])
        require(fingerprint(qpath) == item["sha256"], "QA artifact changed")
        text = qpath.read_text()
        current = current_qa(text)
        identity_match = re.findall(r"^- Project/task identity: (.*)$", current, re.M)
        require(len(identity_match) == 1 and identity_match[0].startswith(p["project"] + ":"), "foreign QA scope")
        task = identity_match[0].split(":", 1)[1]
        require(task in p["task_ids"] and task not in seen, "duplicate or foreign task QA")
        seen.add(task)
        if value["Capture schema"] == "3":
            snapshot_file = contained(evidence, item["snapshot_path"])
            require(fingerprint(snapshot_file) == item["snapshot_sha256"], "snapshot file changed")
            snapshot = json.loads(snapshot_file.read_text())
            if snapshot["body"].get("binding") in {"runtime-scope-v1", "product-scope-v1"}:
                require(p["source_head"] == snapshot["body"]["head"], "capture assessed HEAD provenance mismatch")
            verify_qa_binding(snapshot, source, qpath, p["project"], task)
        else:
            quality_gate(text)
            require(text.splitlines().count('- QA verification contract: `full-qa-verification-v2`') == 1, "unsupported formal QA contract")
            segment = current.split("### Input Artifacts", 1)[0]
            for label in ("Artifact kind: implementation-quality", "Assessed source HEAD: " + p["source_head"], "Verdict: PASS", "Gate Decision: PASS"):
                require(segment.splitlines().count("- " + label) == 1, "current QA gate missing/duplicate")
            inputs = current.split("### Input Artifacts\n", 1)
            require(len(inputs) == 2, "missing current QA inputs")
            inputs = inputs[1].split("\n### ", 1)[0]
            rows = []
            for line in inputs.splitlines():
                if not line.startswith("|"):
                    continue
                cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
                if cells[0] == "Root kind" or all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                    continue
                require(len(cells) == 3 and re.fullmatch(r"[0-9a-f]{64}", cells[2]), "malformed QA input row")
                rows.append(cells)
            require(rows and any(kind == "approved-target-source" for kind, _, _ in rows), "QA lacks target-product proof")
            roots = {"approved-target-source": source, "owning-project-evidence": evidence}
            if any(kind == "workflow-source" for kind, _, _ in rows):
                roots["workflow-source"] = workflow_source_root(source)
            unique = set()
            for kind, name, sha in rows:
                name = name.strip()
                require((kind, name) not in unique, "duplicate QA input")
                require(kind in roots, "unsupported QA input root")
                unique.add((kind, name))
                require(fingerprint(contained(roots[kind], name)) == sha, "QA input drift")
    require(seen == set(p["task_ids"]), "owning QA coverage incomplete")
    if state == "completed":
        artifact = contained(workspace, value["Distillation artifact"])
        require(artifact.is_relative_to(evidence / "distillations"), "foreign distillation owner")
        text = artifact.read_text()
        for line in ("- Work ID: " + p["work_id"], "- Owning project: " + p["project"], "- Acceptance: accepted"):
            require(text.splitlines().count(line) == 1, "unaccepted or foreign distillation")
        require(fingerprint(artifact) == p["distillation_sha256"], "accepted distillation drift")
    return {"state": state, "current_quality": True}


def distillation_claim(workspace, ref):
    # Invalid siblings still participate in physical duplicate detection.
    candidate = (Path(workspace) / ref).resolve()
    if candidate.is_relative_to(Path(workspace).resolve()) and candidate.is_file():
        stat = candidate.stat()
        return (stat.st_dev, stat.st_ino)
    return str(candidate)


def collection(workspace, owner):
    paths = population(workspace, owner)
    parsed, claims, distillations, errors = {}, {}, {}, {}
    # Collect claims from invalid siblings too; a scoped selection never hides duplicates.
    for path in paths:
        text = path.read_text()
        for work in re.findall(r"^- Work ID:\s*`?([^`\n]+)`?", text, re.M):
            claims.setdefault(work.strip(), set()).add(path)
        for ref in re.findall(r"^- Distillation artifact:\s*`?([^`\n]+)`?", text, re.M):
            if ref.strip() not in {"none", ""}:
                distillations.setdefault(distillation_claim(workspace, ref.strip()), set()).add(path)
        try:
            parsed[path] = fields(path)
        except (Blocked, ValueError) as error:
            errors[path.name] = str(error)
    result = []
    for path in paths:
        try:
            require(path in parsed, "invalid record fields")
            row = parsed[path]
            if row.get("Capture schema", "1") == "1":
                result.append({"path": path.name, "state": row.get("State"), "current_quality": False, "quality": "unknown-historical-or-advisory"})
                continue
            require(len(claims.get(row.get("Work ID"), set())) == 1, "duplicate work claim in owning collection")
            ref = row.get("Distillation artifact", "none")
            require(ref == "none" or len(distillations.get(distillation_claim(workspace, ref), set())) == 1, "shared distillation claim")
            result.append(dict(validate_formal(path, workspace), path=path.name))
        except (Blocked, ValueError, KeyError, OSError) as error:
            errors[path.name] = str(error)
    return {"records": result, "errors": errors, "supporting_only": True}


def goal_collection(workspace, owner, required_work_ids):
    """Explicit current-goal selection; original exhaustive API is unchanged."""
    from maintenance_policy import select_goal
    from orchestration_compatibility import digest
    workspace = Path(workspace).absolute()
    physical_owner = contained(workspace, owner).parent
    full = collection(workspace, owner)
    claims = []
    inventory = {'records': [], 'invalid': [{'path': p, 'reason': e} for p, e in full['errors'].items()]}
    for path in population(workspace, owner):
        claim = {'path': path.name, 'owner_ref': str(physical_owner), 'work_ids': [],
                 'source_refs': [], 'distillation_refs': [], 'aliases': [], 'complete': False}
        try:
            row = fields(path)
            work = row['Work ID']
            require(bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/-]*', work)), 'unknown work identity')
            claim['work_ids'] = [work]
            require(not any('alias' in k.lower() or 'claim' in k.lower() for k in row), 'unresolved alias claims')
            require(row.get('Capture schema') in {'2', '3'}, 'historical dependency closure unknown')
            p = proof(path)
            require(p['work_id'] == work, 'foreign proof work identity')
            source = Path(p['source_root'])
            require(source.is_absolute() and source.resolve() == source and source.is_dir(), 'unknown source scope')
            evidence = contained(workspace, p['evidence_root'])
            require(evidence.is_relative_to(physical_owner), 'foreign evidence owner')
            for item in p['qa_refs']:
                qpath = contained(evidence, item['path'])
                require(fingerprint(qpath) == item['sha256'], 'unknown changed QA claims')
                claim['source_refs'].append(str(qpath))
                text = current_qa(qpath.read_text())
                identity = re.findall(r'^- Project/task identity: (.*)$', text, re.M)
                require(len(identity) == 1 and identity[0].startswith(p['project'] + ':'), 'foreign QA identity')
                require(identity[0].split(':', 1)[1] in p['task_ids'], 'foreign QA task coverage')
                if row['Capture schema'] == '2' or '### Input Artifacts\n' in text:
                    table = text.split('### Input Artifacts\n', 1)
                    require(len(table) == 2, 'missing dependency claims')
                    roots = {'approved-target-source': source, 'owning-project-evidence': evidence}
                    seen = set()
                    for line in table[1].split('\n### ', 1)[0].splitlines():
                        if not line.startswith('|'): continue
                        cells = [c.strip().strip('`') for c in line.strip('|').split('|')]
                        if cells[0] == 'Root kind' or all(re.fullmatch(r'[-: ]+', c) for c in cells): continue
                        require(len(cells) == 3 and cells[0] in {'approved-target-source', 'workflow-source', 'owning-project-evidence'} and re.fullmatch(r'[0-9a-f]{64}', cells[2]), 'unknown dependency row')
                        if cells[0] == 'workflow-source' and cells[0] not in roots:
                            roots[cells[0]] = workflow_source_root(source)
                        require(tuple(cells[:2]) not in seen, 'duplicate dependency row'); seen.add(tuple(cells[:2]))
                        claim['source_refs'].append(str(contained(roots[cells[0]], cells[1])))
                    require(seen, 'missing dependency closure')
                if row['Capture schema'] == '3':
                    snap = contained(evidence, item['snapshot_path'])
                    require(fingerprint(snap) == item['snapshot_sha256'], 'changed snapshot claims')
                    snapshot = json.loads(snap.read_text())
                    body = snapshot['body']
                    require(snapshot.get('sha256') == digest(body), 'unknown snapshot integrity')
                    require(body.get('binding') in {'product-scope-v1', 'runtime-scope-v1'}, 'unknown binding closure')
                    require(body.get('repository') == str(source) and body.get('project') == p['project']
                            and body.get('task') in p['task_ids'], 'foreign snapshot identity')
                    if body['binding'] == 'product-scope-v1':
                        claim['source_refs'] += [str(source / '.systems'), str(source / '.github')]
                        claim['source_refs'] += [str(source / f) for f in ('README.md', 'HUMANS.md', '.gitignore')]
                        dependencies = body['dependencies']
                        claim['source_refs'] += [d['path'] for d in dependencies['directories'] + dependencies['files']]
                    else:
                        claim['source_refs'].append(str(contained(source, body['runtime_root'])))
                        claim['source_refs'] += [d['path'] for d in body['dependencies']]
            if row.get('Distillation artifact', 'none') != 'none':
                claim['distillation_refs'].append(str(contained(workspace, row['Distillation artifact'])))
            claim['source_refs'] = sorted(set(claim['source_refs']))
            claim['complete'] = True
        except (Blocked, ValueError, KeyError, OSError, TypeError):
            pass
        claims.append(claim)
        if path.name not in full['errors']:
            record = next(r for r in full['records'] if r['path'] == path.name)
            inventory['records'].append(dict(record, work_id=claim['work_ids'][0] if claim['work_ids'] else 'unknown'))
    selected = select_goal(inventory, claims, str(physical_owner), required_work_ids)
    current = {r['work_id']: r for r in selected['records']}
    for work in required_work_ids:
        row = current.get(work)
        if row is None or not row.get('current_quality') or row['state'] not in {'ready', 'completed'}:
            selected['invalid'].append({'path': work, 'reason': 'required current Capture incomplete'})
    selected['gate_result'] = 'FAIL' if selected['invalid'] else 'PASS'
    return selected


def parent_completion(ledger, workspace, owner, work_id, plan_path, plan_sha256):
    """Recheck actual integrated outputs and the whole owning capture collection."""
    require(not Path(plan_path).is_symlink() and fingerprint(plan_path) == plan_sha256, "parent plan drift")
    plan = json.loads(Path(plan_path).read_text())
    inspect_plan(plan)
    expected = {u["id"]: u for u in plan["units"]}
    rows = list(ledger.read()["reservations"].values())
    require(rows and len(rows) == len(expected) and {r["unit"]["id"] for r in rows} == set(expected), "parent unit coverage incomplete")
    for row in rows:
        require(row["state"] == "integrated" and row["termination"] is True
                and row["unit"] == expected[row["unit"]["id"]], "parent integration incomplete")
        integration_confirm(row["integration"], row["review"])
    current = collection(workspace, owner)
    require(not current["errors"], "owning capture collection invalid")
    matches = [path for path in population(workspace, owner) if fields(path).get("Work ID") == work_id]
    require(len(matches) == 1, "parent capture missing or duplicate")
    capture = validate_formal(matches[0], workspace)
    require(capture["current_quality"] and capture["state"] == "completed", "parent current capture incomplete")
    p = proof(matches[0])
    require(set(p["task_ids"]) == {r["unit"]["task_id"] for r in rows}, "parent task coverage mismatch")
    return {"state": "ready-for-local-parent-gate", "formal_pass": False, "supporting_only": True}

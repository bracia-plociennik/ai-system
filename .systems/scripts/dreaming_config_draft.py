"""Build an explicit, reviewable local manifest; never activate it or a timer."""
import argparse
import json
import os
from pathlib import Path
from dreaming_guard import read_file, hash_bytes
from dreaming_universal_sources import frontmatter, CREDENTIAL, config
from dreaming_universal_evidence import slug, need, LENSES


def draft(home, owner, company, system_source, workflow_source, model, cli, cli_version, authority):
    """Workspace identities are explicit owner inputs, not inferred from basenames."""
    home = Path(home); owner_id, owner_path = owner; company_id, company_path = company
    slug(owner_id); slug(company_id)
    owner_path = Path(owner_path); company_path = Path(company_path); cli = Path(cli).resolve()
    recipients = {owner_id: {'adapter': 'owner-report', 'lenses': list(LENSES)},
                  'wep': {'adapter': 'wep', 'lenses': ['systems', 'company', 'brand']},
                  'ai-system': {'adapter': 'proposal', 'lenses': ['systems']},
                  'ai-workflow': {'adapter': 'proposal', 'lenses': ['systems']},
                  company_id: {'adapter': 'proposal', 'lenses': ['company', 'systems']}}
    entries = []; omitted = []
    def add(root, prefix, source_owner, subject_type, subject_id, cls, audiences, ownership=None):
        sid = 'source-' + hash_bytes((str(root)+'/'+prefix).encode())[:20]
        entry = {'id': sid, 'root': str(root), 'prefix': prefix, 'owner': source_owner,
                 'subject_type': subject_type, 'subject_id': subject_id, 'source_class': cls,
                 'audiences': audiences, 'sharing_authority': authority if source_owner != owner_id else ''}
        if ownership: entry['ownership_fields'] = ownership
        entries.append(entry)
    for prefix in ('core', 'context', 'memory', 'memory.md', 'decisions', 'distillations', 'checkpoints', 'capture-state'):
        if (owner_path/prefix).exists(): add(owner_path, prefix, owner_id, 'person', owner_id, 'personal', [owner_id])
    for prefix in ('personal-ops/check-ins', 'personal-ops/check-ins-v3', 'personal-ops/check-ins-v4', 'personal-ops/weekly-check-ins', 'personal-ops/weekly-check-ins-v3', 'personal-ops/weekly-check-ins-v4', 'notes/personal-brand', 'assets/brandbook'):
        if (owner_path/prefix).exists(): add(owner_path, prefix, owner_id, 'brand' if 'brand' in prefix else 'person', owner_id, 'personal', [owner_id])
    for prefix in ('status.md', 'core', 'context', 'memory.md', 'memory', 'decisions', 'distillations', 'checkpoints', 'capture-state'):
        if (company_path/prefix).exists(): add(company_path, prefix, company_id, 'company', company_id, 'work', [owner_id, company_id])
    for root, subject in ((Path(system_source), 'ai-system'), (Path(workflow_source), 'ai-workflow')):
        for prefix in ('.systems', 'README.md', 'HUMANS.md'):
            if (root/prefix).exists(): add(root, prefix, company_id, 'system', subject, 'source', [owner_id, 'ai-system', 'ai-workflow'])
    # Project routers are explicit project namespaces, not every repository's raw corpus.
    for workspace, wid in ((owner_path, owner_id), (company_path, company_id)):
        base = workspace/'project-state'
        if base.exists():
            for project in sorted(base.iterdir()):
                if not project.is_dir() or project.is_symlink(): continue
                try: slug(project.name)
                except ValueError: continue
                for name in ('status.md', 'memory.md', 'decisions', 'distillations', 'checkpoints', 'capture-state'):
                    prefix = str(project.relative_to(workspace)/name)
                    if (workspace/prefix).exists(): add(workspace, prefix, wid, 'project', project.name, 'work', [owner_id, 'wep'] + ([company_id] if wid == company_id else []))
    # Native immutable Work Entry records carry owner/project identity. Register
    # exact versions, never infer project identity from the work-log directory.
    native_gaps = 0
    import uuid
    from dreaming_provider_v1 import parse_json
    for path in sorted((owner_path/'work-log').glob('**/*.json')):
        try:
            data = read_file(str(owner_path), path.relative_to(owner_path).as_posix(), 1048576, prescreen=False)
            need(not CREDENTIAL.search(data), 'credential-marker')
            doc = parse_json(data.decode())
            if not isinstance(doc, dict) or not {'entry_id','work_id','owner_workspace','project_id','revision','schema_version','duration','source_refs','status'} <= set(doc): continue
            need(doc['owner_workspace'] in (owner_id, owner_path.name) and doc['schema_version'] == 1, 'native-owner-mismatch')
            slug(doc['project_id'])
            for key in ('entry_id','work_id'): need(str(uuid.UUID(doc[key])) == doc[key], 'invalid-native-identity')
            add(owner_path, path.relative_to(owner_path).as_posix(), owner_id, 'project', doc['project_id'], 'work', [owner_id,'wep'])
            entries[-1]['ownership_json'] = {key:doc[key] for key in ('owner_workspace','project_id','entry_id','work_id','schema_version')}
            if doc['owner_workspace'] != owner_id: entries[-1]['native_owner_id'] = doc['owner_workspace']
        except (OSError, ValueError, TypeError, KeyError, UnicodeError): native_gaps += 1
    # Mixed task store: metadata + an existing unique owner namespace decides ownership.
    # No owner guessed from filename, directory proximity or project-like prose.
    tasks = owner_path/'tasks/TaskNotes/Tasks'
    for path in sorted(tasks.glob('*.md')):
        identifier = hash_bytes(path.name.encode())[:20]
        try:
            data = read_file(str(owner_path), path.relative_to(owner_path).as_posix(), 1048576, prescreen=False)
            need(not CREDENTIAL.search(data), 'credential-marker')
            fields = frontmatter(data.decode())
            bindings = {k: fields.get(k, '') for k in ('workspace', 'owner_scope', 'client', 'project', 'owned_asset')}
            entities = [(kind, fields.get(key, '')) for kind, key in (('clients','client'), ('project-state','project'), ('owned-assets','owned_asset'))
                        if fields.get(key, '') not in ('', 'none', 'null', '~')]
            resolved = []
            for kind, entity in entities:
                slug(entity)
                matches = [(p, wid) for p, wid in ((owner_path, owner_id), (company_path, company_id)) if (p/kind/entity).is_dir() and not (p/kind/entity).is_symlink()]
                need(len(matches) == 1, 'ambiguous-task-owner'); resolved.append(matches[0][1])
            if resolved:
                need(len(set(resolved)) == 1, 'conflicting-task-owner'); wid = resolved[0]
            else:
                declared = fields.get('workspace', '').removesuffix('-workspace')
                need(declared in (owner_id, company_id) and fields.get('owner_scope') in ('workspace','primary-entity'), 'unknown-task-owner')
                wid = declared
            project = fields.get('project', '')
            is_project = project not in ('', 'none', 'null', '~') and any((p/'project-state'/project).is_dir() for p in (owner_path, company_path))
            audiences = [owner_id] + ([company_id] if wid == company_id else [])
            # Task notes can contain personal commentary: never route bodies to technical consumers.
            add(owner_path, path.relative_to(owner_path).as_posix(), wid,
                'project' if is_project else 'company' if wid == company_id else 'person',
                project if is_project else wid, 'personal' if wid == owner_id else 'work', audiences, bindings)
        except (OSError, ValueError, UnicodeError): omitted.append(identifier)
    value = {'schema_version': 2, 'authority_ref': authority, 'report_owner': owner_id,
             'workspace': str(owner_path), 'analyzer': {'model': model, 'version': 'universal-v2',
                'cli_version': cli_version, 'cli_sha256': hash_bytes(cli.read_bytes()), 'executable': str(cli)},
             'sources': entries, 'recipients': recipients, 'decisions': []}
    value['scope_gaps'] = {'task_unknown_owner_count': len(omitted), 'task_unknown_owner_ids': omitted, 'native_entry_gap_count': native_gaps}
    config(value)
    return value, {'task_ownership_gaps': omitted, 'task_gap_count': len(omitted),
                   'raw_exports_attachments_ocr': 'excluded', 'authority': 'draft-not-activation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('home', 'owner-id', 'owner-workspace', 'company-id', 'company-workspace', 'system-source',
                  'workflow-source', 'model', 'cli', 'cli-version', 'authority-ref', 'output'):
        parser.add_argument('--'+field, required=True)
    args = parser.parse_args()
    value, gaps = draft(args.home, (args.owner_id,args.owner_workspace), (args.company_id,args.company_workspace),
        args.system_source, args.workflow_source, args.model, args.cli, args.cli_version, args.authority_ref)
    path = Path(args.output)
    need(path.is_absolute() and path.parent.is_dir(), 'invalid-output')
    for target, payload in ((path,value), (path.with_suffix('.gaps.json'),gaps)):
        fd = os.open(target, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd,'w') as stream: json.dump(payload, stream, indent=2, ensure_ascii=False); stream.write('\n')
    print(json.dumps({'sources':len(value['sources']), 'task_ownership_gaps':gaps['task_gap_count'], 'activated':False}))


if __name__ == '__main__': main()

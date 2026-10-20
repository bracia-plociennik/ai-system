#!/usr/bin/env python3
"""Inspect product-source integration only; never infer model behavior or consent."""
import argparse
import json
from pathlib import Path
import re

FIELDS = {'phase-0-idea-validation': ['Goal versus proposed mechanism', 'Material assumption and evidence', 'Strongest supported objection or none with reason', 'Simpler or no-change option when viable', 'Reconsideration trigger', 'Recommendation and accepted tradeoff'], 'phase-1-architecture': ['Material assumption', 'What-if scenario', 'Consequence', 'System response', 'Verification', 'Reconsideration trigger'], 'phase-2-project-plan': ['Unnecessary work removed or retained with reason', 'Sequencing and dependency challenge', 'Small experiment or reason not applicable'], 'phase-3-specification': ['Material objection or scenario', 'Observable acceptance check or accepted limitation'], 'phase-4-implementation': ['New evidence against a premise', 'Covered correction or existing decision route'], 'phase-5-quality': ['Problem and premise validity', 'Overbuild and underbuild', 'Material objection disposition and verification'], 'phase-7-checkpoint': ['Material decision and basis', 'Accepted tradeoff and reconsideration trigger'], 'phase-8-final-check': ['Outcome and premise review', 'Reached reconsideration triggers and disposition'], 'phase-1-architecture-qa': ['Material What-if coverage and evidence', 'Feasible alternative and decision rationale'], 'phase-2-plan-qa': ['Unnecessary scope and early experiment review'], 'phase-3-spec-qa': ['Objection and scenario to acceptance-check mapping']}
COMMON = ('task-intake', 'intent-to-execution-brief', 'response-contract')
BAD = (
 r'\b(?:always|must)\s+(?:disagree|oppose|invent objections|fabricate objections)\b',
 r'\b(?:may|can|must|should)\s+(?:silently\s+)?(?:change|replace|expand)\s+(?:the\s+)?(?:owner.?s\s+)?(?:goal|scope|permissions|architecture)\s+without\s+(?:owner\s+)?approval\b',
 r'\b(?:skip|waive)\s+(?:required\s+)?(?:qa|approval|tests)\s+(?:because|when)\s+(?:the\s+)?agent\s+disagrees\b',
 r'\b(?:every|each)\s+(?:answer|response)\s+(?:must|shall)\s+(?:include|contain)\s+(?:an?\s+)?(?:objection|counterargument|criticism block)\b',
)

def read(root, relative):
    p = root / relative
    if any(x.is_symlink() for x in (p, *p.parents)):
        raise ValueError('linked integration source: ' + relative)
    if not p.is_file():
        raise ValueError('missing integration source: ' + relative)
    return p.read_text(encoding='utf-8')

def contradictions(text):
    # Check clauses independently; a safe prohibition cannot hide a later
    # enablement after "but", a sentence, colon or semicolon on the same line.
    for clause in re.split(r'[\n.;:]|\b(?:but|however|unless|yet)\b', text, flags=re.I):
        for pattern in BAD:
            for hit in re.finditer(pattern, clause, flags=re.I):
                prefix = clause[max(0, hit.start()-35):hit.start()].lower()
                if re.search(r'(?:do not|must not|never|forbid|prohibit)\s*$', prefix):
                    continue
                raise ValueError('contradictory judgment requirement: ' + hit.group(0))

def inspect(root):
    root = Path(root).resolve(strict=True)
    workflow = (root / '.systems/ai/core/repository-modes.md').is_file()
    routes = ['.systems/ai/core/'+s+'.md' for s in COMMON]
    routes += ['.systems/ai/core/'+s+'.md' for s in
               (('operating-model','agent-contract-details','quality-review','work-lead') if workflow else
                ('agent-startup','management-agent-contract','project-orchestration'))]
    routes += ['AGENTS.md' if workflow else '.systems/ai/templates/root/AGENTS.template.md']
    checked = ['.systems/ai/core/critical-judgment.md']
    contract = read(root, checked[0])
    if 'Critical judgment contract: critical-judgment-v1' not in contract:
        raise ValueError('unsupported critical judgment contract')
    for phrase in ('assessment, basis, consequence and recommendation','verified fact, inference, risk hypothesis and preference',
                   'Never manufacture objections or alternatives to fill a quota','permitted tradeoff','material new evidence',
                   'Structural checks verify source routing'):
        if phrase not in contract:raise ValueError('missing core boundary: '+phrase)
    for rel in routes:
        text = read(root, rel)
        if 'critical-judgment.md' not in text:raise ValueError('missing judgment route: '+rel)
        checked.append(rel)
    if workflow:
        for phase, fields in FIELDS.items():
            source = '.systems/ai/workflow/'+phase+'.md'
            body = read(root, source)
            if 'critical-judgment.md' not in body:raise ValueError('missing phase consumer: '+source)
            producer = '.systems/ai/templates/workflow/'+phase+'.template.md'
            text = read(root, producer)
            for field in fields:
                # Require an actual labeled producer field, not a heading or a
                # prose mention that happens to contain the expected words.
                if not re.search(r'^- '+re.escape(field)+r':[^\n]*$', text, re.M):
                    raise ValueError('missing producer field: '+producer+': '+field)
            checked.extend((source,producer))
    for rel in checked:contradictions(read(root,rel))
    return {'contract':'critical-judgment-v1','product':'ai-workflow' if workflow else 'ai-system',
            'source_files_checked':len(set(checked)),'producer_consumer_mapping':'complete',
            'evidence_role':'structural-supporting-only','native_behavior_verified':False,'owner_approval_verified':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args()
    try:print(json.dumps(inspect(a.root),sort_keys=True));return 0
    except (OSError,UnicodeError,ValueError) as e:print('Critical judgment source check failed: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())

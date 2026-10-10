"""Pure source capability verifier. No inference, execution or owner authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

SOURCES = {'AGENTS.md', '.systems/scripts/lib/style-profile.py', '.systems/scripts/style-profile'} | {
    '.systems/ai/core/' + name + '.md' for name in (
        'intent-to-execution-brief', 'style-profile', 'task-intake', 'command-routing',
        'prompt-composition', 'owner-decision-checkpoints', 'execution-modes',
        'delivery-constraints', 'permissions', 'risk-model', 'quality-review',
        'full-qa-verification', 'phase-commit-policy')}
FIELDS = {'contract', 'semantic_version', 'tested_commit', 'mode_mapping', 'delivery_mapping', 'sources'}
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')


class InvalidCapability(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidCapability(message)


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate capability field')
        value[key] = item
    return value


def git(root, *args):
    env = {key: value for key, value in os.environ.items() if key not in {'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'}}
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=env)
    require(result.returncode == 0, 'Git source evidence unavailable')
    return result.stdout


def unlinked(path):
    require(not any(part.is_symlink() for part in [path, *path.parents]), 'linked capability source/root')
    require(path.is_file(), 'missing capability source')


def candidate(root, profile_path):
    """Check candidate metadata/live bytes only; never advertise capability."""
    root, profile_path = Path(root), Path(profile_path)
    require(root.is_absolute() and root.is_dir(), 'explicit absolute Workflow root required')
    require(not any(p.is_symlink() for p in [root, *root.parents]), 'linked Workflow root')
    unlinked(profile_path)
    profile = json.loads(profile_path.read_text(), object_pairs_hook=unique)
    require(isinstance(profile, dict) and set(profile) == FIELDS, 'unknown capability fields')
    require(profile['contract'] == 'intent-to-execution-brief-v1' and type(profile['semantic_version']) is int
            and profile['semantic_version'] == 1, 'unknown capability version')
    require(profile['mode_mapping'] == {'auto': 'auto', 'human': 'human-coop'}, 'mode mapping mismatch')
    require(profile['delivery_mapping'] == {'auto-unconstrained': 'auto-unbounded'}, 'delivery mapping mismatch')
    require(isinstance(profile['tested_commit'], str) and HEX40.fullmatch(profile['tested_commit']), 'invalid tested source commit')
    require(isinstance(profile['sources'], dict) and set(profile['sources']) == SOURCES, 'unknown or incomplete source population')
    for relative, pin in profile['sources'].items():
        require(isinstance(pin, dict) and set(pin) == {'sha256', 'mode'}, 'unknown source pin fields')
        require(isinstance(pin['sha256'], str) and HEX64.fullmatch(pin['sha256'])
                and pin['mode'] in {'100644', '100755'}, 'invalid source pin')
        source = root / relative
        unlinked(source)
        require(hashlib.sha256(source.read_bytes()).hexdigest() == pin['sha256'], 'live source mismatch: ' + relative)
        require(('100755' if source.stat().st_mode & 0o100 else '100644') == pin['mode'], 'live source mode mismatch: ' + relative)
    return {'status': 'candidate-live-only', 'authority': 'none', 'capability_verified': False}


def verify(root, profile_path, expected_head):
    root, profile_path = Path(root), Path(profile_path)
    require(root.is_absolute() and root.is_dir(), 'explicit absolute Workflow root required')
    require(isinstance(expected_head, str) and HEX40.fullmatch(expected_head), 'expected reviewed HEAD required')
    require(not any(p.is_symlink() for p in [root, *root.parents]), 'linked Workflow root')
    require(Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()) == root.resolve(),
            'Workflow root is not an independent Git repository')
    unlinked(profile_path)
    try:
        profile = json.loads(profile_path.read_text(), object_pairs_hook=unique)
    except (json.JSONDecodeError, UnicodeError) as error:
        raise InvalidCapability('malformed capability') from error
    require(isinstance(profile, dict) and set(profile) == FIELDS, 'unknown capability fields')
    require(profile['contract'] == 'intent-to-execution-brief-v1' and type(profile['semantic_version']) is int
            and profile['semantic_version'] == 1, 'unknown capability version')
    require(profile['mode_mapping'] == {'auto': 'auto', 'human': 'human-coop'}, 'mode mapping mismatch')
    require(profile['delivery_mapping'] == {'auto-unconstrained': 'auto-unbounded'}, 'delivery mapping mismatch')
    commit = profile['tested_commit']
    require(isinstance(commit, str) and HEX40.fullmatch(commit), 'invalid tested source commit')
    require(git(root, 'rev-parse', 'HEAD').decode().strip() == expected_head, 'installed HEAD differs from accepted handoff')
    require(git(root, 'cat-file', '-t', commit).decode().strip() == 'commit', 'tested source is not a commit')
    require(isinstance(profile['sources'], dict) and set(profile['sources']) == SOURCES, 'unknown or incomplete source population')
    for relative, pin in profile['sources'].items():
        require(isinstance(pin, dict) and set(pin) == {'sha256', 'mode'}, 'unknown source pin fields')
        require(isinstance(pin['sha256'], str) and HEX64.fullmatch(pin['sha256'])
                and pin['mode'] in {'100644', '100755'}, 'invalid source pin')
        source = root / relative
        unlinked(source)
        require(hashlib.sha256(source.read_bytes()).hexdigest() == pin['sha256'], 'live source mismatch: ' + relative)
        live_mode = '100755' if source.stat().st_mode & 0o100 else '100644'
        require(live_mode == pin['mode'], 'live source mode mismatch: ' + relative)
        for revision in (commit, expected_head):
            row = git(root, 'ls-tree', revision, '--', relative).decode().strip().split()
            require(len(row) == 4 and row[0] == pin['mode'] and row[1] == 'blob' and row[3] == relative,
                    'committed source shape/mode mismatch: ' + relative)
            require(hashlib.sha256(git(root, 'cat-file', 'blob', row[2])).hexdigest() == pin['sha256'],
                    'committed source mismatch: ' + relative)
        rows = git(root, 'ls-files', '--stage', '--', relative).decode().strip().splitlines()
        require(len(rows) == 1, 'missing or conflicting source index: ' + relative)
        row = rows[0].split()
        require(len(row) == 4 and row[0] == pin['mode'] and row[2] == '0' and row[3] == relative,
                'index source mode/stage mismatch: ' + relative)
        require(hashlib.sha256(git(root, 'cat-file', 'blob', row[1])).hexdigest() == pin['sha256'],
                'index source mismatch: ' + relative)
    return {'status': 'source-bound', 'authority': 'support-metadata-only',
            'tested_commit': commit, 'accepted_head': expected_head, 'sources': len(SOURCES),
            'native_behavior_verified': False, 'owner_approval_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workflow-root', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--expected-head', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.workflow_root, args.profile, args.expected_head), sort_keys=True))
    except (InvalidCapability, OSError, TypeError) as error:
        parser.exit(1, 'Intent brief capability rejected: ' + str(error) + '\n')


if __name__ == '__main__':
    main()

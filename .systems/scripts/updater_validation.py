"""Change-selected updater verification. Unknown coverage stops; no automatic full QA."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE_CHECKS = ['check-privacy-boundary', 'check-checkout-role', 'check-shared-installation']
# Reviewed producer/consumer mappings, not file-provided commands. Extend coverage
# with a reviewed change; an unknown product delta must never silently skip tests.
CALORIE_PATHS = {
    '.systems/scripts/calculate-personal-ops-budgets',
    '.systems/scripts/personal_ops_spor_proposals.py',
    '.systems/scripts/render-personal-ops-daily-summary-v4',
    '.systems/scripts/render-personal-ops-weekly-summary',
    '.systems/scripts/tests/test_calorie_weekday_plan.py',
    '.systems/ai/core/personal-ops-budgets.md',
    '.systems/ai/templates/workspace/personal-ops/check-in-settings.local.template.md',
}
UPDATER_PATHS = {
    '.systems/scripts/update-from-upstream', '.systems/scripts/updater_validation.py',
    '.systems/scripts/tests/test_updater_validation.py',
    '.systems/scripts/check-validation-profiles',
    '.systems/ai/capabilities/task-efficiency-v1.json',
    '.systems/ai/core/validation-profiles.md', '.systems/ai/core/validation-routing.md',
    '.systems/ai/core/update-from-upstream.md',
    '.systems/ai/core/execution-efficiency.md', '.systems/ai/core/management-agent-contract.md',
    '.systems/ai/core/response-contract.md', '.systems/ai/templates/root/AGENTS.template.md',
}


def plan(paths: list[str]) -> dict:
    paths = sorted(set(paths))
    unknown = [path for path in paths if path not in CALORIE_PATHS | UPDATER_PATHS]
    if unknown:
        raise ValueError('Unmapped updater test coverage; reviewed mapping or explicit full verification required: ' + ', '.join(unknown))
    checks = list(BASE_CHECKS)
    tests = []
    if set(paths) & CALORIE_PATHS:
        checks += ['check-personal-ops', 'check-personal-ops-aggregates-v4', 'check-spor-proposals']
        tests += ['test_calorie_weekday_plan.py', 'test_daily_state_budget_display.py']
    if set(paths) & UPDATER_PATHS:
        checks += ['check-validation-profiles', 'check-execution-efficiency']
        tests += ['test_updater_validation.py']
    return {'contract': 'updater-targeted-validation-v1', 'changed_paths': paths,
            'checks': list(dict.fromkeys(checks)), 'tests': tests,
            'full_validation': False, 'evidence_scope': 'changed-product-only'}


def selected_changes(root: Path, base: str, target: str) -> list[str]:
    # Resolve revisions first: a revision supplied as data is never an option.
    ids = []
    for value in [base, target]:
        result = subprocess.run(['git','-C',str(root),'rev-parse','--verify',value+'^{commit}'],
                                text=True,capture_output=True,check=True)
        digest = result.stdout.strip()
        if len(digest) != 40 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid update revision')
        ids.append(digest)
    result = subprocess.run(['git','-C',str(root),'diff','--name-only','-z',*ids,'--'],capture_output=True,check=True)
    return [path for path in result.stdout.decode().split('\0') if path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--plan-only',action='store_true')
    args = parser.parse_args()
    try:
        selected = plan(selected_changes(ROOT,args.base,args.target))
        print(json.dumps(selected,ensure_ascii=False),flush=True)
        if args.plan_only:
            return 0
        # Existing runner retains product input guard, dependency closure, privacy
        # and compatibility checks. No cached green receipt or skipped smoke/full claim.
        subprocess.run([str(ROOT/'.systems/scripts/validate-ai-system'),'--profile','scoped',
                        '--checks',','.join(selected['checks'])],cwd=ROOT,check=True)
        for test in selected['tests']:
            subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','.systems/scripts/tests',
                            '-p',test],cwd=ROOT,check=True)
        print('UPDATER_TARGETED_COMPLETE scope=changed-product-only full_validation=false')
        return 0
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        print('STOP: updater targeted verification: '+str(exc),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

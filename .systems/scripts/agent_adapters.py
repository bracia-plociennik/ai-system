"""Owned, recoverable startup fragments. No provider credentials or task execution."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import tempfile
import uuid
from agent_context import (ContextError, concrete, registration, safe_bytes, strict_json,
                           workspace_registry, POLICY)

START = '<!-- ai-system:codex:v1:start -->'
END = '<!-- ai-system:codex:v1:end -->'
SOURCE_FILES = (*POLICY, '.systems/scripts/agent_context.py', '.systems/scripts/local_paths.py',
                '.systems/scripts/agent_adapters.py', '.systems/scripts/resolve-agent-context')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def snapshot(path):
    path = concrete(path)
    if not path.exists():
        return {'sha256': None, 'mode': None}
    return {'sha256': digest(safe_bytes(path)), 'mode': stat.S_IMODE(path.stat().st_mode)}


def mkdir_private(path):
    path = concrete(path)
    missing = []
    while not path.exists():
        missing.append(path)
        path = path.parent
    for item in reversed(missing):
        item.mkdir(mode=0o700)


def atomic_write(path, data, mode=0o600):
    path = concrete(path)
    mkdir_private(path.parent)
    fd, temporary = tempfile.mkstemp(prefix='.adapter-', dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def writer_lock(user_home):
    path = concrete(user_home) / '.config/ai-system/adapter.lock'
    mkdir_private(path.parent)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ContextError('unsafe adapter lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ContextError('another adapter writer is active', 4) from None
        yield
    finally:
        os.close(fd)


def owned_fragment(text):
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ContextError('ambiguous managed fragment', 4)
    if 'ai-system:codex:' in text and START not in text:
        raise ContextError('unknown managed fragment version', 3)
    if START not in text:
        return None
    match = re.search(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', text, re.S)
    if not match:
        raise ContextError('invalid managed fragment', 4)
    return match.group(0)


def source_digest(system_home):
    return digest(''.join(f'{rel}={digest(safe_bytes(system_home / rel))}\n'
                          for rel in SOURCE_FILES).encode())


def owner_root(system_home, workspace_id, asset_id, env):
    if not all(isinstance(x, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', x)
               for x in (workspace_id, asset_id)):
        raise ContextError('invalid adapter owner identity')
    rows, _ = workspace_registry(system_home, env)
    roots = [root for ident, root, _ in rows if ident == workspace_id]
    if len(roots) != 1:
        raise ContextError('adapter owner workspace unavailable', 3)
    asset = concrete(roots[0] / 'owned-assets' / asset_id)
    if not asset.is_dir():
        raise ContextError('adapter owner asset must already exist', 3)
    return asset / 'assets/agent-adapters/receipts/codex'


def fragment(system_home, receipt, transaction_id):
    command = shlex.quote(str(system_home / '.systems/scripts/resolve-agent-context'))
    inspect = shlex.quote(str(system_home / '.systems/scripts/manage-agent-adapter'))
    return f'''{START}
AI System startup marker: asys-codex-{transaction_id[:16]}
Receipt: {receipt}
Before task actions, inspect adapter state with {inspect} inspect --tool codex.
The receipt must be applied, its relevant source unchanged and user registration enabled; otherwise inspect only.
Resolve the actual absolute working directory with {command} --cwd <ABS-CWD> --tool codex.
Read {system_home}/.systems/ai/core/agent-startup.md and system-workflow-authority.md; then only matching task/project policy.
System leads covered configurable Workflow decisions through ONE human/delegated work-lead role and ONE procedure. Verify actual owner provenance, current revocation/scope and local phase/QA/tool gates before writes; metadata never grants consent.
Management role applies only to its installation. Registered repo/worktree ownership wins over personal default; unknown repos are not enrolled and receive no unrelated private memory. No full-home permission, automatic TaskNotes, canonical memory writes or extra agent process. Reserved owner decisions/final-owner-yes and factual QA remain binding.
Refresh on resume/compaction/CWD or policy change. Keep automatic instructions <=16KiB. Provider-native auto-memory control is not managed by this v1 adapter; never claim that control is enforced. Existing CLI memories setting must be observed separately before memory-policy claims.
{END}
'''


def build_plan(system_home, owner_workspace_id, owner_asset_id, *, user_home=None,
               codex_home=None, transaction_id=None, tool='codex'):
    if tool != 'codex':
        return {'schema_version': 1, 'tool': tool, 'status': 'design-only',
                'activation_supported': False, 'native_verification': 'unverified',
                'execution_authorized': False,
                'next': 'MVP adapter contract in agent-adapters.md; no installation or native test'}
    home = concrete(user_home or os.environ.get('HOME', str(Path.home())))
    env = dict(os.environ, HOME=str(home)); env.pop('AI_SYSTEM_HOME', None)
    system = concrete(system_home, environment=env)
    role = strict_json(system / 'ai-system.local.json')
    if not isinstance(role, dict) or role != {'schema_version': 1, 'role': 'management'} or type(role.get('schema_version')) is not int:
        raise ContextError('adapter requires explicit management installation', 3)
    codex = concrete(codex_home or os.environ.get('CODEX_HOME', str(home / '.codex')), environment=env)
    if not codex.is_relative_to(home):
        raise ContextError('v1 adapter requires a Codex home within the selected user home', 3)
    override = codex / 'AGENTS.override.md'
    if override.exists() and safe_bytes(override).strip():
        raise ContextError('global AGENTS.override.md shadows adapter; review required', 4)
    reg = home / '.config/ai-system/installation.json'
    before_reg = strict_json(reg) if reg.exists() else None
    if before_reg is not None:
        previous, previous_home, _, _ = registration(env)
        if (previous_home != system or previous['owner_workspace_id'] != owner_workspace_id
                or previous['owner_asset_id'] != owner_asset_id):
            raise ContextError('installation/owner rebind requires separate reviewed scope', 4)
    tx = transaction_id or uuid.uuid4().hex
    if not isinstance(tx, str) or not re.fullmatch(r'[a-f0-9]{32}', tx):
        raise ContextError('invalid transaction identity')
    receipts = owner_root(system, owner_workspace_id, owner_asset_id, dict(env, AI_SYSTEM_HOME=str(system)))
    receipt = receipts / tx / 'transaction.json'
    agents = codex / 'AGENTS.md'
    before_agents = safe_bytes(agents).decode('utf-8') if agents.exists() else ''
    old = owned_fragment(before_agents)
    if old:
        original = receipt_from_fragment(old, receipts)
        if original.get('fragment') != old or original.get('status') != 'applied':
            raise ContextError('managed fragment changed or interrupted; reconcile existing receipt', 4)
    new = fragment(system, receipt, tx)
    separator = '\n\n' if before_agents and not old else ''
    after_agents = before_agents.replace(old, new, 1) if old else before_agents + separator + new
    if len(after_agents.encode()) > 16384:
        raise ContextError('global guidance exceeds startup budget', 3)
    record = dict(schema_version=1, system_id=before_reg['system_id'] if before_reg else 'primary-system',
                  system_home=before_reg['system_home'] if before_reg else str(system), enabled=True,
                  adapter_ids=sorted(set((before_reg['adapter_ids'] if before_reg else []) + ['codex'])),
                  owner_workspace_id=owner_workspace_id, owner_asset_id=owner_asset_id)
    value = dict(schema_version=1, tool='codex', user_home=str(home), codex_home=str(codex),
                 system_home=str(system), owner_workspace_id=owner_workspace_id, owner_asset_id=owner_asset_id,
                 transaction_id=tx, receipt=str(receipt), registration_path=str(reg), agents_path=str(agents),
                 registration=record, registration_before=before_reg, source_digest=source_digest(system),
                 fragment=new, old_fragment=old, separator=separator,
                 before={'registration': snapshot(reg), 'agents': snapshot(agents)},
                 after_agents_sha256=digest(after_agents.encode()), execution_authorized=False,
                 memory_control='unsupported-by-v1-adapter; canonical writes still require actual scope')
    value['plan_id'] = digest(encoded(value))
    return value


def receipt_from_fragment(block, root):
    refs = re.findall(r'^Receipt: (.+)$', block, re.M)
    if len(refs) != 1:
        raise ContextError('managed receipt reference missing')
    path = concrete(refs[0])
    if not path.is_relative_to(root) or path.name != 'transaction.json':
        raise ContextError('foreign managed receipt', 4)
    result = strict_json(path)
    if result.get('schema_version') != 1 or result.get('fragment') != block:
        raise ContextError('unknown or changed receipt', 4)
    return result


def validate_plan(plan, *, require_current_source=True):
    if not isinstance(plan, dict) or plan.get('tool') != 'codex':
        raise ContextError('activation is supported only for Codex')
    required = {'schema_version','tool','user_home','codex_home','system_home','owner_workspace_id',
                'owner_asset_id','transaction_id','receipt','registration_path','agents_path',
                'registration','registration_before','source_digest','fragment','old_fragment','separator',
                'before','after_agents_sha256','execution_authorized','memory_control','plan_id'}
    if set(plan) != required or type(plan['schema_version']) is not int or plan['schema_version'] != 1:
        raise ContextError('unsupported adapter plan')
    unsigned = {key:value for key,value in plan.items() if key != 'plan_id'}
    if plan['plan_id'] != digest(encoded(unsigned)) or plan['execution_authorized'] is not False:
        raise ContextError('plan integrity invalid; integrity is not permission')
    home, system, codex = map(concrete, (plan['user_home'], plan['system_home'], plan['codex_home']))
    if not codex.is_relative_to(home):
        raise ContextError('foreign Codex home')
    env = dict(os.environ, HOME=str(home), AI_SYSTEM_HOME=str(system))
    root = owner_root(system, plan['owner_workspace_id'], plan['owner_asset_id'], env)
    tx = plan['transaction_id']
    if not isinstance(tx,str) or not re.fullmatch('[0-9a-f]{32}',tx):
        raise ContextError('invalid transaction identity')
    if (concrete(plan['receipt']) != root/tx/'transaction.json'
            or concrete(plan['registration_path']) != home/'.config/ai-system/installation.json'
            or concrete(plan['agents_path']) != codex/'AGENTS.md'
            or plan['fragment'] != fragment(system, root/tx/'transaction.json', tx)):
        raise ContextError('plan target/fragment identity mismatch')
    if require_current_source and source_digest(system) != plan['source_digest']:
        raise ContextError('relevant installation source changed',4)
    return home, system


def apply_plan(plan, *, approved=False):
    if not approved:
        raise ContextError('apply requires actual scoped approval and --approved')
    home, system = validate_plan(plan)
    reg, agents, receipt = map(Path, (plan['registration_path'],plan['agents_path'],plan['receipt']))
    with writer_lock(home):
        prior = strict_json(receipt) if receipt.exists() else None
        current_reg = strict_json(reg) if reg.exists() else None
        current_agents = safe_bytes(agents).decode() if agents.exists() else ''
        if prior and prior.get('plan_id') != plan['plan_id']:
            raise ContextError('receipt collision',4)
        if prior and prior.get('status') not in {'pending','applied'}:
            raise ContextError('transaction is no longer applicable',4)
        if prior and prior.get('status') == 'applied':
            if current_reg == plan['registration'] and owned_fragment(current_agents) == plan['fragment']:
                return dict(status='noop', receipt=str(receipt), execution_authorized=False)
            raise ContextError('applied installation changed; inspect before refresh',4)
        pending = dict(plan['registration'],enabled=False)
        if prior:
            if current_reg not in (plan['registration_before'],pending,plan['registration']):
                raise ContextError('registration changed during interrupted transaction',4)
            if snapshot(agents)['sha256'] not in (plan['before']['agents']['sha256'],plan['after_agents_sha256']):
                raise ContextError('global instructions changed during interrupted transaction',4)
        else:
            if snapshot(reg) != plan['before']['registration'] or snapshot(agents) != plan['before']['agents']:
                raise ContextError('stale adapter plan',4)
            fresh = build_plan(system,plan['owner_workspace_id'],plan['owner_asset_id'],user_home=home,
                               codex_home=plan['codex_home'],transaction_id=plan['transaction_id'])
            if fresh != plan:
                raise ContextError('adapter plan does not match current installation',4)
        transaction = dict(plan,status='pending',steps=[])
        atomic_write(receipt,encoded(transaction))
        # Global entry checks both enabled and this receipt's applied state.
        # Thus an interrupted enable/receipt write never publishes partial policy.
        atomic_write(reg,encoded(pending))
        if owned_fragment(current_agents) != plan['fragment']:
            old = plan['old_fragment']
            target = current_agents.replace(old,plan['fragment'],1) if old else current_agents+plan['separator']+plan['fragment']
            if digest(target.encode()) != plan['after_agents_sha256']:
                raise ContextError('global merge base changed',4)
            atomic_write(agents,target.encode(),plan['before']['agents']['mode'] or 0o600)
        atomic_write(reg,encoded(plan['registration']))
        transaction.update(status='applied',steps=['pending-receipt','disabled-registration','owned-fragment','enabled-registration','applied-receipt'])
        atomic_write(receipt,encoded(transaction))
    return dict(status='applied',receipt=str(receipt),execution_authorized=False,
                memory_control=plan['memory_control'])


def inspect_adapter(*, user_home=None, codex_home=None, tool='codex'):
    if tool != 'codex':
        return build_plan(None,None,None,tool=tool)
    home=concrete(user_home or os.environ.get('HOME',str(Path.home())))
    env=dict(os.environ,HOME=str(home));env.pop('AI_SYSTEM_HOME',None)
    record,system,_,_=registration(env)
    codex=concrete(codex_home or os.environ.get('CODEX_HOME',str(home/'.codex')),environment=env)
    override=codex/'AGENTS.override.md'
    if override.exists() and safe_bytes(override).strip():
        raise ContextError('global override shadows adapter',4)
    root=owner_root(system,record['owner_workspace_id'],record['owner_asset_id'],dict(env,AI_SYSTEM_HOME=str(system)))
    agents=codex/'AGENTS.md'
    block=owned_fragment(safe_bytes(agents).decode()) if agents.exists() else None
    receipt=receipt_from_fragment(block,root) if block else None
    active=bool(record['enabled'] and receipt and receipt['status']=='applied' and receipt['source_digest']==source_digest(system))
    return dict(schema_version=1,tool='codex',status='active' if active else 'disabled-or-incomplete',
                active=active,system_home=str(system),receipt_state=receipt['status'] if receipt else None,
                native_verification='unverified',memory_control='unsupported-by-v1-adapter',execution_authorized=False)


def disable_adapter(*, user_home=None, approved=False):
    if not approved:raise ContextError('disable requires actual scoped approval and --approved')
    home=concrete(user_home or os.environ.get('HOME',str(Path.home())))
    env=dict(os.environ,HOME=str(home));env.pop('AI_SYSTEM_HOME',None)
    with writer_lock(home):
        record,_,path,_=registration(env)
        atomic_write(path,encoded(dict(record,enabled=False)))
    return dict(status='disabled',execution_authorized=False)


def restore_receipt(path, *, approved=False, user_home=None):
    if not approved:
        raise ContextError('restore requires actual scoped approval and --approved')
    value = strict_json(concrete(path))
    plan = {key: val for key, val in value.items()
            if key not in {'status', 'steps', 'restore_before_sha256', 'restore_agents_sha256'}}
    home, _ = validate_plan(plan, require_current_source=False)
    if concrete(path) != concrete(plan['receipt']):
        raise ContextError('receipt path mismatch')
    if user_home is not None and concrete(user_home) != home:
        raise ContextError('foreign restore home')
    with writer_lock(home):
        reg, agents = Path(plan['registration_path']), Path(plan['agents_path'])
        current = strict_json(reg) if reg.exists() else None
        text = safe_bytes(agents).decode() if agents.exists() else ''
        pending = dict(plan['registration'], enabled=False)
        if value.get('status') == 'restored':
            return dict(status='noop', receipt=plan['receipt'], execution_authorized=False)
        if current not in (plan['registration'], pending, plan['registration_before']):
            raise ContextError('registration changed; restore requires review', 4)
        resuming = value.get('status') == 'restoring'
        if value.get('status') not in {'pending', 'applied', 'restoring'}:
            raise ContextError('unknown transaction state')
        current_hash = digest(text.encode())
        already_withdrawn = resuming and current_hash == value['restore_agents_sha256']
        if resuming and current_hash not in (value['restore_before_sha256'], value['restore_agents_sha256']):
            raise ContextError('instructions changed during restore; review required', 4)
        if not already_withdrawn:
            if owned_fragment(text) != plan['fragment']:
                # A pending apply may have stopped before writing its fragment.
                if not (value['status'] == 'pending' and snapshot(agents) == plan['before']['agents']):
                    raise ContextError('owned fragment changed; restore requires review', 4)
                restored = text
            else:
                owned = plan['fragment']
                if plan['separator'] and plan['separator'] + owned in text:
                    owned = plan['separator'] + owned
                restored = text.replace(owned, plan['old_fragment'] or '', 1)
            value.update(status='restoring', restore_before_sha256=current_hash,
                         restore_agents_sha256=digest(restored.encode()))
            atomic_write(Path(plan['receipt']), encoded(value))
            atomic_write(reg, encoded(pending))
            if not restored and plan['before']['agents']['sha256'] is None:
                if agents.exists(): agents.unlink()
            else:
                atomic_write(agents, restored.encode(), plan['before']['agents']['mode'] or 0o600)
        if plan['registration_before'] is None:
            if reg.exists(): reg.unlink()
        else:
            atomic_write(reg, encoded(plan['registration_before']))
        value['status'] = 'restored'
        atomic_write(Path(plan['receipt']), encoded(value))
    return dict(status='restored', receipt=plan['receipt'], execution_authorized=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=('inspect','plan','apply','disable','restore'),nargs='?',default='inspect')
    parser.add_argument('--tool',choices=('codex','claude-code','generic'),default='codex')
    parser.add_argument('--system-home');parser.add_argument('--owner-workspace-id');parser.add_argument('--owner-asset-id')
    parser.add_argument('--user-home');parser.add_argument('--codex-home');parser.add_argument('--plan');parser.add_argument('--receipt')
    parser.add_argument('--approved',action='store_true')
    args=parser.parse_args()
    try:
        if args.tool!='codex' and args.operation not in {'inspect','plan'}:
            raise ContextError('non-Codex adapters are design-only',3)
        if args.operation=='inspect':out=inspect_adapter(user_home=args.user_home,codex_home=args.codex_home,tool=args.tool)
        elif args.operation=='plan':out=build_plan(args.system_home,args.owner_workspace_id,args.owner_asset_id,user_home=args.user_home,codex_home=args.codex_home,tool=args.tool)
        elif args.operation=='apply':out=apply_plan(strict_json(Path(args.plan)),approved=args.approved)
        elif args.operation=='disable':out=disable_adapter(user_home=args.user_home,approved=args.approved)
        else:out=restore_receipt(Path(args.receipt),approved=args.approved,user_home=args.user_home)
        print(json.dumps(out,indent=2));return 0
    except (ContextError,OSError,ValueError,TypeError,KeyError) as error:
        print(json.dumps({'status':'unavailable','error':str(error),'execution_authorized':False}))
        return error.code if isinstance(error,ContextError) else 3


if __name__=='__main__':raise SystemExit(main())

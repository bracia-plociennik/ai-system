"""Cooperative validation input stability; never grants semantic PASS or a write lock."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

CONTRACT = 'product-v1'
ROOT_FILES = ('.gitignore', 'README.md', 'HUMANS.md')
SKIP = {'__pycache__', '.git'}

class InputChanged(ValueError):
    pass

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def checksum(value):
    return hashlib.sha256(encoded(value)).hexdigest()

def unlinked(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise InputChanged('validation input is linked')
    return path

def signature(s):
    return [s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns]

def outputs_identity(fds):
    result = []
    for fd in fds:
        try:
            s = os.fstat(fd)
            if stat.S_ISREG(s.st_mode):
                result.append([s.st_dev, s.st_ino])
        except OSError:
            pass
    return result

def file_entry(path, *, skip_identities=()):
    before = path.lstat()
    if [before.st_dev, before.st_ino] in skip_identities:
        return None
    if not stat.S_ISREG(before.st_mode):
        raise InputChanged('validation input is not a regular unlinked file')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    fd = os.open(path, flags)
    try:
        opened = os.fstat(fd)
        if signature(opened) != signature(before):
            raise InputChanged('validation input changed while opening')
        h = hashlib.sha256()
        while chunk := os.read(fd, 1024 * 1024):
            h.update(chunk)
        if signature(os.fstat(fd)) != signature(before):
            raise InputChanged('validation input changed while reading')
    finally:
        os.close(fd)
    if signature(path.lstat()) != signature(before):
        raise InputChanged('validation input replaced while reading')
    return {'sha256': h.hexdigest(), 'executable': bool(before.st_mode & 0o111), 'stat': signature(before)}

def namespace(root, exclusions=(), skip_identities=(), include_directories=True):
    root = unlinked(root)
    if not root.exists():
        raise InputChanged('selected validation input root is missing')
    entries = {}
    def visit(path):
        rel = path.relative_to(root).as_posix() if path != root else '.'
        if path in exclusions:
            return
        info = path.lstat()
        if stat.S_ISDIR(info.st_mode):
            # Directory inode/mode catch replacement; mtime is not a read input:
            # transient test fixtures may be created and removed by this run.
            if include_directories:
                entries[rel + '/'] = {'directory': [info.st_dev, info.st_ino, info.st_mode]}
            for child in sorted(path.iterdir()):
                if child.name not in SKIP and child.suffix != '.pyc':
                    visit(child)
        else:
            item = file_entry(path, skip_identities=skip_identities)
            if item is not None:
                entries[rel] = item
    visit(root)
    return entries

def product(root):
    root = unlinked(root)
    result = subprocess.run(['git','-C',str(root),'ls-files','-z','--','.systems','.github',*ROOT_FILES,'AGENTS.md'], capture_output=True)
    if result.returncode and ((root/'.git').exists() or (root/'.git').is_symlink()):
        raise InputChanged('Git source inventory is unavailable')
    tracked = [os.fsdecode(p) for p in result.stdout.split(b'\0') if p]
    if result.returncode and (root/'AGENTS.md').is_file():
        tracked.append('AGENTS.md')
    entries = {}
    for name in ('.systems', '.github'):
        path = root / name
        if path.exists() or path.is_symlink():
            entries.update({name+'/'+k:v for k,v in namespace(path).items()})
    for name in ROOT_FILES + (('AGENTS.md',) if 'AGENTS.md' in tracked else ()):
        path = root/name
        if path.exists() or path.is_symlink():
            entries[name] = file_entry(path)
    for name in tracked:
        if not SKIP.intersection(Path(name).parts) and not name.endswith('.pyc') and not (root/name).exists():
            # Missing tracked inputs remain distinguishable from never-declared files.
            entries[name] = {'missing': True}
    return entries

def product_digest(root):
    # Stable source identity excludes inode/timestamps, but includes names/modes.
    return digest_entries(product(root))

def digest_entries(data):
    stable = {k:({'directory': True} if 'directory' in v else {a:b for a,b in v.items() if a!='stat'}) for k,v in data.items()}
    return checksum({'scope':CONTRACT,'inputs':stable})

class Guard:
    def __init__(self, root, runtime_roots=(), outputs=(), output_fds=(1,2)):
        self.root = str(unlinked(root))
        self.runtime_roots = [str(unlinked(p)) for p in runtime_roots]
        self.outputs = [str(Path(os.path.abspath(p))) for p in outputs if p]
        if any(not Path(p).exists() for p in self.runtime_roots):
            raise InputChanged('selected validation input root is missing')
        self.runtime_identities = {p:signature(Path(p).stat())[:2] for p in self.runtime_roots}
        protected = [Path(self.root)/n for n in ('.systems','.github',*ROOT_FILES,'AGENTS.md')]
        if any(Path(p)==q or Path(p).is_relative_to(q) for p in self.outputs for q in protected):
            raise InputChanged('product inputs cannot be output-exempt')
        if any(Path(p)==Path(r) or Path(p).is_dir() for p in self.outputs for r in self.runtime_roots):
            raise InputChanged('only exact output files may be exempt')
        self.output_identities = outputs_identity(output_fds)
        self.before = self.observe()
        if self.observe() != self.before:
            raise InputChanged('validation inputs changed during preflight')

    def observe(self):
        if any(signature(Path(p).stat())[:2] != identity for p,identity in self.runtime_identities.items()):
            raise InputChanged('selected validation input root was replaced')
        return {'source':product(self.root), 'runtime':{
            p:namespace(p, exclusions={Path(v) for v in self.outputs}, skip_identities=self.output_identities, include_directories=False)
            for p in self.runtime_roots}}

    def finish(self):
        try:
            after = self.observe()
        except (OSError, ValueError) as exc:
            raise InputChanged('validation input-changed: unreadable, linked or missing input') from exc
        if after != self.before:
            scope = 'source' if after['source'] != self.before['source'] else 'selected-runtime'
            raise InputChanged('validation input-changed: '+scope)
        return {'contract':CONTRACT, 'state':'stable', 'source_digest':digest_entries(after['source']),
                'runtime_scopes':len(self.runtime_roots), 'supporting_only':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['start','finish','digest'])
    parser.add_argument('--root',type=Path)
    parser.add_argument('--state',type=Path)
    parser.add_argument('--input-root',action='append',default=[])
    parser.add_argument('--output',action='append',default=[])
    args=parser.parse_args()
    try:
        if args.action=='digest':
            print(product_digest(args.root));return 0
        if args.action=='start':
            guard=Guard(args.root,args.input_root,args.output,output_fds=(3,4))
            with open(unlinked(args.state), 'x', opener=lambda p,f:os.open(p,f | getattr(os, 'O_NOFOLLOW', 0),0o600)) as stream:
                json.dump(guard.__dict__,stream)
            print('VALIDATION_INPUT_GUARD state=started scope='+CONTRACT)
        else:
            with unlinked(args.state).open() as stream:
                value=json.load(stream)
            guard=Guard.__new__(Guard);guard.__dict__.update(value)
            print('VALIDATION_INPUT_GUARD '+json.dumps(guard.finish(),sort_keys=True))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print('VALIDATION_INPUT_GUARD state=input-changed reason='+str(exc),file=sys.stderr)
        return 75

if __name__=='__main__':
    raise SystemExit(main())

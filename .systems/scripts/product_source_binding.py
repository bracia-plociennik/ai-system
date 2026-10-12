"""Complete product and QA dependency equality; HEAD is assessed provenance."""
from pathlib import Path
from orchestration_compatibility import require, identity, digest
from runtime_source_binding import namespace, external_file
from qa_source_binding import git

PRODUCT_DIRECTORIES = ('.systems', '.github')
PRODUCT_FILES = ('README.md', 'HUMANS.md', '.gitignore')


def product_population(repo):
    repo = Path(repo).absolute()
    require(repo.is_dir() and repo.resolve() == repo, 'unsafe product repository')
    population = {}
    for name in PRODUCT_DIRECTORIES:
        path = repo / name
        require(not path.is_symlink(), 'linked product namespace')
        if path.exists():
            population[name] = namespace(path, [])
        else:
            require(name == '.github', 'required product namespace missing')
            population[name] = None
    for name in PRODUCT_FILES:
        require((repo / name).is_file(), 'required product file missing or special')
        population[name] = external_file(str(repo / name))
    # Publication's explicit runtime boundary remains separate from product inputs.
    for name in git(repo, 'ls-files', '-z').split('\0'):
        if name:
            require(name in PRODUCT_FILES or any(name.startswith(n + '/') for n in PRODUCT_DIRECTORIES)
                    or name.startswith('ai-workflow-workspace/'), 'unknown tracked product boundary')
    return population


def dependency_population(directories, files, repo):
    require(isinstance(directories, list) and isinstance(files, list), 'invalid QA dependencies')
    paths = directories + files
    require(paths and all(isinstance(p, str) and Path(p).is_absolute() for p in paths), 'missing absolute QA dependencies')
    require(len(set(paths)) == len(paths), 'duplicate QA dependency')
    roots = [Path(p) for p in paths]
    for i, root in enumerate(roots):
        require(root.resolve() == root and not any(p.is_symlink() for p in (root, *root.parents)), 'linked QA dependency')
        require(not any(root.is_relative_to(Path(repo) / n) for n in PRODUCT_DIRECTORIES)
                and root not in [Path(repo) / n for n in PRODUCT_FILES], 'QA dependency aliases product input')
        require(not any(root.is_relative_to(other) or other.is_relative_to(root)
                        for other in roots[:i]), 'overlapping QA dependencies')
    require(all(Path(p).is_file() for p in files), 'missing or special QA dependency file')
    return {'directories': [{'path': p, 'population': namespace(p, [])} for p in directories],
            'files': [external_file(p) for p in files]}


def product_snapshot(repo, project, task, dependency_directories=(), dependency_files=()):
    repo = Path(repo).absolute()
    require(all(isinstance(x, str) and x for x in (project, task)), 'missing product QA scope')
    require(git(repo, 'rev-parse', '--show-toplevel') == str(repo), 'product source must be Git root')
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = repo / common
    body = {'schema': 2, 'role': 'implementation-quality', 'binding': 'product-scope-v1',
            'project': project, 'task': task, 'repository': str(repo),
            'repository_identity': identity(repo), 'common_identity': identity(common),
            'head': git(repo, 'rev-parse', 'HEAD'), 'population': product_population(repo),
            'dependencies': dependency_population(list(dependency_directories), list(dependency_files), repo)}
    return {'body': body, 'sha256': digest(body)}


def verify_product_snapshot(value, repo):
    require(isinstance(value, dict) and value.get('sha256') == digest(value.get('body')), 'product snapshot fingerprint mismatch')
    body = value['body']
    require(set(body) == {'schema', 'role', 'binding', 'project', 'task', 'repository',
                         'repository_identity', 'common_identity', 'head', 'population', 'dependencies'}, 'invalid product snapshot fields')
    require(body['schema'] == 2 and body['role'] == 'implementation-quality'
            and body['binding'] == 'product-scope-v1', 'unsupported product snapshot')
    repo = Path(repo).absolute()
    require(body['repository'] == str(repo) and body['repository_identity'] == identity(repo), 'product repository identity changed')
    require(git(repo, 'rev-parse', '--show-toplevel') == str(repo), 'product source must be Git root')
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = repo / common
    require(identity(common) == body['common_identity'], 'product common Git identity changed')
    require(isinstance(body['head'], str) and __import__('re').fullmatch(r'[0-9a-f]{40,64}', body['head']), 'invalid product assessed HEAD')
    require(git(repo, 'cat-file', '-t', body['head']) == 'commit', 'product provenance commit missing')
    require(product_population(repo) == body['population'], 'product source population drift')
    deps = body['dependencies']
    require(isinstance(deps, dict) and set(deps) == {'directories', 'files'}
            and isinstance(deps['directories'], list) and isinstance(deps['files'], list), 'invalid product QA dependencies')
    require(all(isinstance(d, dict) and set(d) == {'path', 'population'} for d in deps['directories'])
            and all(isinstance(d, dict) and set(d) == {'path', 'mode', 'sha256'} for d in deps['files']), 'invalid QA dependency fields')
    require(dependency_population([d['path'] for d in deps['directories']],
                                  [d['path'] for d in deps['files']], repo) == deps, 'product QA dependency drift')
    return {'equivalent': True, 'binding': 'product-scope-v1', 'assessed_head': body['head'],
            'current_head': git(repo, 'rev-parse', 'HEAD'), 'supporting_only': True}

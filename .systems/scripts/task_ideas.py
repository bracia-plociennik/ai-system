"""SilverBullet idea checkboxes in the canonical TODO section."""
import json
import re
import uuid

SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
KINDS = {'correction', 'stage-extension', 'unrelated'}


def plain(value):
    return (isinstance(value, str) and bool(value.strip()) and
            not any(ord(c) < 32 or c in '\x85\u2028\u2029' for c in value) and
            '<' not in value and '>' not in value)


def merge_idea(text, request):
    base = {'id', 'text', 'source', 'parent_task_id', 'parent_stage_id', 'kind'}
    resolution = {'disposition', 'evidence'}
    if not isinstance(request, dict) or set(request) not in (base, base | resolution):
        raise ValueError('invalid idea fields')
    if any(not plain(v) for v in request.values()):
        raise ValueError('idea values must be single-line plain text')
    if not SLUG.fullmatch(request['id']) or not SLUG.fullmatch(request['parent_stage_id']):
        raise ValueError('invalid idea or stage identity')
    if str(uuid.UUID(request['parent_task_id'])) != request['parent_task_id'] or request['kind'] not in KINDS:
        raise ValueError('invalid idea parent or kind')
    resolved = resolution <= request.keys()
    if resolved and request['disposition'] not in {'accepted', 'deferred', 'declined', 'covered'}:
        raise ValueError('invalid idea disposition')
    raw = re.search(r'^## Working dump[ \t]*\r?$', text, re.M)
    active = text[:raw.start()] if raw else text
    headings = list(re.finditer(r'^## TODO[ \t]*\r?$', active, re.M))
    if len(headings) != 1:
        raise ValueError('missing or ambiguous TODO')
    start = headings[0].end()
    following = re.search(r'^## ', active[start:], re.M)
    end = start + following.start() if following else len(active)
    body = text[start:end]
    opening = '<!-- ai-system-idea:' + request['id'] + ':start -->'
    closing = '<!-- ai-system-idea:' + request['id'] + ':end -->'
    if opening not in body and closing not in body:
        if resolved:
            raise ValueError('capture idea before resolving it')
        payload = json.dumps(request, ensure_ascii=False, sort_keys=True)
        block = (opening + '\n- [ ] Ocenić pomysł — ' + request['text'] + '\n' +
                 '<!-- idea-data ' + payload + ' -->\n' + closing + '\n')
        return text[:end].rstrip('\n') + '\n\n' + block + '\n' + text[end:]
    if body.count(opening) != 1 or body.count(closing) != 1:
        raise ValueError('ambiguous idea markers')
    left, right = body.index(opening), body.index(closing)
    if right < left:
        raise ValueError('invalid idea marker order')
    block = body[left:right]
    metadata = re.findall(r'^<!-- idea-data (.+) -->$', block, re.M)
    if len(metadata) != 1:
        raise ValueError('missing or ambiguous idea metadata')
    previous = json.loads(metadata[0])
    if {key: previous.get(key) for key in base} != {key: request[key] for key in base}:
        raise ValueError('idea identity already has different content')
    if not resolved:
        return text
    if resolution <= previous.keys():
        if previous != request:
            raise ValueError('resolved idea requires explicit new decision')
        return text
    checks = list(re.finditer(r'^- \[[ xX]\] .+$', block, re.M))
    if len(checks) != 1:
        raise ValueError('ambiguous idea checkbox')
    check = checks[0]
    updated = block[:check.start()] + check[0].replace('- [ ]', '- [x]', 1) + block[check.end():]
    updated = updated.replace('<!-- idea-data ' + metadata[0] + ' -->',
                              '<!-- idea-data ' + json.dumps(request, ensure_ascii=False, sort_keys=True) + ' -->')
    updated += 'Rozstrzygnięcie — ' + request['disposition'] + '. Dowód — ' + request['evidence'] + '\n'
    return text[:start] + body[:left] + updated + body[right:] + text[end:]

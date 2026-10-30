"""Task identity at actual creation; legacy creation dates are never inferred."""
from datetime import datetime, timezone
import json
import re
import uuid


def new_identity(at=None):
    value = (at or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()
    return {'task_id': str(uuid.uuid4()), 'created_at': value}


def initialize_markdown(text, *, created=False, at=None):
    match = re.match(r'\A(?:\ufeff)?---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)', text)
    if not match:
        raise ValueError('task-frontmatter-required')
    header = match[1]
    if re.search(r"^[\"'](?:type|task_id|created_at)[\"'][ \t]*:", header, re.M):
        raise ValueError('ambiguous-task-metadata-key')
    if len(re.findall(r'^type:', header, re.M)) != 1:
        raise ValueError('duplicate-task-metadata-field')
    if not re.search(r'^type:[ \t]*(?:task|"task"|\x27task\x27)[ \t]*(?:#.*)?$', header.replace('\r\n', '\n'), re.M):
        raise ValueError('task-type-required')
    updates = {}
    ids = re.findall(r'^(?:task_id|"task_id"|\x27task_id\x27)[ \t]*:(.*)$', header, re.M)
    if len(ids) > 1:
        raise ValueError('duplicate-task-id')
    raw = ids[0].strip().strip('"\x27') if ids else ''
    if raw:
        if str(uuid.UUID(raw)) != raw:
            raise ValueError('invalid-task-id')
    else:
        updates['task_id'] = str(uuid.uuid4())
    if created:
        updates['created_at'] = new_identity(at)['created_at']
    newline = '\r\n' if '\r\n' in text else '\n'
    for key, value in updates.items():
        occurrences = re.findall(r'^(?:' + key + '|"' + key + '"|\x27' + key + '\x27)[ \t]*:.*$', header, re.M)
        if len(occurrences) > 1:
            raise ValueError('duplicate-task-metadata-field')
        line = key + ': ' + json.dumps(value)
        if occurrences:
            header = header.replace(occurrences[0].rstrip('\r'), line)
        else:
            header += newline + line
    return text[:match.start(1)] + header + text[match.end(1):]

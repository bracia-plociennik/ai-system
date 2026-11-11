"""Versioned, inert SPOR question data. No I/O, inference or authority grants."""
import re

CONTRACT = 'spor-question-queue-v1'
START = '<!-- spor-questions:start -->'
END = '<!-- spor-questions:end -->'
BLOCK = re.compile(re.escape(START) + r'\n.*?\n' + re.escape(END), re.S)
FULL_QUESTION = {
    'daily': 'Jeśli dzisiaj miałoby być ostatnim dniem mojego życia, czy chciałbym zrobić to, co zaplanowałem do zrobienia na dziś? (W takim sensie, że gdybym regularnie miał robić takie rzeczy, czy byłbym zadowolony z kierunku życia?)',
    'weekly': 'Jeśli przyszły tydzień miałby być ostatnim tygodniem mojego życia, czy chciałbym zrobić to, co zaplanowałem do zrobienia na przyszły tydzień? (W takim sensie, że gdybym regularnie miał robić takie rzeczy, czy byłbym zadowolony z kierunku życia?)',
}


def plain(value):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > 8000:
        raise ValueError('Invalid question text')
    if '<!--' in value or re.search(r'(?m)^(?:#{1,6} |---\s*$)', value):
        raise ValueError('Question cannot replace form structure')
    from personal_ops_spor_proposals import SECRET
    if SECRET.search(value):
        raise ValueError('Secret-like question rejected')
    return value


def validate(queue, mode, field_map, fields):
    if (not isinstance(queue, dict) or set(queue) - {'contract', 'items', 'overflow_reason'}
            or queue.get('contract') != CONTRACT or not isinstance(queue.get('items'), list)
            or len(queue['items']) > len(field_map) + 10):
        raise ValueError('Invalid question queue')
    seen = set(); covered = set(); texts = set(); essential = 0
    alignment = next(k for k, v in field_map.items() if v['label'].startswith('Odpowiedź:'))
    alignment_unknown = 'UNKNOWN' in fields[alignment]
    life_count = 0
    for q in queue['items']:
        if (not isinstance(q, dict) or set(q) - {'id', 'priority', 'kind', 'field_ids', 'text', 'recommendation', 'reason'}
                or not {'id', 'priority', 'kind', 'field_ids', 'text'} <= set(q)):
            raise ValueError('Invalid question item')
        priority = q['priority']; ident = q['id']
        if priority not in ('essential', 'optional') or q['kind'] not in ('question', 'decision'):
            raise ValueError('Invalid question classification')
        prefix = 'K' if priority == 'essential' else 'O'
        if not isinstance(ident, str) or not re.fullmatch(prefix + r'[1-9]\d*', ident) or ident in seen:
            raise ValueError('Duplicate or invalid question ID')
        ids = q['field_ids']
        if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or not set(ids) <= set(field_map):
            raise ValueError('Question references unknown fields')
        text = plain(q['text'])
        if text.strip() in texts:
            raise ValueError('Duplicate question text')
        texts.add(text.strip()); seen.add(ident); covered.update(ids)
        for key in ('recommendation', 'reason'):
            if key in q: plain(q[key])
        if alignment in ids:
            if q['priority'] != 'essential' or q['kind'] != 'question' or text != FULL_QUESTION[mode]:
                raise ValueError('Life Alignment must retain exact owner question')
            life_count += 1
        essential += priority == 'essential'
    if life_count != int(alignment_unknown):
        raise ValueError('Missing or repeated unresolved Life Alignment question')
    unknown = {k for k, value in fields.items() if 'UNKNOWN' in value}
    if not unknown <= covered:
        raise ValueError('Unknown fields need a question reference')
    if essential > (4 if mode == 'daily' else 5):
        plain(queue.get('overflow_reason'))
    return queue


def render(queue):
    lines = [START, '', '## Pytania i decyzje — kluczowe 20/80', '',
             'Wystarczy odpowiedź na poniższe punkty. Nie stanowi ona zgody na zapis ani wykonanie działań.', '']
    for priority in ('essential', 'optional'):
        if priority == 'optional':
            lines.extend(['## Pytania i decyzje — opcjonalne', '',
                          'Pominięte odpowiedzi pozostają UNKNOWN i same nie blokują finalizacji.', ''])
        rows = [q for q in queue['items'] if q['priority'] == priority]
        if not rows: lines.extend(['Brak dodatkowych pytań i decyzji.', ''])
        for number, q in enumerate(rows, 1):
            kind = 'Decyzja' if q['kind'] == 'decision' else 'Pytanie'
            lines.extend([f"{number}. **{q['id']} · {kind}**", '',
                          *['   ' + s if s else '' for s in q['text'].splitlines()], ''])
            for key, label in (('recommendation', 'Propozycja AI'), ('reason', 'Podstawa')):
                if q.get(key):
                    lines.extend(['   '+label+': '+q[key].replace('\n','\n   '), ''])
    if queue.get('overflow_reason'):
        lines.extend(['Dodatkowe punkty kluczowe: ' + queue['overflow_reason'], ''])
    lines.append(END)
    return '\n'.join(lines)


def annotate(fields, queue):
    """References are a render projection, never injected into stored field values."""
    result = dict(fields)
    for key in result:
        refs = [q['id'] for q in queue['items'] if key in q['field_ids']]
        if refs: result[key] += '\n\nDo uzupełnienia / decyzji: ' + ', '.join(refs) + '.'
    return result


def replace_tail(body, queue, expected_queue=None):
    matches = list(BLOCK.finditer(body))
    if len(matches) != 1:
        raise ValueError('Edited question structure requires reconciliation')
    if expected_queue is not None and matches[0].group() != render(expected_queue):
        raise ValueError('Question text changed; reread and reconcile owner edits')
    return body[:matches[0].start()] + render(queue) + body[matches[0].end():]


def strip_markers(body):
    return body.replace(START + '\n', '').replace(END + '\n', '').replace(END, '')


def known(value):
    return ('UNKNOWN' not in value and value.startswith(('Potwierdzone:', 'Zaplanowane:')))


def resolved(queue, fields, changed):
    """Only a normalized owner patch can retire a fully answered item."""
    return {**queue, 'items': [q for q in queue['items']
            if not (set(q['field_ids']) & set(changed)
                    and all(known(fields[k]) for k in q['field_ids']))]}

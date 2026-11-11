"""Deterministic chat projection. No reads, writes or external actions."""
import re
DRAFT_FIELD_MARKER = re.compile(r'^<!-- (?:spor-field:f\d{3}|/spor-field) -->\n?', re.MULTILINE)

def chat_body(saved):
    """Pure numbered chat projection; preserve every field value and stored byte."""
    body = saved['body']
    if saved.get('metadata', {}).get('form_version') == 2:
        from personal_ops_drafts import FIELD, form
        from spor_question_queue import validate, annotate, strip_markers
        queue = saved['metadata']['questions']
        fields = {m[1]: m[2] for m in FIELD.finditer(body)}
        validate(queue, saved['metadata']['mode'], form(saved['metadata']['mode'], 2), fields)
        values = annotate(fields, queue)
        body = FIELD.sub(lambda m: '<!-- spor-field:' + m[1] + ' -->\n' + values[m[1]] + '\n<!-- /spor-field -->', body)
        body = strip_markers(body)
    lines = body.splitlines(keepends=True)
    rendered = []
    index = number = 0
    # Only the literal empty template example is omitted, never real table rows.
    placeholder = (
        '| Czas | Element | DoD | DL |\n'
        '| --- | --- | --- | --- |\n'
        '| <jawny czas albo pytanie> | <stream, tylko jeden WIG> | '
        '<istniejący lub proponowany> | <istniejący lub proponowany> |'
    )
    while index < len(lines):
        line = lines[index]
        if re.match(r'^#{1,6} ', line):
            number = 0
        if (line.startswith('- ') and index + 1 < len(lines)
                and re.fullmatch(r'<!-- spor-field:f\d{3} -->\n?', lines[index + 1])):
            end = index + 2
            while end < len(lines) and lines[end].rstrip('\n') != '<!-- /spor-field -->':
                end += 1
            if end == len(lines):
                raise RuntimeError('Incomplete draft field in chat projection')
            number += 1
            label = line[2:].rstrip('\n')
            rendered.append(f'\n{number}. **{label}**\n\n')
            # Indentation keeps paragraphs, bullets and tables inside this field.
            rendered.extend('   ' + value if value.strip() else value
                            for value in lines[index + 2:end])
            rendered.append('\n')
            index = end + 1
        else:
            if ''.join(lines[index:index + 3]).rstrip('\n') in (placeholder, placeholder.replace('<jawny czas albo pytanie>', '<jawny czas albo UNKNOWN>')):
                index += 3
                continue
            rendered.append(line)
            index += 1
    return DRAFT_FIELD_MARKER.sub('', ''.join(rendered))

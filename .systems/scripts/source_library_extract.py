"""Local, page-bounded source extraction. Inputs are data, never commands."""
import csv
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

MAX_BYTES = 512 * 1024 * 1024
MAX_PAGES = 2000
PAGE_TIMEOUT = 60


class ExtractionError(ValueError):
    pass


def run_tool(argv, directory, *, timeout=PAGE_TIMEOUT):
    """Bound time and regular-file output; never invoke a shell or inherit stdin."""
    if not shutil.which(argv[0]):
        raise ExtractionError('missing extraction tool: ' + argv[0])
    output = Path(directory) / 'command-output'
    errors = Path(directory) / 'command-errors'
    def limits():
        import resource
        resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024, 32 * 1024 * 1024))
    try:
        with output.open('wb') as out, errors.open('wb') as err:
            done = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                  timeout=timeout, check=False,
                                  env=dict(os.environ, OMP_THREAD_LIMIT='1'), preexec_fn=limits)
        if done.returncode:
            raise ExtractionError('extraction tool failed: ' + argv[0])
        if output.stat().st_size > 8 * 1024 * 1024:
            raise ExtractionError('extraction output exceeds page limit')
        return output.read_text(encoding='utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        raise ExtractionError('page extraction timed out') from None


def count_pages(original, scratch, *, timeout=PAGE_TIMEOUT):
    if original.suffix != '.pdf':
        return None
    text = run_tool(['pdfinfo', str(original)], scratch, timeout=timeout)
    match = re.search(r'^Pages:\s+(\d+)\s*$', text, re.M)
    if not match or not 1 <= int(match[1]) <= MAX_PAGES:
        raise ExtractionError('unsupported PDF page count')
    return int(match[1])


def text_pages(original):
    if original.stat().st_size > MAX_BYTES:
        raise ExtractionError('source exceeds file size limit')
    text = original.read_text(encoding='utf-8-sig')
    if '\x00' in text:
        raise ExtractionError('binary text input')
    result, lines, start = [], [], 1
    for n, line in enumerate(text.splitlines(), 1):
        lines.append(line)
        if sum(len(s) + 1 for s in lines) >= 2000:
            result.append({'page': len(result) + 1, 'locator': f'lines {start}-{n}',
                           'text': '\n'.join(lines), 'method': 'text', 'confidence': None,
                           'quality': 'extracted'})
            start, lines = n + 1, []
    if lines or not result:
        result.append({'page': len(result) + 1, 'locator': f'lines {start}-{max(start, len(text.splitlines()))}',
                       'text': '\n'.join(lines), 'method': 'text', 'confidence': None,
                       'quality': 'extracted' if text.strip() else 'empty'})
    if len(result) > MAX_PAGES:
        raise ExtractionError('text exceeds chunk limit')
    return result


def pdf_page(original, number, scratch, *, timeout=PAGE_TIMEOUT):
    deadline = time.monotonic() + timeout
    def remaining():
        return max(.01, deadline - time.monotonic())
    raw = run_tool(['pdftotext', '-f', str(number), '-l', str(number), '-layout',
                    str(original), '-'], scratch, timeout=remaining()).strip('\f\n ')
    # Text layers are useful but do not prove image/chart comprehension.
    if len(re.sub(r'\W', '', raw)) >= 20 and '\ufffd' not in raw:
        return {'page': number, 'locator': f'page {number}', 'text': raw,
                'method': 'pdf-text', 'confidence': None, 'quality': 'extracted'}
    image = Path(scratch) / 'page'
    run_tool(['pdftoppm', '-f', str(number), '-l', str(number), '-singlefile',
              '-scale-to', '2000', '-png', str(original), str(image)], scratch, timeout=remaining())
    tsv = run_tool(['tesseract', str(image.with_suffix('.png')), 'stdout', '-l', 'pol+eng',
                    '--oem', '1', '--psm', '3', 'tsv'], scratch, timeout=remaining())
    words, confidences, previous = [], [], None
    for row in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
        if row.get('level') != '5' or not row.get('text', '').strip():
            continue
        line = tuple(row.get(k) for k in ('block_num', 'par_num', 'line_num'))
        words.append(('\n' if previous is not None and line != previous else ' ') + row['text'])
        previous = line
        confidences.append(float(row['conf']))
    text = ''.join(words).strip()
    confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0
    return {'page': number, 'locator': f'page {number}', 'text': text or raw,
            'method': 'ocr', 'confidence': confidence,
            'quality': 'ocr-review' if confidence >= 70 else 'low-quality' if text or raw else 'empty'}

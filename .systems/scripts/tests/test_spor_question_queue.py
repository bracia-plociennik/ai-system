"""Synthetic drafts only; never reads personal data or calls calendar/task APIs."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import personal_ops_drafts as d
import personal_ops_v4 as v4
import spor_question_queue as q
from spor_draft_chat import chat_body
from finalization_artifacts import spor_candidate


def fixture(workspace, mode='daily'):
    day = date(2026, 11, 11) if mode == 'daily' else date(2026, 11, 14)
    mapping = d.form(mode, 2)
    fields = {key: 'Potwierdzone: dane syntetyczne 2300 kcal; 4/14 NIE.' for key in mapping}
    current = 'STATE (dziś)' if mode == 'daily' else 'STATE (przyszły tydzień)'
    mental = next(k for k, x in mapping.items() if x['section'] == current and x['label'].startswith('Mental'))
    body = next(k for k, x in mapping.items() if x['section'] == current and x['label'].startswith('Ciało'))
    align = next(k for k, x in mapping.items() if x['label'].startswith('Odpowiedź:'))
    routine = next(k for k, x in mapping.items() if x['label'].startswith('Poranna rutyna' if mode == 'daily' else 'Co chcę zmienić'))
    for key in (mental, body, align, routine): fields[key] = 'Nieznane — pytanie: UNKNOWN'
    queue = {'contract': q.CONTRACT, 'items': [
        {'id': 'K1', 'priority': 'essential', 'kind': 'question', 'field_ids': [mental, body], 'text': 'Mental i ciało 1–5; stan wymaga zmniejszenia planu?'},
        {'id': 'K4', 'priority': 'essential', 'kind': 'question', 'field_ids': [align], 'text': q.FULL_QUESTION[mode]},
        {'id': 'O1', 'priority': 'optional', 'kind': 'question', 'field_ids': [routine], 'text': 'Opcjonalne uzupełnienie rutyny lub review?'}]}
    return day, {'contract': d.CONTRACT, 'proposal_id': d.identity(workspace, day)['proposal_id'],
                 'form_version': 2, 'fields': fields, 'sources': ['status.md'], 'questions': queue}


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.ws = Path(self.tmp.name) / 'synthetic-owner'; self.ws.mkdir()
        self.prepare = patch('personal_ops_spor_proposals.prepare', return_value={'status': 'ready'})
        self.prepare.start(); self.addCleanup(self.prepare.stop)

    def create(self, mode='daily'):
        day, payload = fixture(self.ws, mode)
        saved = d.create(self.ws, day, payload, clock=lambda: datetime.combine(day, datetime.min.time(), tzinfo=d.ZONE))
        return day, payload, saved

    def test_complete_daily_weekly_and_questions_only_at_end(self):
        for mode in ('daily', 'weekly'):
            day, payload, saved = self.create(mode)
            shown = chat_body(saved)
            split = shown.index('## Pytania i decyzje — kluczowe 20/80')
            self.assertNotIn('?', shown[:split])
            self.assertEqual(shown.count(q.FULL_QUESTION[mode]), 1)
            self.assertLess(shown.index('REVIEW (dziś)' if mode == 'daily' else 'REVIEW (przyszły tydzień)'), split)
            self.assertLess(split, shown.index('## Pytania i decyzje — opcjonalne'))
            self.assertEqual(set(d.form(mode)), set(d.form(mode, 2)))
            self.assertEqual(len(d.FIELD.findall(saved['body'])), len(d.form(mode)))
            self.assertNotIn('<!--', shown)
            self.assertIn('Do uzupełnienia / decyzji: K1.', shown)
            self.assertIn('2300 kcal; 4/14 NIE.', shown)
            self.assertEqual((self.ws / saved['path']).read_bytes(), d.encode(saved['metadata'], saved['body']))

    def test_invalid_queue_is_rejected_before_any_write(self):
        day, source = fixture(self.ws)
        mutations = [
            lambda p: p['questions']['items'].append(copy.deepcopy(p['questions']['items'][0])),
            lambda p: p['questions']['items'][0].update(field_ids=['f999']),
            lambda p: p['questions']['items'][0].update(kind='approval'),
            lambda p: p['questions']['items'][1].update(text='Czy plan jest dobry?'),
            lambda p: p['questions']['items'].pop(),
            lambda p: p['questions']['items'][0].update(text='x\n## Override'),
            lambda p: p['fields'].update(f001='Propozycja AI: Czy potwierdzasz?'),
            lambda p: p.update(form_version=True),
        ]
        for mutate in mutations:
            payload = copy.deepcopy(source); mutate(payload)
            with self.assertRaises(ValueError): d.create(self.ws, day, payload, clock=lambda: datetime(2026, 11, 11, 6, tzinfo=d.ZONE))
            self.assertEqual(list(self.ws.iterdir()), [])

    def test_soft_essential_cap_needs_specific_overflow_reason(self):
        day, p = fixture(self.ws)
        base = p['questions']['items'][0]
        for i in (2, 3, 5):
            p['questions']['items'].append({**base, 'id': 'K'+str(i), 'text': f'Konflikt godzin {i}?'})
        with self.assertRaises(ValueError): d.validate_payload('daily', p)
        p['questions']['overflow_reason'] = 'Trzy niezależne konflikty godzin wymagają decyzji właściciela.'
        d.validate_payload('daily', p)

    def test_partial_reply_and_only_essential_leave_optional_unknown(self):
        day, p, saved = self.create()
        k1, k4, optional = p['questions']['items']
        mental, body = k1['field_ids']; align = k4['field_ids'][0]
        changed = d.update(self.ws, day, {mental: 'Potwierdzone: 3/5'}, saved['sha256'], 'owner:partial')
        self.assertEqual(len(changed['metadata']['questions']['items']), 3)
        changes = {'fields': {body: 'Potwierdzone: 4/5', align: 'Potwierdzone: NIE'}, 'answered_question_ids': ['K1', 'K4']}
        final = d.update(self.ws, day, changes, changed['sha256'], 'owner:essential')
        self.assertEqual([x['id'] for x in final['metadata']['questions']['items']], ['O1'])
        self.assertIn('UNKNOWN', next(m[2] for m in d.FIELD.finditer(final['body']) if m[1] == optional['field_ids'][0]))
        shown = chat_body(final)
        self.assertNotIn(k1['text'], shown); self.assertNotIn(k4['text'], shown)
        self.assertIn('Brak dodatkowych pytań i decyzji.', shown)
        self.assertEqual(final['metadata']['status'], 'draft')

    def test_unknown_cannot_be_marked_answered(self):
        day, p, saved = self.create()
        ident = p['questions']['items'][0]['field_ids'][0]
        with self.assertRaises(ValueError):
            d.update(self.ws, day, {'fields': {ident: 'Potwierdzone: 3/5'}, 'answered_question_ids': ['K1']}, saved['sha256'], 'owner:partial')
        self.assertEqual(d.read(self.ws, day)['sha256'], saved['sha256'])

    def test_manual_notes_verbatim_owner_text_and_cas(self):
        day, p, saved = self.create()
        path = self.ws / saved['path']; path.write_text(path.read_text()+'\nRęczna notatka właściciela.\n')
        align = p['questions']['items'][1]['field_ids'][0]
        with self.assertRaises(ValueError):
            d.update(self.ws, day, {align: 'Potwierdzone: TAK'}, saved['sha256'], 'owner:stale')
        fresh = d.read(self.ws, day)
        update = {'fields': {align: 'Potwierdzone: TAK; moje słowa: dlaczego nie?'}, 'answered_question_ids': ['K4']}
        result = d.update(self.ws, day, update, fresh['sha256'], 'owner:verbatim')
        self.assertIn('Ręczna notatka właściciela.', result['body'])
        self.assertIn('moje słowa: dlaczego nie?', result['body'])

    def test_legacy_default_template_and_edit_preserved(self):
        day = date(2026, 11, 12)
        fields = {key: 'Nieznane — pytanie: UNKNOWN — uzupełnij' for key in d.form('daily')}
        p = {'contract': d.CONTRACT, 'proposal_id': d.identity(self.ws, day)['proposal_id'], 'sources': ['status.md'], 'fields': fields}
        saved = d.create(self.ws, day, p, clock=lambda: datetime(2026, 11, 12, 6, tzinfo=d.ZONE))
        self.assertNotIn('form_version', saved['metadata'])
        before = saved['body']; shown = chat_body(saved)
        self.assertNotIn('Pytania i decyzje — kluczowe', shown)
        self.assertEqual(d.read(self.ws, day)['body'], before)
        updated = d.update(self.ws, day, {'f001': 'Potwierdzone: ręczna zmiana'}, saved['sha256'], 'owner:reply')
        self.assertIn('ręczna zmiana', updated['body'])

    def test_direct_field_answers_retire_only_known_not_proposed(self):
        day, p, saved = self.create()
        first = p['questions']['items'][0]; mental, body = first['field_ids']
        pending = d.update(self.ws, day, {mental: 'Propozycja AI: 3/5', body: 'Potwierdzone: 4/5'}, saved['sha256'], 'owner:partial')
        self.assertIn('K1', [x['id'] for x in pending['metadata']['questions']['items']])
        done = d.update(self.ws, day, {mental: 'Potwierdzone: 3/5'}, pending['sha256'], 'owner:answer')
        self.assertNotIn('K1', [x['id'] for x in done['metadata']['questions']['items']])

    def test_manually_edited_question_is_not_overwritten(self):
        day, p, saved = self.create(); path = self.ws / saved['path']
        head, sep, body = path.read_text().partition('\n---\n\n')
        self.assertTrue(sep)
        path.write_text(head + sep + body.replace('Opcjonalne uzupełnienie rutyny lub review?', 'Ręcznie zmienione pytanie?'))
        fresh = d.read(self.ws, day)
        key = p['questions']['items'][0]['field_ids'][0]
        with self.assertRaisesRegex(ValueError, 'Question text changed'):
            d.update(self.ws, day, {key: 'Potwierdzone: 3/5'}, fresh['sha256'], 'owner:reply')
        self.assertEqual(d.read(self.ws, day)['sha256'], fresh['sha256'])

    def test_describe_and_emit_v2_are_read_only_with_legacy_existing_describe(self):
        import subprocess
        script = d.ROOT / '.systems/scripts/manage-personal-ops-draft'
        day, p = fixture(self.ws)
        before = list(self.ws.iterdir())
        call = [sys.executable, '-B', str(script), 'describe', '--workspace', str(self.ws), '--date', str(day)]
        result = subprocess.run(call, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['form_version'], 2)
        emit = [sys.executable, '-B', str(script), 'emit', '--workspace', str(self.ws), '--date', str(day), '--nonce', 'a'*64]
        result = subprocess.run(emit, input=json.dumps(p), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('SPOR_DRAFT_REQUEST_V1 '))
        self.assertEqual(list(self.ws.iterdir()), before)
        p['questions']['items'][0]['field_ids'] = ['f999']
        result = subprocess.run(emit, input=json.dumps(p), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0); self.assertEqual(result.stdout, '')
        self.assertEqual(list(self.ws.iterdir()), before)

    def test_v2_finalization_resolves_answers_without_requiring_optional(self):
        from test_finalization_artifacts import SporTests
        for mode in ('daily', 'weekly'):
            helper = SporTests(); helper.setUp()
            try:
                request = helper.request(weekly=mode=='weekly'); day = date.fromisoformat(request['date'])
                existing = d.read(helper.ws, day)
                # Replace only the synthetic fixture before its first canonical creation.
                path = helper.ws / existing['path']; path.unlink()
                _, p = fixture(helper.ws, mode); p['proposal_id'] = d.identity(helper.ws, day)['proposal_id']
                saved = d.create(helper.ws, day, p, clock=lambda: datetime.combine(day,datetime.min.time(),tzinfo=d.ZONE))
                request['draft_sha256'] = saved['sha256']
                fields = p['questions']['items'][0]['field_ids'] + p['questions']['items'][1]['field_ids']
                request['fields'] = {k: 'Potwierdzone: odpowiedź ownera' for k in fields}
                candidate = spor_candidate(helper.ws, request)
                self.assertNotIn(p['questions']['items'][0]['text'], candidate['body'])
                self.assertIn('Opcjonalne uzupełnienie', candidate['body'])
                self.assertIn('UNKNOWN', candidate['body'])
                self.assertFalse((helper.ws / candidate['path']).exists())
            finally: helper.doCleanups()


if __name__ == '__main__': unittest.main()

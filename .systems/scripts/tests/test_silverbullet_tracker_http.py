import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_silverbullet_tracker import TrackerFixture
from silverbullet_tracker_http import Application, PREFIX
from silverbullet_tracker import TrackerError


class HttpTests(TrackerFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.app=Application({'workspace':str(self.w),'origin':'https://example.test','native_url':'http://127.0.0.1:3000','allowed_user':'owner'},tracker=self.tracker)
        self.headers={'Cookie':'session=synthetic','Origin':'https://example.test','Sec-Fetch-Site':'same-origin','Content-Type':'application/json'}
        self.headers['X-Task-Tracker-CSRF']=self.tracker.csrf('owner',self.headers['Cookie'])

    def call(self, method, route, data=None, headers=None):
        with patch.object(self.app,'authenticate',return_value=('owner','session=synthetic')):
            return self.app.handle(method,PREFIX+route,headers or self.headers,json.dumps(data).encode() if data is not None else b'')

    def test_state_has_csrf_no_mutating_control(self):
        status,body,_=self.call('GET','state');self.assertEqual(status,200);self.assertIn('csrf',body)
        with self.assertRaisesRegex(TrackerError,'method-not-allowed'):self.call('DELETE','state')

    def test_origin_and_csrf_are_both_required(self):
        for headers in [{**self.headers,'Origin':'https://other.test'}, {**self.headers,'X-Task-Tracker-CSRF':''}, {**self.headers,'Sec-Fetch-Site':'cross-site'}]:
            with self.assertRaises(TrackerError) as result:self.call('POST','events',{},headers)
            self.assertEqual(result.exception.status,403)

    def test_no_auth_cookie_is_rejected_before_profile(self):
        with self.assertRaises(TrackerError) as result:self.app.authenticate({})
        self.assertEqual(result.exception.status,401)

    def test_profile_owner_and_admin_enforced(self):
        class Response:
            status=200;headers={'Content-Type':'application/json'}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):return json.dumps(self.value).encode()
        for value in [{'username':'reader','admin':True},{'username':'owner','admin':False}]:
            response=Response();response.value=value
            with patch.object(self.app.opener,'open',return_value=response), self.assertRaisesRegex(TrackerError,'owner-access'):
                self.app.authenticate(self.headers)

    def test_create_keeps_template_notes_and_injects_real_identity(self):
        text='---\ntype: task\ntitle: New\nstatus: open\ncategory: do\n---\nCustom template note\n'
        headers={**self.headers,'If-None-Match':'*','X-Sync-Mode':'true'}
        with patch.object(self.app,'authenticate',return_value=('owner','session=synthetic')):
            status,body,meta=self.app.handle('PUT','/.task-create/tasks/Client/Project/New.md',headers,text.encode())
            self.assertEqual(status,201);self.assertIn('X-Last-Modified',meta)
            path=self.vault/'tasks/Client/Project/New.md';self.assertTrue(path.read_text().endswith('Custom template note\n'));self.assertIn('created_at:',path.read_text())
            with self.assertRaises(TrackerError) as error:self.app.handle('PUT','/.task-create/tasks/Client/Project/New.md',headers,text.encode())
            self.assertEqual(error.exception.status,412)

    def test_traversal_and_generic_file_access_rejected(self):
        for path in ['/.task-create/tasks/%2e%2e/config.md','/.task-create/tasks/a/%2f..%2fconfig.md']:
            with self.assertRaises(TrackerError):self.app.create_task(path,b'---\ntype: task\n---\n',{'If-None-Match':'*','X-Sync-Mode':'true'})
        with self.assertRaises(TrackerError):self.call('GET','../private-tax')


if __name__=='__main__':unittest.main()

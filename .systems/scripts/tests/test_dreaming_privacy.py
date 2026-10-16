import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import dreaming_privacy as p
from dreaming_provider_v1 import ProtocolError

class Privacy(unittest.TestCase):
    def test_local_forms(self):
        for text in ["/home/test/a.md","/srv/private/data", "/Users/owner/test",r"C:\private\a.md",r"\\host\share\a", "file:///tmp/x","%2Fhome%2Fowner%2Fx",r"\u002fhome\u002fowner\u002fx", r"\/srv\/x\/y", "/unusual/root/file", "https://example.org/?path=%2Fhome%2Fprivate%2Fx", "https://192.168.1.1/page"]:
            with self.subTest(text=text),self.assertRaises(ProtocolError):p.clean_projection({'pending':{'title':text}})
    def test_secrets_identity(self):
        for text in ["api_key=synthetic", "hello@example.invalid", "-----BEGIN PRIVATE KEY-----"]:
            with self.assertRaises(ProtocolError):p.clean_projection({'translation':text})
    def test_safe(self):
        for text in ["Useful process notes", "notes/process.md", "See https://example.org/process/a", "Review required"]:p.clean_projection({'title':text})
    def test_safe_category(self):
        try:p.clean_text('/home/private/owner/secret')
        except ProtocolError as e:self.assertEqual(str(e),'private-path')

if __name__=='__main__':unittest.main()

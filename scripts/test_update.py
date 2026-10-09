import hashlib, importlib.util, io, json, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'packaging'))
from update import update, validate_extract
from build_package import build
class UpdateTests(unittest.TestCase):
    def test_verified_update_and_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            archive=build(Path(t)/'dist');data=archive.read_bytes();version=json.loads((ROOT/'plugin.json').read_text(encoding='utf-8'))['version']
            release={'tag_name':'v'+version,'assets':[{'name':archive.name,'browser_download_url':'zip'},{'name':'SHA256SUMS.txt','browser_download_url':'sha'}]}
            values={'zip':data,'sha':(hashlib.sha256(data).hexdigest()+'  '+archive.name).encode()}
            def fetch(url):return values.get(url,json.dumps(release).encode())
            self.assertEqual(update(Path(t)/'user',False,fetch)['latest'],version)
            self.assertFalse((Path(t)/'user').exists())
            self.assertTrue(update(Path(t)/'user',True,fetch)['applied'])
            values['zip']=data+b'tamper'
            with self.assertRaises(ValueError):update(Path(t)/'other',True,fetch)
            self.assertFalse((Path(t)/'other').exists())
    def test_unsafe_archive(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('robot-test-knowledge/../../escape','x')
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):validate_extract(b.getvalue(),t)
if __name__=='__main__':unittest.main()

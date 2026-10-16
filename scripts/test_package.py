import importlib.util, json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from build_package import build, package_bytes
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("plugin_installer",ROOT/"packaging/install.py")
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class PackageTests(unittest.TestCase):
    def test_text_payload_is_identical_for_lf_and_crlf_checkouts(self):
        with tempfile.TemporaryDirectory(prefix="robot-line-endings-") as temp:
            root=Path(temp);text=root/"sample.md";launcher=root/"Install.cmd";binary=root/"sample.xlsx"
            text.write_bytes(b"alpha\nbeta\n")
            plain=package_bytes(text)
            text.write_bytes(b"alpha\r\nbeta\r\n")
            self.assertEqual(package_bytes(text),plain)
            launcher.write_bytes(b"@echo off\npause\n")
            windows=package_bytes(launcher)
            launcher.write_bytes(b"@echo off\r\npause\r\n")
            self.assertEqual(package_bytes(launcher),windows)
            self.assertIn(b"\r\n",windows)
            binary.write_bytes(b"PK\x03\x04\r\n\x00")
            self.assertEqual(package_bytes(binary),binary.read_bytes())

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="robot-package-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        archive=build(self.root/"dist")
        with zipfile.ZipFile(archive) as z:
            self.names=z.namelist();self.assertTrue(all(item.create_system==3 for item in z.infolist()))
            z.extractall(self.root/"unpacked")
        self.package=self.root/"unpacked/robot-test-knowledge"
        self.home=self.root/"user"
    def test_windows_long_destination_is_refused_before_any_writes(self):
        from unittest.mock import patch
        home=self.root/('u'*200)
        for file_limit,directory_limit in ((259,None),(None,247)):
            with patch.object(installer,'WINDOWS_FILE_LIMIT',file_limit),patch.object(installer,'WINDOWS_DIRECTORY_LIMIT',directory_limit):
                with self.assertRaisesRegex(ValueError,'shorter --user-root'):
                    installer.install(self.package,home,True)
            self.assertFalse(home.exists())

    def test_archive_and_reproducibility(self):
        first=build(self.root/"one").read_bytes();second=build(self.root/"two").read_bytes()
        self.assertEqual(first,second)
        self.assertFalse(any("/projects/" in n or "/.git/" in n for n in self.names))
        expected={"robot-test-knowledge/skills/testcase-iteration/assets/templates/"+name for name in ("通用软件测试用例模板_v1.0.xlsx","固件测试用例模板_v1.0.xlsx","ROS测试用例模板_v1.0.xlsx")}
        self.assertEqual({n for n in self.names if n.endswith(".xlsx")},expected)
        self.assertEqual(json.loads((self.package/"plugin.json").read_text(encoding="utf-8"))["version"],json.loads((ROOT/"plugin.json").read_text(encoding="utf-8"))["version"])
    def test_packaged_markdown_references_are_self_contained(self):
        import re, urllib.parse
        for p in self.package.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if '://' in link or link.startswith('#'):continue
                value=urllib.parse.unquote(link.split('#')[0].strip('<>'))
                if not value:continue
                target=(p.parent/value).resolve()
                self.assertTrue(target.is_relative_to(self.package.resolve()),str(p)+': '+link)
                self.assertTrue(target.exists(),str(p)+': '+link)

    def test_install_preview_then_apply_and_repeat(self):
        installer.install(self.package,self.home)
        self.assertFalse(self.home.exists())
        result=installer.install(self.package,self.home,True)
        data=json.loads(Path(result["marketplace"]).read_text(encoding="utf-8"))
        self.assertEqual(len(data["plugins"]),1)
        source=self.home/data["plugins"][0]["source"]["path"][2:]
        self.assertTrue((source/"skills/testcase-iteration/SKILL.md").exists())
        installer.install(self.package,self.home,True)
        self.assertEqual(len(json.loads(Path(result["marketplace"]).read_text(encoding="utf-8"))["plugins"]),1)
    def test_preserve_existing_marketplace(self):
        catalog=self.home/".agents/plugins/marketplace.json";catalog.parent.mkdir(parents=True)
        other={"name":"existing","source":{"source":"local","path":"./existing"}}
        catalog.write_text(json.dumps({"name":"my-source","plugins":[other],"custom":"keep"}),encoding="utf-8")
        installer.install(self.package,self.home,True)
        data=json.loads(catalog.read_text(encoding="utf-8"))
        self.assertEqual(data["name"],"my-source");self.assertEqual(data["custom"],"keep");self.assertEqual(data["plugins"][0],other)
        self.assertTrue(catalog.with_name("marketplace.before-robot-test-knowledge.json").exists())
    def test_tampered_package_refused_without_writes(self):
        (self.package/"skills/testcase-iteration/SKILL.md").write_text("changed",encoding="utf-8")
        with self.assertRaises(ValueError):installer.install(self.package,self.home,True)
        self.assertFalse(self.home.exists())
    def test_installed_edits_refused(self):
        result=installer.install(self.package,self.home,True)
        f=Path(result["plugin_path"])/"skills/pytest-generation/SKILL.md";f.write_text("my edit",encoding="utf-8")
        with self.assertRaises(FileExistsError):installer.install(self.package,self.home,True)
        self.assertEqual(f.read_text(encoding="utf-8"),"my edit")
    def test_external_same_name_refused(self):
        catalog=self.home/".agents/plugins/marketplace.json";catalog.parent.mkdir(parents=True)
        text=json.dumps({"name":"mine","plugins":[{"name":"robot-test-knowledge","source":{"source":"local","path":"./other"}}]})
        catalog.write_text(text,encoding="utf-8")
        with self.assertRaises(FileExistsError):installer.install(self.package,self.home,True)
        self.assertEqual(catalog.read_text(encoding="utf-8"),text)
        self.assertFalse((self.home/".codex").exists())
    def test_real_cli(self):
        subprocess.run([sys.executable,"-X","utf8",str(self.package/"install.py"),"--user-root",str(self.home),"--apply"],check=True)
        self.assertTrue((self.home/".agents/plugins/marketplace.json").exists())
    def test_interrupted_copy_can_retry_without_partial_version(self):
        from unittest.mock import patch
        original=Path.open;writes=[]
        def fail_second(p,*args,**kwargs):
            if args and args[0]=='xb' and p.is_relative_to(self.home):
                writes.append(p)
                if len(writes)==2:raise OSError('simulated interrupted copy')
            return original(p,*args,**kwargs)
        with patch.object(Path,'open',fail_second):
            with self.assertRaises(OSError):installer.install(self.package,self.home,True)
        self.assertFalse((self.home/'.agents/plugins/marketplace.json').exists())
        self.assertFalse(any(p.is_file() for p in self.home.rglob('*')))
        self.assertTrue(installer.install(self.package,self.home,True)['applied'])
    def test_catalog_failure_preserves_previous_source_and_can_retry(self):
        from unittest.mock import patch
        catalog=self.home/'.agents/plugins/marketplace.json';catalog.parent.mkdir(parents=True)
        before=json.dumps({'name':'mine','plugins':[{'name':'other','source':{'source':'local','path':'./other'}}]})
        catalog.write_text(before,encoding='utf-8')
        with patch.object(installer.os,'replace',side_effect=OSError('simulated catalog failure')):
            with self.assertRaises(OSError):installer.install(self.package,self.home,True)
        self.assertEqual(catalog.read_text(encoding='utf-8'),before)
        self.assertTrue(installer.install(self.package,self.home,True)['applied'])
    def test_preexisting_partial_or_modified_directory_is_preserved(self):
        preview=installer.install(self.package,self.home);dest=Path(preview['plugin_path']);dest.mkdir(parents=True)
        marker=dest/'user-file.txt';marker.write_text('keep',encoding='utf-8')
        with self.assertRaises(FileExistsError):installer.install(self.package,self.home,True)
        self.assertEqual(marker.read_text(encoding='utf-8'),'keep')
    def test_build_identity_is_installed_and_candidate_is_distinct(self):
        result=installer.install(self.package,self.home,True)
        identity=json.loads((Path(result['plugin_path'])/'build-info.json').read_text(encoding='utf-8'))
        self.assertEqual(identity['channel'],'candidate');self.assertEqual(len(identity['payload_sha256']),64)
        archive=build(self.root/'candidate');self.assertIn('-candidate-',archive.name)
        released=build(self.root/'release',channel='release');self.assertNotIn('-candidate-',released.name)
    def test_package_does_not_replace_existing_different_asset(self):
        archive=build(self.root/'protected');archive.write_bytes(b'keep official asset')
        with self.assertRaises(FileExistsError):build(self.root/'protected')
        self.assertEqual(archive.read_bytes(),b'keep official asset')

if __name__=="__main__":unittest.main()

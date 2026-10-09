import importlib.util, json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from build_package import build
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("plugin_installer",ROOT/"packaging/install.py")
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="robot-package-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        archive=build(self.root/"dist")
        with zipfile.ZipFile(archive) as z:
            self.names=z.namelist();z.extractall(self.root/"unpacked")
        self.package=self.root/"unpacked/robot-test-knowledge"
        self.home=self.root/"user"
    def test_archive_and_reproducibility(self):
        first=build(self.root/"one").read_bytes();second=build(self.root/"two").read_bytes()
        self.assertEqual(first,second)
        self.assertFalse(any("/projects/" in n or n.endswith(".xlsx") or "/.git/" in n for n in self.names))
        self.assertEqual(json.loads((self.package/"plugin.json").read_text(encoding="utf-8"))["version"],"0.2.0")
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
if __name__=="__main__":unittest.main()

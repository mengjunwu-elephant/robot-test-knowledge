import importlib.util, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from validate_offline import validate
ROOT=Path(__file__).resolve().parents[1]

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'repo'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
        # Mirrors are expected to match before each mutation.
        shutil.copytree(self.root/'skills',self.root/'.agents/skills',dirs_exist_ok=True)
    def test_extra_mirror_skill_is_rejected(self):
        p=self.root/'.agents/skills/retired-skill/SKILL.md';p.parent.mkdir();p.write_text('retired',encoding='utf-8')
        self.assertTrue(any('extra mirror file' in e for e in validate(self.root)['errors']))
    def test_deleted_source_with_stale_mirror_is_rejected(self):
        p=self.root/'skills/pytest-generation/references/sdk-patterns.md';p.unlink()
        self.assertTrue(any('extra mirror file' in e for e in validate(self.root)['errors']))
    def test_missing_skill_reports_failure_instead_of_crashing(self):
        (self.root/'skills/pytest-generation/SKILL.md').unlink()
        self.assertFalse(validate(self.root)['passed'])
    def test_launcher_import_has_no_runtime_side_effects(self):
        spec=importlib.util.spec_from_file_location('isolated_launcher',ROOT/'scripts/test_launcher_windows.py')
        module=importlib.util.module_from_spec(spec)
        with patch('subprocess.run',side_effect=AssertionError('import ran a command')),patch.object(Path,'write_text',side_effect=AssertionError('import wrote a file')):
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.verify_launcher))

if __name__=='__main__':unittest.main()

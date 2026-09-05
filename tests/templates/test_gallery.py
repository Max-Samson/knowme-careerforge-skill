"""Gallery and actual resumes must share their sole maintained layout."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('gallery', ROOT / 'scripts/build/build-gallery.py')
gallery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gallery)


class TestGallery(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.tmp = Path(scratch.name)

    def test_all_previews_equal_direct_instantiation(self):
        out = self.tmp / 'gallery'
        gallery.build_gallery(out)
        binder = gallery.load_instantiator()
        templates = [d for d in (ROOT / 'src/templates').iterdir() if d.is_dir() and d.name != 'common']
        self.assertEqual(len(list(out.glob('*.html'))), len(templates) + 1)
        for template in templates:
            with self.subTest(template=template.name):
                direct = binder.instantiate_workspace(template.name, template / 'sample-profile.json',
                                                       output_path=self.tmp / 'direct.html', quiet=True)
                self.assertEqual((out / f'{template.name}.html').read_bytes(), direct.read_bytes())

    def copy_project(self):
        fake = self.tmp / 'project'
        shutil.copytree(ROOT / 'src', fake / 'src')
        shutil.copytree(ROOT / 'scripts', fake / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        (fake / 'package.json').write_text('{}')
        return fake

    def test_canvas_change_updates_both_paths(self):
        fake = self.copy_project()
        canvas = fake / 'src/templates/minimal/canvas.html'
        canvas.write_text(canvas.read_text().replace('<main>', '<main data-layout="single-source-proof">'))
        with patch.object(gallery, 'get_project_root', return_value=fake):
            out = self.tmp / 'gallery'
            gallery.build_gallery(out)
            binder = gallery.load_instantiator()
            direct = binder.instantiate_workspace('minimal', fake / 'src/templates/minimal/sample-profile.json',
                                                   output_path=self.tmp / 'direct.html', quiet=True)
            self.assertIn('single-source-proof', direct.read_text())
            self.assertEqual(direct.read_bytes(), (out / 'minimal.html').read_bytes())

    def test_bad_sample_preserves_complete_previous_gallery_and_fails_cli(self):
        fake = self.copy_project()
        out = self.tmp / 'gallery'
        with patch.object(gallery, 'get_project_root', return_value=fake):
            gallery.build_gallery(out)
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            sample = fake / 'src/templates/startup-generalist/sample-profile.json'
            for contents in ('{broken', '{"inventedField": true}', None):
                with self.subTest(contents=contents):
                    if contents is None:
                        sample.unlink()
                    else:
                        sample.write_text(contents)
                    result = subprocess.run([sys.executable, str(fake / 'scripts/build/build-gallery.py'),
                                             '--output', str(out)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('"status": "FAIL"', result.stderr)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})


if __name__ == '__main__':
    unittest.main()

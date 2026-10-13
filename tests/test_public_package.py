import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import jupyter_lecture_studio as public
from jupyter_lecture_studio.compat import LuxurySlideDeck
import lecture_studio
from lecture_studio.cli import create_starter, main


class PublicPackageTests(unittest.TestCase):
    def test_existing_imports_retain_class_identity(self):
        for name in lecture_studio.__all__:
            self.assertIs(getattr(public, name), getattr(lecture_studio, name))
        self.assertEqual(public.__version__, lecture_studio.__version__)
        from lecture_studio.compat import LuxurySlideDeck as old
        self.assertIs(LuxurySlideDeck, old)

    def test_bundled_documentation_and_cli_path(self):
        index = public.documentation_path()
        self.assertTrue(index.is_file())
        for name in ['USAGE_AR.html', 'reference.html', 'searchindex.js', '_static/studio-docs.css']:
            self.assertTrue((index.parent / name).is_file(), name)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            main(['docs'])
        self.assertEqual(Path(output.getvalue().strip()), index)

    def test_starter_uses_public_namespace(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = create_starter(Path(temp) / 'lesson', 'AI')
            cells = json.loads((directory / 'lecture.ipynb').read_text())['cells']
            self.assertIn('from jupyter_lecture_studio import LectureDeck', cells[1]['source'])

if __name__ == '__main__':
    unittest.main()

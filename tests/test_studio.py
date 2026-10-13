import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lecture_studio import Brand, Diagram, LectureDeck, Node, RichText, Theme, diagram_names, preset_diagram
from lecture_studio.cli import create_starter, main, starter
from lecture_studio.compat import LuxurySlideDeck
from lecture_studio.deck import asset


class StudioTests(unittest.TestCase):
    def test_plain_text_escaping_and_code_never_executes(self):
        deck = LectureDeck(course='<script>bad()</script>')
        page = deck.slide('<img src=x>', '<b>plain</b>', cards=[{'title': '<tag>', 'code': 'raise RuntimeError("<danger>")'}], show=False)
        self.assertNotIn('<script>', page)
        self.assertNotIn('<img', page)
        self.assertIn('&lt;b&gt;plain&lt;/b&gt;', page)
        self.assertIn('&lt;danger&gt;', page)

    def test_rich_text_is_explicit(self):
        page = LectureDeck().note('شرح', RichText('<strong>فكرة</strong>'), show=False)
        self.assertIn('<strong>فكرة</strong>', page)

    def test_empty_rich_reason_has_no_panel(self):
        self.assertFalse(RichText('  '))
        deck = LuxurySlideDeck()
        with patch('IPython.display.display'):
            deck.show({'title': 'شرح', 'steps_data': [{'title': 'فكرة', 'explanation': 'شرح'}]})
        self.assertNotIn('الفكرة:', deck._components[0])

    def test_fonts_are_embedded_and_original_palette_is_selected(self):
        page = LectureDeck().cover('غلاف', hero_code='>>> print(1)', footer_label='PYTHON / FOUNDATIONS', show=False)
        self.assertEqual(page.count('data:font/woff2;base64,'), 9)
        self.assertIn('data-palette="original"', page)
        self.assertIn('<em>&gt;&gt;&gt;</em>', page)
        self.assertIn('PYTHON / FOUNDATIONS', page)

    def test_multi_language_code_and_unknown_fallback(self):
        deck = LectureDeck(language='sql')
        page = deck.slide('SQL', cards=[{'title': 'Query', 'code': 'SELECT name FROM students;'}], show=False)
        self.assertIn('SQL</span>', page)
        page = deck.slide('Unknown', cards=[{'title': 'x', 'language': 'not-a-real-language', 'code': '<b>&'}], show=False)
        self.assertIn('&lt;b&gt;&amp;', page)

    def test_diagram_direction_selection_and_hidden_answer(self):
        page = LectureDeck().slide('بحث', diagram={'title': 'مسار', 'direction': 'rtl', 'nodes': [{'value': 'أ'}, {'value': 'ب', 'selected': True}]}, activity={'question': 'لماذا؟', 'answer': 'السبب'}, show=False)
        self.assertIn('ls-node ls-selected', page)
        self.assertIn('aria-hidden="true">←', page)
        self.assertIn('<details data-answer><summary>اكشف', page)
        self.assertIn('<details class="ls-stage" open>', page)

    def test_custom_settings_are_validated(self):
        for options in ({'accent': 'red'}, {'background': '#12'}, {'motion': 'yes'}, {'max_width': -1}, {'preset': 'missing'}, {'direction': 'up'}):
            with self.subTest(options=options), self.assertRaises((ValueError, TypeError)):
                Theme(**options)
        with self.assertRaises(ValueError):
            Diagram('x', [])
        with self.assertRaises(ValueError):
            Diagram('x', [Node('1')], kind='x" onclick="bad')

    def test_themes_are_isolated_and_offline_by_default(self):
        first, second = LectureDeck(theme='gold'), LectureDeck(theme='ocean', motion=False)
        a, b = first.slide('A', show=False), second.slide('B', show=False)
        # Themes are variables on each wrapper, so decks coexist on one page.
        self.assertIn('data-theme="gold" data-palette="original"', a)
        self.assertIn('data-theme="ocean" data-palette="custom"', b)
        self.assertIn('--ls-accent:#9fceff', b)
        self.assertIn('data-motion="false"', b)
        self.assertNotIn('@import', a)
        self.assertNotIn('.jp-Notebook', a)
        self.assertIn('prefers-reduced-motion', a)

    def test_stylesheet_is_scoped_and_has_no_remote_fonts(self):
        css = asset('studio.css')
        self.assertNotIn('fonts.googleapis', css)
        self.assertNotIn('family=', css)
        for rule in css.split('}'):
            if '{' not in rule:
                continue
            selector = rule.split('{')[-2].rsplit('*/', 1)[-1].strip()
            if selector.startswith(('from', 'to', '0%', '50%')):
                continue  # keyframe steps
            for part in selector.split(','):
                self.assertTrue(part.strip().startswith('.lecture-studio'), part)
        self.assertNotIn('!important', css.split('/* 7. Motion')[0].split('*/', 1)[1])
        self.assertIn('box-sizing: border-box', css)

    def test_notebook_canvas_is_opt_in(self):
        page = LectureDeck(notebook_style=True).slide('A', show=False)
        self.assertIn('.jp-Notebook:has(.lecture-studio[data-notebook-style="true"])', page)
        self.assertNotIn('content:\'PYTHON', page)

    def test_numbering_no_magic_titles_and_clear(self):
        deck = LectureDeck()
        first = deck.slide('عنوان خاص', cards=[{'title': str(i)} for i in range(8)], show=False)
        self.assertIn('عنوان خاص</h2>', first)
        self.assertIn('data-scene="01"', first)
        with self.assertRaises(TypeError):
            deck.slide('خطأ', cards=[{'title': 42}], show=False)
        self.assertIn('data-scene="02"', deck.slide('ثان', show=False))
        deck.clear()
        self.assertEqual(len(deck._components), 0)
        self.assertIn('data-scene="01"', deck.slide('جديد', show=False))

    def test_cover_and_table(self):
        deck = LectureDeck()
        page = deck.cover('غلاف', sections=[{'title': 'محور'}], show=False)
        self.assertIn('ls-cover ls-no-hero', page)
        self.assertNotIn('PYTHON LAB', page)
        page = deck.table('مقارنة', ['A', 'B'], [[1, '<x>']], show=False)
        self.assertIn('&lt;x&gt;', page)
        with self.assertRaises(ValueError):
            deck.table('خطأ', ['A'], [[1, 2]], show=False)

    def test_all_python_presets(self):
        self.assertEqual(len(diagram_names()), 11)
        for name in diagram_names():
            self.assertIsInstance(preset_diagram(name), Diagram)
            LectureDeck().slide(name, diagram=name, show=False)
        with self.assertRaises(ValueError):
            preset_diagram('missing')

    def test_json_loader_export_and_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'lecture'
            create_starter(source, 'مادة تجريبية')
            before = (source / 'lecture.json').read_bytes()
            with self.assertRaises(FileExistsError):
                create_starter(source, 'غيرها')
            self.assertEqual((source / 'lecture.json').read_bytes(), before)
            notebook = json.loads((source / 'lecture.ipynb').read_text())
            self.assertEqual(notebook['nbformat'], 4)
            deck = LectureDeck.from_file(source / 'lecture.json', show=False)
            output = deck.export(source / 'nested' / 'lecture.html')
            result = output.read_text()
            self.assertIn('<!doctype html>', result)
            self.assertIn('مادة تجريبية', result)
            self.assertNotIn('<script', result)
            self.assertNotIn('fonts.googleapis.com', result)
            self.assertEqual(len(deck), len(starter('x')['components']))
            with patch('builtins.print'):
                main(['export', str(source / 'lecture.json'), str(source / 'cli.html')])
            self.assertTrue((source / 'cli.html').exists())
            bad = source / 'bad.json'
            bad.write_text('{"unknown": true}')
            with self.assertRaises(ValueError):
                LectureDeck.from_file(bad, show=False)

    def test_show_does_not_return_duplicate_html(self):
        with patch('IPython.display.display') as display:
            deck = LectureDeck()
            self.assertIsNone(deck.slide('A'))
            self.assertIsNone(deck.render([{'title': 'B'}, {'title': 'C'}]))
            self.assertEqual(display.call_count, 3)

    def test_legacy_bridge(self):
        with patch('IPython.display.display'):
            deck = LuxurySlideDeck(brand=Brand(course='مادة أخرى'))
            self.assertIsNone(deck.show({'title': 'قديم', 'description': '<p>شرح</p>', 'steps_data': [{'title': 'تطبيق', 'explanation': 'start:stop:step', 'code_snippet': 'print(1)'}], 'visual': 'index'}))
        body = deck._components[0]
        self.assertIn('<code>start:stop:step</code>', body)
        self.assertIn('مادة أخرى', body)
        activity = LectureDeck().slide('توقع', activity={'question': 'ما الناتج؟', 'answer': '1', 'code': 'print(1)'}, show=False)
        activity = activity[activity.index('<aside'): ]
        self.assertNotIn('code-bar', activity)


if __name__ == '__main__':
    unittest.main()

"""Behaviour added in 1.0: locales, themes, markup, rerun safety, new components,
student exports, presentation mode, JSON round trips and plugins."""
from dataclasses import dataclass
import json
from pathlib import Path
import re
import tempfile
from typing import ClassVar
import unittest
from unittest.mock import patch

from lecture_studio import (
    Component,
    LectureDeck,
    RichText,
    Theme,
    TraceStep,
    component_names,
    get_locale,
    notebook,
    register_component,
    register_locale,
    register_theme,
)
from lecture_studio.highlight import highlight, split_lines
from lecture_studio.markup import inline, rich

ARABIC = re.compile(r'[؀-ۿ]')


def body(page):
    """The markup after the stylesheet, i.e. only what the components produced."""
    return page.split('</style>', 1)[-1]


def full_deck(deck):
    deck.cover('Title', 'Lead', tags=['a'], hero_code='>>> 1', show=False)
    deck.slide('Slide', 'Text', cards=[{'title': 'c', 'explanation': 'e', 'reason': 'r', 'code': 'x = 1'}],
               diagram={'title': 'd', 'nodes': [{'value': 'a'}, {'value': 'b'}]},
               activity={'question': 'q', 'answer': 'secret-activity'}, notes='speaker-only', show=False)
    deck.callout('Remember this', style='tip', show=False)
    deck.compare('Loop', 'for i in range(len(xs)): print(xs[i])', 'for x in xs: print(x)', show=False)
    deck.code('print(1 + 1)', title='Run', output='2', highlight=[1], line_numbers=True, show=False)
    deck.quiz('Pick', ['one', 'two', 'three'], 1, explanation='secret-quiz', show=False)
    deck.trace('x = 1\nx = x + 1\nprint(x)', [{'line': 1, 'variables': {'x': 1}}, {'line': 2, 'variables': {'x': 2}},
                                             {'line': 3, 'output': '2'}], title='Trace', show=False)
    deck.exercise('Practice', 'Write a loop', hints=['Use range'], solution='secret_solution = 1', show=False)
    deck.agenda(['Goal one', 'Goal two'], show=False)
    deck.recap(['Done'], show=False)
    deck.divider('Part two', 'More', show=False)
    deck.note('Note', 'Body', show=False)
    deck.table('T', ['a'], [[1]], show=False)
    return deck


class LocaleTests(unittest.TestCase):
    def test_english_deck_has_no_arabic_interface_text(self):
        deck = full_deck(LectureDeck(course='Data Science', locale='en'))
        page = body(deck.html())
        self.assertIsNone(ARABIC.search(page), ARABIC.search(page) and page[ARABIC.search(page).start() - 80:][:160])
        self.assertIn('dir="ltr" lang="en"', page)
        self.assertIn('Key idea:', page)

    def test_direction_and_locale_follow_each_other(self):
        self.assertEqual(LectureDeck(direction='ltr').locale.code, 'en')
        self.assertEqual(LectureDeck(locale='en').direction, 'ltr')
        self.assertEqual(LectureDeck().direction, 'rtl')
        self.assertEqual(LectureDeck(locale='en', direction='rtl').direction, 'rtl')

    def test_arabic_defaults_are_unchanged(self):
        page = LectureDeck().slide('س', cards=[{'title': 'x', 'reason': 'لأن'}], activity={'question': 'q', 'answer': 'a'}, show=False)
        for label in ('الفكرة:', 'توقّع قبل التنفيذ', 'اكشف الإجابة وفسّرها', 'مختبر التعلم', 'افهم ← توقّع ← جرّب ← فسّر'):
            self.assertIn(label, page)

    def test_custom_locale_and_label_overrides(self):
        register_locale('fr', {'reveal': 'Voir la réponse'})
        page = LectureDeck(locale='fr').slide('Q', activity={'question': 'q', 'answer': 'a'}, show=False)
        self.assertIn('Voir la réponse', page)
        self.assertIn('Predict before running', page)
        custom = get_locale('en').with_labels(reveal='Show me')
        self.assertIn('Show me', LectureDeck(locale=custom).slide('Q', activity={'question': 'q', 'answer': 'a'}, show=False))
        with self.assertRaises(KeyError):
            register_locale('xx', {'not-a-label': 'x'})
        with self.assertRaises(ValueError):
            LectureDeck(locale='zz')


class ThemeTests(unittest.TestCase):
    def test_paper_palette_and_registered_themes(self):
        page = LectureDeck(theme='paper').slide('A', show=False)
        self.assertIn('data-palette="paper"', page)
        register_theme('campus', accent='#2266aa', background='#101820', tokens={'card-bg': '#14202c'})
        page = LectureDeck(theme='campus').slide('A', show=False)
        self.assertIn('--ls-accent:#2266aa', page)
        self.assertIn('--ls-card-bg:#14202c', page)

    def test_token_values_cannot_escape_the_style_attribute(self):
        for bad in ({'card-bg': 'red;}</style><script>'}, {'Bad Name': 'red'}, {'title': ' '}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Theme(tokens=bad)
        page = LectureDeck(tokens={'title': 'rgb(1, 2, 3)', 'font': '"Cairo", serif'}).slide('A', show=False)
        self.assertIn('--ls-title:rgb(1, 2, 3)', page)
        self.assertIn('--ls-font:&quot;Cairo&quot;, serif', page)

    def test_theme_from_mapping(self):
        deck = LectureDeck(theme={'preset': 'emerald', 'motion': False})
        self.assertEqual(deck.theme.preset, 'emerald')
        self.assertFalse(deck.theme.motion)


class MarkupTests(unittest.TestCase):
    def test_inline_code_and_bold_are_applied_after_escaping(self):
        self.assertEqual(inline('Use `print(<b>)` and **care**'), 'Use <code>print(&lt;b&gt;)</code> and <strong>care</strong>')
        self.assertEqual(inline('a**2 + b**2'), 'a**2 + b**2')
        self.assertEqual(inline('**kwargs and **extra'), '**kwargs and **extra')
        self.assertIn('<strong>الاسم</strong> و<strong>الكائن</strong>', inline('بين **الاسم** و**الكائن**'))
        self.assertEqual(inline('كتاب**x**'), 'كتاب**x**')
        self.assertEqual(inline('`x`', markup='text'), '`x`')

    def test_symbol_terms_are_isolated_in_rtl_only(self):
        self.assertIn('<bdi dir="ltr">C++</bdi>', inline('لغة C++ سريعة'))
        self.assertIn('<bdi dir="ltr">C#</bdi>', inline('و C# أيضاً'))
        self.assertNotIn('bdi', inline('C++ is fast', direction='ltr'))
        self.assertNotIn('bdi', inline('`C++`'))

    def test_rich_text_is_verbatim_and_lines_break(self):
        self.assertEqual(rich(RichText('<em>x</em>')), '<em>x</em>')
        self.assertEqual(rich('a\nb'), 'a<br>b')
        page = LectureDeck().render({'type': 'note', 'title': 't', 'body': {'html': '<b>json</b>'}}, show=False)
        self.assertIn('<b>json</b>', page)


class HighlightTests(unittest.TestCase):
    def test_python_uses_pygments_compatible_classes(self):
        result = highlight('for x in range(3):  # loop\n    print("a", 1)', 'python')
        for cls in ('k', 'nb', 'c', 's', 'm'):
            self.assertIn(f'<span class="{cls}">', result)

    def test_split_lines_keeps_multiline_tokens_balanced(self):
        result = split_lines(highlight('s = """a\nb"""\nprint(s)', 'python'), marked=[2], numbers=True)
        self.assertEqual(result.count('data-line='), 3)
        self.assertEqual(result.count('<span'), result.count('</span>'))
        self.assertIn('ls-line ls-marked" data-line="2"', result)
        self.assertIn('ls-numbered', result)


class RerunTests(unittest.TestCase):
    def setUp(self):
        notebook.reset_fonts()

    def run_cell(self, deck, cell, count, titles):
        with patch('lecture_studio.notebook.current_cell', return_value=(cell, count)), \
             patch('lecture_studio.notebook.display_html') as display:
            for title in titles:
                deck.slide(title)
        return display

    def test_rerunning_a_cell_replaces_its_components_in_place(self):
        deck = LectureDeck()
        self.run_cell(deck, 'a', 1, ['A1'])
        self.run_cell(deck, 'b', 2, ['B1', 'B2'])
        self.run_cell(deck, 'c', 3, ['C1'])
        self.run_cell(deck, 'b', 4, ['B1 edited'])
        self.assertEqual([c.title for c in deck], ['A1', 'B1 edited', 'C1'])
        self.assertIn('data-scene="03"', deck._components[2])

    def test_explicit_ids_replace_wherever_they_were_created(self):
        deck = LectureDeck()
        deck.slide('one', id='intro', show=False)
        deck.slide('two', show=False)
        deck.slide('one again', id='intro', show=False)
        self.assertEqual([c.title for c in deck], ['one again', 'two'])

    def test_fonts_are_sent_once_per_notebook(self):
        deck = LectureDeck()
        first = self.run_cell(deck, 'a', 1, ['A']).call_args.args[0]
        second = self.run_cell(deck, 'b', 2, ['B']).call_args.args[0]
        rerun = self.run_cell(deck, 'a', 3, ['A']).call_args.args[0]
        self.assertIn('data:font/woff2', first)
        self.assertNotIn('data:font/woff2', second)
        self.assertIn('data:font/woff2', rerun)
        self.assertLess(len(second), len(first) // 3)

    def test_html_is_deterministic(self):
        first, second = (full_deck(LectureDeck(course='X')).html() for _ in range(2))
        self.assertEqual(first, second)


class ComponentTests(unittest.TestCase):
    def test_all_builtin_components_are_registered(self):
        for name in ('cover', 'slide', 'note', 'table', 'callout', 'compare', 'code', 'quiz', 'trace', 'exercise',
                     'agenda', 'figure', 'divider'):
            self.assertIn(name, component_names())

    def test_quiz_trace_and_exercise_markup(self):
        page = full_deck(LectureDeck(locale='en')).html()
        self.assertIn('data-correct', page)
        self.assertEqual(page.count('type="radio"'), 3 + 3)
        self.assertIn('#ls-', page)  # trace step rules are scoped to the component id
        self.assertIn('ls-line ls-marked', page)
        self.assertIn('Output', page)
        self.assertEqual(len(re.findall(r'id="(ls-[0-9a-f]{10})"', page)), 1)

    def test_validation(self):
        deck = LectureDeck()
        for call in (lambda: deck.quiz('q', ['only'], 0), lambda: deck.quiz('q', ['a', 'b'], 2),
                     lambda: deck.quiz('q', ['a', 'b'], 'c'), lambda: deck.trace('x = 1', [{'line': 5}]),
                     lambda: deck.code(''), lambda: deck.callout('x', style='loud'), lambda: deck.agenda([]),
                     lambda: deck.code('x', highlight=[0]), lambda: deck.compare('t', 'a', 'b', mode='x')):
            with self.assertRaises((ValueError, TypeError)):
                call()
        self.assertEqual(len(deck), 0)
        self.assertEqual(TraceStep(1, {'xs': [1, 2]}).variables, {'xs': '[1, 2]'})

    def test_figures_embed_local_images_and_reject_scripts(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'dot.svg'
            image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4"/>')
            deck = LectureDeck()
            page = deck.figure(str(image), caption='A dot', show=False)
            self.assertIn('src="data:image/svg+xml;base64,', page)
            self.assertIn('https://example.org/a.png', deck.figure('https://example.org/a.png', show=False))
            for bad in ('javascript:alert(1)', str(Path(temp) / 'missing.png'), str(Path(temp) / 'file.txt')):
                with self.subTest(bad=bad), self.assertRaises((ValueError, FileNotFoundError)):
                    deck.figure(bad, show=False)
            self.assertEqual(len(deck), 2)

    def test_plugin_components(self):
        @dataclass(frozen=True)
        class Banner(Component):
            kind: ClassVar[str] = 'test-banner'
            text: str

        register_component(Banner, lambda c, ctx: f'<section class="ls-note">{ctx.line(c.text)}</section>')
        with self.assertRaises(ValueError):
            register_component(Banner, lambda c, ctx: '')
        deck = LectureDeck()
        self.assertIn('Hello <code>world</code>', deck.render({'type': 'test-banner', 'text': 'Hello `world`'}, show=False))
        self.assertIn('Hi', deck.add(Banner('Hi'), show=False))


class ExportTests(unittest.TestCase):
    def test_student_copy_removes_every_answer(self):
        deck = full_deck(LectureDeck(locale='en'))
        with tempfile.TemporaryDirectory() as temp:
            teacher = deck.export(Path(temp) / 'teacher.html').read_text()
            student = deck.export(Path(temp) / 'student.html', include_answers=False).read_text()
        for secret in ('secret-activity', 'secret-quiz', 'secret_solution', 'class="ls-option" data-correct'):
            self.assertIn(secret, teacher)
            self.assertNotIn(secret, student)
        self.assertNotIn('speaker-only', teacher)
        self.assertNotIn('<script', teacher)

    def test_presentation_export(self):
        deck = full_deck(LectureDeck(locale='en'))
        with tempfile.TemporaryDirectory() as temp:
            page = deck.export(Path(temp) / 'slides.html', present=True, fragments=True).read_text()
        self.assertIn('lecture-studio ls-present', page)
        self.assertIn('data-fragments="true"', page)
        self.assertIn('speaker-only', page)
        self.assertIn('LECTURE_STUDIO_LABELS', page)
        self.assertEqual(page.count('<script>'), 1)

    def test_json_round_trip(self):
        deck = full_deck(LectureDeck(course='Round trip', locale='en', theme='ocean'))
        deck.slide('Rich', RichText('<b>bold</b>'), id='rich', show=False)
        with tempfile.TemporaryDirectory() as temp:
            path = deck.save(Path(temp) / 'course.json')
            data = json.loads(path.read_text())
            self.assertEqual(data['locale'], 'en')
            self.assertEqual(data['components'][-1]['id'], 'rich')
            again = LectureDeck.from_file(path, show=False)
        self.assertEqual(again.components, deck.components)
        self.assertEqual(again.html(), deck.html())


if __name__ == '__main__':
    unittest.main()

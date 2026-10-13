import html
import re
import unittest

from lecture_studio import LectureDeck
from lecture_studio.highlight import highlight, split_lines
from lecture_studio.lexers import highlighter_names, language_label, register_highlighter

SAMPLES = {
    'c': '#include <stdio.h>\nint main(void) {\n    printf("%d\\n", 42); /* done */\n    return 0;\n}',
    'cpp': '#include <vector>\nclass Student {};\nint main() {\n    std::vector<int> v = {1, 2};\n    int* p = nullptr;\n    std::cout << v.size() << std::endl;\n}',
    'java': '@Override\npublic class Main {\n    String s = "a\\"b"; // note\n    long n = 10_000L;\n    boolean ok = true;\n}',
    'csharp': 'var path = @"C:\\temp";\nConsole.WriteLine($"Hi {path}");',
    'javascript': "const total = [1, 2].reduce((a, b) => a + b, 0);\nconsole.log(`Total: ${total}`); // 3\nlet $el = null;",
    'typescript': 'interface User { name: string }\n@Component\nclass Box<T> {}',
    'sql': "select name, count(*) from students where grade >= 80 and name like 'O''Neil' -- top\norder by name desc;",
    'bash': '#!/bin/bash\necho "Home: $HOME" ${USER} $1  # done\nif [ -f x ]; then cat x; fi',
    'go': 'package main\nimport "fmt"\nfunc main() { fmt.Println(len(`raw`), nil) }',
    'rust': '#[derive(Debug)]\nfn longest<\'a>(x: &\'a str) -> &\'a str { println!("{}", x); x }',
    'kotlin': 'data class User(val name: String)\nfun main() = println("""raw""")',
    'dart': "void main() { print('hi'); }",
    'swift': 'let x: Int = 5\nprint(x, nil)',
    'r': 'x <- c(1, 2) # values\nprint(mean(x))',
    'matlab': "x = [1 2 3]'; % transpose\ndisp('ok')",
    'json': '{"name": "Ali", "score": -3.5e2, "ok": true, "none": null}',
    'html': '<!DOCTYPE html>\n<!-- c -->\n<p class="x" id=main>A &amp; <b>B</b></p>',
    'css': '/* c */\n.card:hover, h1 { color: #fff; margin: -4px 1.5rem !important; }\n@media (max-width: 600px) {}',
}


def spans(markup):
    return [(cls, html.unescape(text)) for cls, text in re.findall(r'<span class="(\w+)">([^<]*)</span>', markup)]


class LexerTests(unittest.TestCase):
    def test_every_builtin_language_round_trips_its_source(self):
        for language, code in SAMPLES.items():
            with self.subTest(language=language):
                markup = highlight(code, language)
                self.assertEqual(html.unescape(re.sub(r'<[^>]+>', '', markup)), code)
                self.assertTrue(spans(markup))

    def test_code_is_always_escaped(self):
        hostile = '</code><script>alert(1)</script> "<img onerror=x>" // <b>'
        for language in highlighter_names():
            with self.subTest(language=language):
                markup = highlight(hostile, language)
                self.assertNotIn('<script', markup)
                self.assertNotIn('<img', markup)
                self.assertNotIn('<b>', markup)

    def test_language_specific_tokens(self):
        expected = {
            'c': [('cp', '#include <stdio.h>'), ('nb', 'printf'), ('c', '/* done */')],
            'cpp': [('k', 'class'), ('nc', 'Student'), ('kc', 'nullptr'), ('nb', 'std'), ('kt', 'vector')],
            'java': [('nd', '@Override'), ('s', '"a\\"b"'), ('m', '10_000L'), ('kc', 'true')],
            'csharp': [('s', '@"C:\\temp"'), ('nb', 'Console'), ('s', '$"Hi {path}"')],
            'javascript': [('s', '`Total: ${total}`'), ('nb', 'console'), ('kc', 'null')],
            'typescript': [('k', 'interface'), ('kt', 'string'), ('nd', '@Component')],
            'sql': [('k', 'select'), ('nb', 'count'), ('s', "'O''Neil'"), ('c', '-- top'), ('k', 'desc')],
            'bash': [('c', '#!/bin/bash'), ('nb', 'echo'), ('nv', '${USER}'), ('nv', '$1'), ('k', 'fi')],
            'go': [('k', 'func'), ('s', '`raw`'), ('kc', 'nil'), ('nb', 'len')],
            'rust': [('nd', '#[derive(Debug)]'), ('nb', 'println!'), ('kt', 'str')],
            'kotlin': [('k', 'data'), ('nc', 'User'), ('s', '"""raw"""')],
            'r': [('c', '# values'), ('nb', 'mean')],
            'matlab': [('c', '% transpose'), ('s', "'ok'")],
            'json': [('nt', '"name"'), ('s', '"Ali"'), ('m', '-3.5e2'), ('kc', 'true')],
            'html': [('cp', '<!DOCTYPE html>'), ('c', '<!-- c -->'), ('nt', 'p'), ('na', 'class'), ('s', '"x"'), ('s', 'main')],
            'css': [('nc', '.card'), ('nc', ':hover'), ('nt', 'h1'), ('na', 'color'), ('m', '#fff'), ('m', '-4px'),
                    ('k', '!important'), ('k', '@media')],
        }
        for language, tokens in expected.items():
            found = spans(highlight(SAMPLES[language], language))
            for token in tokens:
                with self.subTest(language=language, token=token):
                    self.assertIn(token, found)

    def test_lifetimes_and_transposes_are_not_strings(self):
        self.assertNotIn(('s', "'a>(x: &'"), spans(highlight(SAMPLES['rust'], 'rust')))
        self.assertFalse([t for c, t in spans(highlight("y = x';", 'matlab')) if c == 's'])

    def test_aliases_and_labels(self):
        for alias in ['c++', 'CPP', 'hpp', 'cs', 'C#', 'js', 'ts', 'sh', 'postgres', 'golang']:
            with self.subTest(alias=alias):
                self.assertTrue(spans(highlight('int x = 1; select', alias)) or alias in ('sh',))
        self.assertEqual(language_label('cpp'), 'C++')
        self.assertEqual(language_label('csharp'), 'C#')
        self.assertEqual(language_label('python'), 'PYTHON')
        deck = LectureDeck(locale='en', language='cpp')
        self.assertIn('<span>C++</span>', deck.code('int x = 1;', show=False))

    def test_multiline_comments_stay_balanced_per_line(self):
        markup = split_lines(highlight('/* one\ntwo */\nint x;', 'c'), numbers=True)
        for line in re.findall(r'<span class="ls-line" data-line="\d+">(.*?)</span>(?=<span class="ls-line"|</span>$)', markup):
            self.assertEqual(line.count('<span'), line.count('</span>'))
        self.assertIn('data-line="2"><span class="c">two */</span>', markup)

    def test_register_custom_highlighter(self):
        register_highlighter(['pseudo-test'], lambda code: '<span class="k">' + html.escape(code) + '</span>',
                             label='Pseudocode')
        self.assertEqual(highlight('IF <x>', 'pseudo-test'), '<span class="k">IF &lt;x&gt;</span>')
        self.assertEqual(language_label('pseudo-test'), 'PSEUDOCODE')
        with self.assertRaises(ValueError):
            register_highlighter(['pseudo-test'], str)
        register_highlighter('pseudo-test', html.escape, replace=True)
        self.assertEqual(highlight('<x>', 'pseudo-test'), '&lt;x&gt;')
        for bad in ([], ['has space'], ['']):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                register_highlighter(bad, html.escape)
        with self.assertRaises(TypeError):
            register_highlighter(['other-test'], 'not callable')  # type: ignore[arg-type]

    def test_unknown_language_is_escaped_text(self):
        self.assertEqual(highlight('a < b', 'no-such-language'), 'a &lt; b')


if __name__ == '__main__':
    unittest.main()

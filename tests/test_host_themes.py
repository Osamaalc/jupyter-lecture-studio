"""Lectures under light and dark notebook themes.

The same notebook is exported with nbconvert's JupyterLab Light and Dark themes (the host CSS
JupyterLab itself uses) and measured in Chromium:

- every element of a deck has identical colors under both themes (the host never leaks in);
- with ``notebook_style=True`` the notebook follows the host theme, and every text run in markdown,
  code and output cells stays readable (WCAG AA contrast) in both.
"""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from lecture_studio import LectureDeck

AVAILABLE = all(importlib.util.find_spec(name) for name in ['playwright', 'nbconvert', 'nbformat'])

PROPS = ['color', 'background-color', 'background-image', 'border-top-color', 'border-bottom-color',
         'border-left-color', 'border-right-color', 'fill', 'stroke', 'box-shadow']

STYLES = r'''props => [...document.querySelectorAll('.lecture-studio :is(.ls-frame, .ls-note, .ls-callout), '
  + '.lecture-studio :is(.ls-frame, .ls-note, .ls-callout) *')].map(e => {
    const s = getComputedStyle(e);
    return [e.tagName + '.' + (e.getAttribute('class') || ''), ...props.map(p => s.getPropertyValue(p))];
})'''

CONTRAST = r'''() => {
  const rgb = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const mix = (t, u) => ({r: t.r * t.a + u.r * (1 - t.a), g: t.g * t.a + u.g * (1 - t.a), b: t.b * t.a + u.b * (1 - t.a), a: 1});
  const lum = c => [c.r, c.g, c.b].map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; })
    .reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const backdrop = el => { const layers = [];
    for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= .95) break; } }
    return layers.reverse().reduce((under, top) => mix(top, under), {r: 255, g: 255, b: 255, a: 1}); };
  const out = [];
  document.querySelectorAll('.jp-MarkdownCell, .jp-CodeCell:not(:has(.lecture-studio))').forEach(cell => {
    const walk = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
    for (let n = walk.nextNode(); n; n = walk.nextNode()) {
      const el = n.parentElement; if (!n.textContent.trim() || el.closest('style,script')) continue;
      const s = getComputedStyle(el); if (s.display === 'none' || s.visibility === 'hidden') continue;
      const bg = backdrop(el), fg = mix(rgb(s.color), bg);
      out.push([n.textContent.trim().slice(0, 30), Math.round(ratio(fg, bg) * 100) / 100]);
    }
  });
  return out;
}'''


def notebook(deck_html: str):
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output
    show = new_code_cell('deck.slide(...)', outputs=[new_output('display_data', data={'text/html': deck_html})])
    practice = new_code_cell('name = "Ali"\nprint(f"Hello {name}", [1, 2])  # greeting',
                             outputs=[new_output('stream', name='stdout', text='Hello Ali [1, 2]\n')])
    text = '## Markdown\n\nA paragraph with `code` and a [link](https://example.com).\n\n| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |'
    nb = new_notebook(cells=[new_markdown_cell(text), show, practice])
    nbformat.validate(nb)
    return nb


@unittest.skipUnless(AVAILABLE, 'needs nbconvert and Playwright with Chromium')
class HostThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from nbconvert import HTMLExporter
        from playwright.sync_api import sync_playwright

        deck = LectureDeck(course='Host themes', notebook_style=True)
        parts = [
            deck.agenda(['Use `print()` and `len()`'], show=False),
            deck.slide('Inline `code`', 'Text with `x = 1`.', cards=[{'title': 'Card', 'explanation': 'A `code` chip',
                                                                      'code': 'print(1)'}], show=False),
            deck.table('Table', ['A', 'B'], [['1', '`x`'], ['2', 'y'], ['3', 'z']], show=False),
            deck.callout('A `code` chip in a callout.', style='tip', show=False),
            deck.trace('x = 1\nx += 1', [{'line': 1, 'variables': {'x': 1}}, {'line': 2, 'variables': {'x': 2}}],
                       show=False),
            deck.matrix([[1, 0], [0, 1]], name='I', brackets=True, show=False),
            deck.confusion_matrix([[5, 1], [2, 4]], ['a', 'b'], show=False),
            LectureDeck(theme='paper', locale='en').slide('Paper', 'With `code`.', show=False),
        ]
        cls.results = {}
        temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        browser_path = os.environ.get('LECTURE_STUDIO_TEST_BROWSER')
        with sync_playwright() as playwright:
            launch = {'executable_path': browser_path} if browser_path else {'channel': 'chromium'}
            try:
                browser = playwright.chromium.launch(**launch)
            except Exception as error:  # noqa: BLE001 - no browser installed
                raise unittest.SkipTest(f'Chromium unavailable: {error}') from error
            for theme in ('light', 'dark'):
                html, _ = HTMLExporter(template_name='lab', theme=theme).from_notebook_node(notebook(''.join(parts)))
                path = Path(temp.name) / f'{theme}.html'
                path.write_text(html, encoding='utf-8')
                page = browser.new_page(viewport={'width': 1300, 'height': 900})
                page.goto(path.as_uri())
                page.evaluate('document.fonts.ready')
                cls.results[theme] = {
                    'styles': page.evaluate(STYLES, PROPS),
                    'contrast': page.evaluate(CONTRAST),
                    'page': page.evaluate('getComputedStyle(document.querySelector(".jp-Notebook")).backgroundColor'),
                    'hover': page.evaluate('''() => { const tr = document.querySelector('.lecture-studio .ls-vars tr');
                        return getComputedStyle(tr).backgroundColor; }'''),
                }
                page.close()
            browser.close()

    def test_deck_colors_ignore_the_host_theme(self):
        light, dark = self.results['light']['styles'], self.results['dark']['styles']
        self.assertGreater(len(light), 100)
        self.assertEqual(len(light), len(dark))
        for a, b in zip(light, dark, strict=True):
            with self.subTest(element=a[0]):
                self.assertEqual(a, b)

    def test_host_never_paints_deck_rows(self):
        for theme in ('light', 'dark'):
            self.assertEqual(self.results[theme]['hover'], 'rgba(0, 0, 0, 0)', theme)

    def test_notebook_style_follows_the_host_theme(self):
        self.assertNotEqual(self.results['light']['page'], self.results['dark']['page'])

    def test_notebook_text_is_readable_in_both_themes(self):
        for theme in ('light', 'dark'):
            runs = self.results[theme]['contrast']
            self.assertGreater(len(runs), 10, theme)
            for text, ratio in runs:
                with self.subTest(theme=theme, text=text):
                    self.assertGreaterEqual(ratio, 4.5)


if __name__ == '__main__':
    unittest.main()

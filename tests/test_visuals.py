import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

from lecture_studio import LectureDeck, to_mathml
from lecture_studio.components.visuals import nice_ticks
from lecture_studio.markup import inline
from lecture_studio.mathml import MathError
from lecture_studio.visuals import Column

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'examples'))
import subjects  # noqa: E402


def body(markup):
    """MathML without the wrapper and the TeX annotation."""
    return re.search(r'<semantics>(.*)<annotation', markup).group(1)


class MathTests(unittest.TestCase):
    def test_common_formulas(self):
        cases = {
            r'\frac{1}{1 + e^{-z}}': '<mfrac><mn>1</mn><mrow><mn>1</mn><mo>+</mo><msup><mi>e</mi><mrow><mo>−</mo><mi>z</mi></mrow></msup></mrow></mfrac>',
            r'x_i^2': '<msubsup><mi>x</mi><mi>i</mi><mn>2</mn></msubsup>',
            r'\sqrt[3]{8}': '<mroot><mn>8</mn><mn>3</mn></mroot>',
            r'\mathbb{R}^n': '<msup><mi>ℝ</mi><mi>n</mi></msup>',
            r'\mathbf{x}': '<mi>𝐱</mi>',
            r'\hat{y}': '<mover accent="true"><mi>y</mi><mo>ˆ</mo></mover>',
            r'\text{if } x': '<mtext>if </mtext><mi>x</mi>',
            r'a \le b \ne c': '<mi>a</mi><mo>≤</mo><mi>b</mi><mo>≠</mo><mi>c</mi>',
        }
        for latex, expected in cases.items():
            with self.subTest(latex=latex):
                self.assertIn(expected, body(to_mathml(latex)))

    def test_limits_operators_and_environments(self):
        self.assertIn('<munderover><mo movablelimits="true">∑</mo>', to_mathml(r'\sum_{i=1}^{n} x_i'))
        self.assertIn('<msubsup><mo>∫</mo>', to_mathml(r'\int_0^1 f'))
        self.assertIn('<munder><mo movablelimits="true" lspace="0.1667em" rspace="0.1667em">arg max</mo>',
                      to_mathml(r'\argmax_w P(w)'))
        self.assertIn('<mo lspace="0.1667em" rspace="0.1667em">log</mo>', to_mathml(r'\log x'))
        matrix = to_mathml(r'\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}')
        self.assertEqual(matrix.count('<mtr>'), 2)
        self.assertEqual(matrix.count('<mtd>'), 4)
        self.assertIn('<mo stretchy="true">[</mo>', matrix)
        cases = to_mathml(r'|x| = \begin{cases} x & x \ge 0 \\ -x & \text{otherwise} \end{cases}')
        self.assertIn('columnalign="left"', cases)
        self.assertIn('<mrow><mo stretchy="true">(</mo>', to_mathml(r'\left( \frac{a}{b} \right)'))

    def test_errors_are_reported_when_authoring(self):
        for latex in [r'\unknown', r'x^2^3', r'x_1_2', r'\frac{1}', r'\left( x', r'{x', 'x}', r'\begin{foo}x\end{foo}',
                      r'\begin{matrix} 1 \end{bmatrix}']:
            with self.subTest(latex=latex), self.assertRaises(MathError):
                to_mathml(latex)
        with self.assertRaises(ValueError):
            LectureDeck().math(r'\nosuchcommand', show=False)

    def test_formula_text_is_escaped(self):
        markup = to_mathml(r'a < b \text{<script>}')
        self.assertNotIn('<script>', markup)
        self.assertIn('<mo>&lt;</mo>', markup)
        self.assertIn('&lt;script&gt;', markup)

    def test_inline_math_in_text(self):
        self.assertIn('<math', inline('the line $y = wx + b$ fits'))
        for plain in ['costs $5 to $10', 'echo $HOME and $PATH', r'a literal \$x$', 'use `$x$` in code']:
            with self.subTest(text=plain):
                self.assertNotIn('<math', inline(plain))
        self.assertIn('literal $x$', inline(r'literal \$x$'))
        self.assertNotIn('<math', inline('$x$', markup='text'))
        arabic = inline('المعادلة $C$ مع C++', direction='rtl')
        self.assertIn('<bdi dir="ltr">C++</bdi>', arabic)
        self.assertNotIn('<bdi', arabic.split('</math>')[0])


class VisualTests(unittest.TestCase):
    def test_every_visual_renders_in_both_locales(self):
        for locale in ('ar', 'en'):
            deck = subjects.build(locale)
            kinds = [c.kind for c in deck]
            for kind in ['math', 'network', 'chart', 'matrix', 'array', 'memory', 'tree', 'graph', 'schema']:
                self.assertIn(kind, kinds)
            html = deck.html()
            self.assertEqual(html.count('class="ls-svg"'), kinds.count('chart') + kinds.count('network')
                             + kinds.count('tree') + kinds.count('graph') + kinds.count('memory') + kinds.count('schema'))
            self.assertIn('ls-viz-array', html)

    def test_json_round_trip_is_identical(self):
        deck = subjects.build('en')
        with tempfile.TemporaryDirectory() as temp:
            path = deck.save(Path(temp) / 'visuals.json')
            again = LectureDeck.from_file(path, show=False)
        self.assertEqual(json.dumps(again.to_dict(), sort_keys=True), json.dumps(deck.to_dict(), sort_keys=True))
        self.assertEqual(again.html(), deck.html())

    def test_markers_are_unique_per_component(self):
        deck = LectureDeck(locale='en')
        for _ in range(2):
            deck.graph(['A', 'B'], [('A', 'B')], directed=True, show=False)
        ids = re.findall(r'<marker id="([^"]+)"', deck.html())
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 2)

    def test_array_validation_and_layout(self):
        deck = LectureDeck(locale='en')
        html = deck.array([1, 2, 3], name='a', pointers={'end': 3}, slice=[0, 2], show=False)
        self.assertIn('is-ghost', html)
        self.assertIn('a[0:2]', html)
        for bad in [dict(values=[]), dict(values=[1], highlight=[1]), dict(values=[1, 2], slice=[2, 1]),
                    dict(values=[1], pointers={'i': 2}), dict(values='abc')]:
            with self.subTest(bad=bad), self.assertRaises((ValueError, TypeError)):
                deck.array(show=False, **bad)

    def test_confusion_matrix_reports_accuracy(self):
        deck = LectureDeck(locale='en')
        html = deck.confusion_matrix([[8, 2], [1, 9]], ['spam', 'ham'], show=False)
        self.assertIn('Accuracy', html)
        self.assertIn('85.0%', html)
        self.assertEqual(html.split('</style>')[-1].count('is-marked'), 2)
        arabic = LectureDeck(locale='ar').confusion_matrix([[1, 0], [0, 1]], ['أ', 'ب'], show=False)
        self.assertIn('الدقة', arabic)
        with self.assertRaises(ValueError):
            deck.matrix([[1, 2], [3]], show=False)
        with self.assertRaises(ValueError):
            deck.matrix([['a']], heatmap=True, show=False)

    def test_chart_inputs(self):
        deck = LectureDeck(locale='en')
        self.assertIn('<polyline', deck.chart([1, 3, 2], show=False))
        self.assertEqual(deck.chart({'a': [1, 2], 'b': [2, 1]}, mode='bar', show=False).count('class="ls-bar"'), 4)
        scatter = deck.chart([{'name': 'pts', 'values': [1, 2], 'x': [0.5, 1.5]}], mode='scatter', show=False)
        self.assertEqual(scatter.count('class="ls-point"'), 2)
        for bad in [dict(series=[]), dict(series={'a': [1], 'b': [1, 2]}), dict(series=[1, float('nan')]),
                    dict(series=[1, 2], labels=['x']), dict(series=[1, 2], mode='pie'),
                    dict(series=[{'name': 's', 'values': [1]}], mode='scatter')]:
            with self.subTest(bad=bad), self.assertRaises((ValueError, TypeError)):
                deck.chart(show=False, **bad)
        self.assertEqual(nice_ticks(0, 1), [0, 0.25, 0.5, 0.75, 1])
        self.assertEqual(nice_ticks(0.23, 0.95), [0.2, 0.4, 0.6, 0.8, 1])

    def test_large_networks_are_abbreviated(self):
        html = LectureDeck(locale='en').network([784, 128, 10], show=False)
        self.assertEqual(html.count('class="ls-neuron"'), 6 * 3)  # 3 + ellipsis + 3 per layer
        self.assertEqual(html.count('⋮'), 3)
        self.assertIn('>784<', html)
        with self.assertRaises(ValueError):
            LectureDeck().network([3], show=False)

    def test_tree_and_graph_validation(self):
        deck = LectureDeck(locale='en')
        self.assertEqual(deck.tree({'value': 1, 'children': [None, {'value': 2}]}, show=False).count('class="ls-edge"'), 1)
        with self.assertRaises(ValueError):
            deck.graph(['A'], [('A', 'Z')], show=False)
        with self.assertRaises(ValueError):
            deck.graph(['A', 'A'], show=False)
        with self.assertRaises(ValueError):
            deck.graph([{'id': 'A', 'x': 10, 'y': 10}, 'B'], show=False)
        deep = {'value': 0}
        for level in range(8):
            deep = {'value': level, 'children': [deep]}
        with self.assertRaises(ValueError):
            deck.tree(deep, show=False)

    def test_memory_references(self):
        deck = LectureDeck(locale='en')
        html = deck.memory({'main': {'p': '@x', 'n': 5}}, {'x': {'next': '@x'}}, show=False)
        self.assertEqual(html.count('class="ls-ref"'), 2)
        with self.assertRaises(ValueError):
            deck.memory({'main': {'p': '@missing'}}, show=False)
        self.assertIn('Call frames', html)
        self.assertIn('Stack', deck.memory({'f': {}}, stack_label='Stack', show=False))

    def test_schema_shorthand_and_references(self):
        column = Column.parse('student_id INT FK -> students.id')
        self.assertEqual((column.name, column.type, column.key, column.references),
                         ('student_id', 'INT', 'fk', 'students.id'))
        self.assertEqual(Column.parse('id INT PK').key, 'pk')
        deck = LectureDeck(locale='en')
        html = deck.schema({'a': ['id PK'], 'b': ['id PK', 'a_id FK -> a.id'], 'c': ['parent FK -> c.parent']}, show=False)
        self.assertEqual(html.count('class="ls-relation"'), 2)
        with self.assertRaises(ValueError):
            deck.schema({'a': ['x FK -> missing.id']}, show=False)
        with self.assertRaises(ValueError):
            Column('x', key='primary')

    def test_visual_text_is_escaped(self):
        deck = LectureDeck(locale='en')
        hostile = '<img src=x onerror=alert(1)>'
        outputs = [
            deck.array([hostile], name=hostile, show=False),
            deck.matrix([[hostile]], row_labels=[hostile], show=False),
            deck.chart({hostile: [1, 2]}, labels=[hostile, 'b'], x_label=hostile, show=False),
            deck.network([2, 2], labels=[hostile, hostile], show=False),
            deck.tree({'value': hostile, 'note': hostile}, show=False),
            deck.graph([{'id': hostile}], show=False),
            deck.memory({hostile: {hostile: hostile}}, show=False),
            deck.schema({hostile: [hostile]}, show=False),
        ]
        for output in outputs:
            with self.subTest(output=output[:60]):
                self.assertNotIn('<img', output)


if __name__ == '__main__':
    unittest.main()

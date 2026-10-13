# Formulas and subject visuals

Lecture Studio draws the figures courses keep redrawing by hand: formulas, arrays, matrices, charts, neural networks, trees, graphs, memory diagrams and database schemas. Each one is a deck method, a model class and a JSON `"type"`, like every other component.

Every visual is laid out in Python and rendered as plain HTML, MathML or inline SVG. There is no JavaScript and no download. The same input always produces the same figure, and figures stay sharp when zoomed or printed. Themes color them through `--ls-viz-*` tokens. Text inside a figure is escaped like all other author text.

| Method | JSON `type` | Draws |
|---|---|---|
| `math` | `math` | Display formulas in LaTeX, with a legend of symbols |
| `array` | `array` | A list as indexed cells, with pointers, a slice and negative indexes |
| `matrix` | `matrix` | A grid, a math matrix (`brackets=True`) or a heatmap |
| `confusion_matrix` | `matrix` | A classifier's confusion matrix with its accuracy |
| `chart` | `chart` | Line, bar or scatter charts |
| `network` | `network` | A fully connected neural network |
| `tree` | `tree` | Search trees, parse trees, decision trees |
| `graph` | `graph` | Nodes and edges, directed or not, with weights |
| `memory` | `memory` | Call frames, variables and the objects they reference |
| `schema` | `schema` | Database tables, keys and relationships |

All visuals accept `title`, `description`, `caption`, `notes`, `id` and `show`. A complete example for every visual is in `examples/subjects.py`.

## Formulas

```python
deck.math(r"\sigma(z) = \frac{1}{1 + e^{-z}}",
          title="The logistic function",
          legend={"z": "weighted sum", r"\sigma": "activation"})

deck.math([r"\hat{y} = \operatorname{softmax}(W\mathbf{x} + b)",
           r"\theta \gets \theta - \eta \, \nabla_\theta J(\theta)"])
```

Formulas inside any text use `$...$`: `"We compute $z = w^T x + b$ first."` The rules follow Pandoc, so prices stay text. The opening `$` must touch the formula and the closing `$` must not be followed by a digit, which keeps `"$5 to $10"` as plain text. Write `\$` for a literal dollar sign. Inline code (`` `$x$` ``) is never treated as a formula.

Formulas become MathML, which Chrome, Edge, Firefox and Safari render natively, and PDF exports keep them as selectable text. The supported LaTeX covers:

- fractions and binomials: `\frac`, `\dfrac`, `\binom`;
- roots and scripts: `\sqrt`, `\sqrt[n]`, `^`, `_` and primes;
- large operators and limits: `\sum`, `\prod`, `\int` and `\lim`, `\max`, `\min`, `\argmax`;
- function names: `\log`, `\sin`, `\exp` and `\operatorname{...}`;
- symbols: Greek letters, relations, arrows, set symbols;
- accents: `\hat`, `\bar`, `\vec`, `\tilde`, `\dot`;
- fonts and text: `\mathbf`, `\mathbb`, `\mathcal`, `\mathrm`, `\text`;
- delimiters and environments: `\left`/`\right` and `matrix`, `pmatrix`, `bmatrix`, `vmatrix`, `cases`, `aligned`.

An unsupported command raises `ValueError` when the lecture is built, never in front of students. `to_mathml(latex)` converts a formula on its own.

## Arrays

```python
deck.array([12, 7, 25, 3, 18, 9], name="nums", highlight=[2],
           pointers={"low": 0, "mid": 2, "high": 5}, slice=[1, 4], negative=True)
```

`pointers` maps labels to indexes; an index equal to the length marks the position after the last item. `slice=[start, stop]` underlines `nums[start:stop]`. `negative=True` adds Python's negative indexes.

## Matrices, heatmaps and confusion matrices

```python
deck.matrix([[1, 0, 2], [-1, 3, 1]], name="W", brackets=True)
deck.matrix([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1], [0.3, 0.3, 0.4]],
            row_labels=["I", "like", "AI"], col_labels=["I", "like", "AI"], heatmap=True)
deck.confusion_matrix([[48, 2, 0], [5, 40, 5], [1, 3, 46]], ["cat", "dog", "bird"])
```

`highlight=[[row, col], ...]` outlines cells and `metrics={"F1": "0.91"}` adds figures under the grid. `confusion_matrix` labels the axes in the lecture's language, outlines the diagonal and computes the accuracy.

## Charts

```python
deck.chart({"training": [0.92, 0.61, 0.44, 0.35], "validation": [0.95, 0.66, 0.52, 0.49]},
           labels=["1", "2", "3", "4"], x_label="Epoch", y_label="Loss")
deck.chart({"Python": [68, 74], "C++": [55, 61]}, mode="bar", labels=["2024", "2025"])
deck.chart([{"name": "samples", "values": [1.2, 2.3, 2.9], "x": [1, 2, 3]}], mode="scatter")
```

`series` is a list of numbers, a dictionary of named series or a list of `{"name", "values", "x"}`. Bar charts always include zero. Set `y_min`/`y_max` to fix the axis.

## Neural networks

```python
deck.network([784, 128, 64, 10], labels=["Pixels", "Hidden 1", "Hidden 2", "Digits"])
```

Layers wider than seven neurons are drawn as three neurons, a vertical ellipsis and three more, with the real size underneath.

## Trees and graphs

```python
deck.tree({"value": 8, "children": [
    {"value": 3, "children": [{"value": 1}, {"value": 6}]},
    {"value": 10, "children": [None, {"value": 14, "selected": True}]},
]})

deck.graph(["A", "B", "C", "D"], [("A", "B", 4), ("A", "C", 2), ("C", "B", 1), ("B", "D", 5)], directed=True)
```

A `None` child keeps an empty slot, so binary trees keep their left and right sides. Graph nodes are placed on a circle unless every node has `x` and `y` on a 0–100 grid. Edges are `(source, target)` or `(source, target, label)`, or dictionaries with `selected=True` to highlight a path.

## Memory diagrams

```python
deck.memory({"global": {"scores": "@a", "alias": "@a"}, "average(values)": {"values": "@a"}},
            {"a": [70, 80, 85]})

deck.memory({"main()": {"head": "@n1"}}, [
    {"id": "n1", "type": "Node", "value": {"data": 5, "next": "@n2"}},
    {"id": "n2", "type": "Node", "value": {"data": 8, "next": "nullptr"}},
], heap_label="Heap")
```

A value written `"@id"` draws an arrow to the object with that id. Objects hold text, a list (indexed slots) or a dictionary (named fields), so the same component shows Python names and objects, C and C++ pointers, linked lists and recursion. The last frame is drawn as the active one.

## Database schemas

```python
deck.schema({
    "students": ["id INT PK", "name VARCHAR", "major_id INT FK -> majors.id"],
    "majors": ["id INT PK", "name VARCHAR UQ"],
})
```

Each column is a shorthand string, `name [TYPE] [PK] [FK] [UQ] [-> table.column]`, or a dictionary with `name`, `type`, `key` and `references`. Relationships are drawn from the foreign key, with the crow's foot on the "many" side, to the referenced column. `per_row` sets how many tables share a row.

## Syntax highlighting for every course

Python, C, C++, Java, C#, JavaScript, TypeScript, Kotlin, Go, Rust, Dart, Swift, SQL, Bash, R, MATLAB, JSON, HTML/XML and CSS are highlighted by the library itself, so they look the same on every computer and need no extra package. The code toolbar names the language (`cpp` shows as `C++`). Other languages use Pygments when the `highlight` extra is installed.

Code fonts never merge symbols into ligatures, so `!=`, `>=` and `<<` look exactly as students type them.

Add a language or replace a built-in one with a function that returns escaped HTML using the same token classes:

```python
import html
import re
from lecture_studio import register_highlighter

def pseudocode(code: str) -> str:
    return re.sub(r"\b(IF|THEN|ELSE|WHILE|RETURN)\b", r'<span class="k">\1</span>', html.escape(code))

register_highlighter(["pseudo"], pseudocode, label="Pseudocode")
```

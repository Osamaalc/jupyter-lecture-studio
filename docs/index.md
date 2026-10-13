---
myst:
  html_meta:
    description: Bilingual (Arabic/English) teaching slides, quizzes, execution traces and code walkthroughs for Jupyter, offline HTML, slideshows and PDF.
    keywords: Jupyter lecture slides, teaching notebooks, Arabic RTL, bilingual, quiz, code trace, offline HTML, presentation
---
# Jupyter Lecture Studio

**Premium, bilingual teaching components for Jupyter — one design for every course.**

Write a lecture in Python or JSON. Present it in Jupyter, share it as a single offline HTML file, project it as a slideshow, or print it as a PDF. Arabic and English are both first-class: interface labels, writing direction and typography follow the lecture's language.

```{container} hero-note
Covers, concept slides, execution traces, code comparisons, quizzes, exercises and callouts, plus formulas, charts, neural networks, trees, graphs, memory diagrams and database schemas — all without JavaScript, all themed, all safe by default.
```

```bash
python -m pip install "jupyter-lecture-studio[notebook,highlight]"
```

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Python Programming", locale="en", theme="paper")
deck.cover("Names and values", "Connect familiar ideas to Python.")
deck.slide("Rebinding a name", cards=[
    {"title": "Observe", "code": "value = 10\nvalue = 'ten'"},
    {"title": "Explain", "explanation": "The name `value` now refers to a different object."},
])
deck.quiz("What does `value` hold now?", ["10", "'ten'"], answer=1)
deck.export("lecture.html")
```

## Choose your path

- **Start here:** [install and build your first lecture](getting-started.md).
- **Teachers:** [components](components.md), [formulas and subject visuals](visuals.md), [teaching, sharing and presenting](presenting.md) and [recipes](cookbook.md).
- **Design:** [themes and design tokens](themes.md), [languages](languages.md).
- **Developers:** [API reference](reference.rst), [CLI and JSON](cli.md), [extending](extending.md), [architecture](architecture.md).
- **العربية:** [دليل الاستخدام الكامل](USAGE_AR.md) و[مرجع الواجهة](API.md) و[الانتقال إلى 1.0](MIGRATION.md).

The library displays code; it never executes it. Executable practice belongs in ordinary notebook cells. The core has no required dependencies.

```{toctree}
:maxdepth: 2
:caption: Learn

getting-started
components
visuals
presenting
themes
languages
cookbook
pdf
cli
```

```{toctree}
:maxdepth: 1
:caption: Develop

reference
extending
architecture
```

```{toctree}
:maxdepth: 1
:caption: العربية

USAGE_AR
API
MIGRATION
```

```{toctree}
:maxdepth: 1
:caption: Project

troubleshooting
licensing
release-notes
```

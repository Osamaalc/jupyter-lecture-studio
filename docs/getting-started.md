# Install and build your first lecture

## Requirements

Python 3.10 or later. The visual components target modern browsers. Notebook canvas styling has been verified in JupyterLab. Hosted notebook platforms may sanitize CSS, so validate their output before teaching.

## Install in the correct environment

```bash
python -m pip install "jupyter-lecture-studio[notebook,highlight]"
```

Inside a notebook, install into the current kernel:

```python
%pip install "jupyter-lecture-studio[notebook,highlight]"
```

Restart the kernel after installation or upgrading. `notebook` installs IPython for display. `highlight` adds Pygments for languages such as Java, C++ and SQL. Python highlighting is built in.

For a script that only exports HTML:

```bash
python -m pip install jupyter-lecture-studio
```

## Cell 1: create the lecture identity

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(
    course="Database Fundamentals",
    series="DATABASE SERIES",
    lesson="01",
    language="sql",
    locale="en",
    theme="gold",
)
```

Create one deck per lecture. Its brand controls the repeated labels, its locale the interface language and direction (`"ar"` by default, `"en"` for English), and its theme the colors, motion and width. See [Themes](themes.md) and [Languages](languages.md).

## Cell 2: introduce the lesson

```python
deck.cover(
    "Ask better questions of your data",
    "Select only what you need.\nExplain why the result is correct.",
    tags=["Understand", "Predict", "Try"],
    sections=[
        {"title": "The idea", "description": "Columns and rows"},
        {"title": "The application", "description": "Write a SELECT query"},
    ],
    hero_code="SELECT name FROM students;",
    hero_result="A focused result",
    hero_label="SQL LAB",
    footer_label="DATABASE / FOUNDATIONS",
)
```

## Cell 3: explain and check understanding

```python
deck.slide(
    "Select a column",
    "A projection chooses the fields in the result.",
    cards=[
        {"title": "Concept", "explanation": "SELECT lists the requested columns."},
        {"title": "Example", "code": "SELECT name FROM students;"},
    ],
    activity={
        "question": "Will the result contain the grade column?",
        "answer": "No. Only name appears in the SELECT list.",
        "label": "Predict first",
        "reveal": "Show the explanation",
    },
)
```

Add executable student examples in separate code cells. Displaying a code card never executes its text.

## Cell 4: check understanding with a quiz

```python
deck.quiz("Which clause filters rows?", ["SELECT", "WHERE", "FROM"], answer=1,
          explanation="`WHERE` keeps only the rows that match the condition.")
```

## Export and share

```python
deck.export("output/database-01.html")                              # teacher copy
deck.export("output/database-01-student.html", include_answers=False)  # student copy
deck.export("output/database-01-slides.html", present=True)            # slideshow
```

Each file contains its styles and the Cairo and JetBrains Mono fonts, and works offline on any device. Export includes the deck's components only, not unrelated notebook cells. See [Teaching, sharing and presenting](presenting.md).

## Scripts and repeated execution

Methods display and return `None` by default. In scripts, use `show=False`:

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Offline lesson", locale="en", motion=False)
html = deck.slide("A useful idea", cards=[{"title": "Explain", "explanation": "Keep it focused."}], show=False)
deck.export("lesson.html")
```

In JupyterLab, Notebook 7 and VS Code, re-running a cell replaces what that cell added, so numbering and exports stay correct. In scripts every call appends; use `id="..."` to replace a specific component, or `deck.clear()` to start again.

## Existing notebooks

`from lecture_studio import LectureDeck` remains supported and refers to the same classes. Installing the new distribution does not require editing your existing imports. New lessons can use `jupyter_lecture_studio` consistently with the PyPI name.

# CLI and JSON workflow

```text
jupyter-lecture-studio init DIR [--course NAME] [--locale ar|en]
jupyter-lecture-studio validate lecture.json
jupyter-lecture-studio export lecture.json lecture.html [--student] [--present] [--fragments]
jupyter-lecture-studio pdf SOURCE lecture.pdf [--mode faithful|vector] [--hide-answers]
jupyter-lecture-studio info | docs | setup-pdf
```

## Create a lecture folder

```bash
jupyter-lecture-studio init lecture-01 --course "Python Programming" --locale en
```

The folder contains `lecture.json` (cover, goals, a slide, a quiz, a tip and a recap), a starter notebook and a README. An existing folder is never overwritten.

## The JSON course format

```json
{
  "brand": {"course": "Python Programming", "series": "PYTHON SERIES", "lesson": "01"},
  "theme": {"preset": "paper", "motion": true},
  "locale": "en",
  "components": [
    {"type": "cover", "title": "Names and values", "description": "Understand rebinding."},
    {"type": "slide", "id": "rebinding", "title": "A name refers to an object",
     "cards": [{"title": "Observe", "code": "x = 10\nx = 'ten'"}],
     "activity": {"question": "What is x now?", "answer": "The string 'ten'."}},
    {"type": "quiz", "question": "Which value does x hold?", "options": ["10", "'ten'"], "answer": 1},
    {"type": "note", "title": "Trusted HTML", "body": {"html": "<em>Allowed</em> because you wrote it."}}
  ]
}
```

Every component type and field is the same as in Python (see [Components](components.md)). Unknown fields and invalid values raise a clear error instead of being ignored. `deck.save("lecture.json")` writes this format from any deck, so you can author in Python and keep JSON, or the reverse.

## Validate and export

```bash
jupyter-lecture-studio validate lecture-01/lecture.json
jupyter-lecture-studio export lecture-01/lecture.json lecture.html
jupyter-lecture-studio export lecture-01/lecture.json lecture-student.html --student
jupyter-lecture-studio export lecture-01/lecture.json lecture-slides.html --present --fragments
```

Export replaces an existing destination. Content is never executed.

## Offline documentation and environment

```bash
jupyter-lecture-studio docs   # path of the bundled documentation site
jupyter-lecture-studio info   # version, components, themes and locales
```

The older `lecture-studio` command and `python -m jupyter_lecture_studio` run the same interface.

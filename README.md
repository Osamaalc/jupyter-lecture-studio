# Jupyter Lecture Studio

**Premium, bilingual teaching components for Jupyter — one design for every course.**

Build lectures in Python or JSON: covers, concept slides, execution traces, code comparisons, quizzes, exercises and callouts, plus formulas, charts, neural networks, trees, graphs, memory diagrams and database schemas. Present them in Jupyter, share them as one offline HTML file, project them as a slideshow, or print them as PDF. Arabic and English are both first-class.

```bash
python -m pip install "jupyter-lecture-studio[notebook,highlight]"
```

## A lecture in one cell

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Introduction to Programming", series="CS 101", lesson="03", locale="en")

deck.cover("Loops and iteration", "Repeat work without repeating code.",
           tags=["Understand", "Trace", "Practice"], hero_code=">>> for x in [1, 2]: print(x)")
deck.agenda(["Write a `for` loop over a list", "Trace an **accumulator** step by step"])
deck.slide("A running total", cards=[
    {"title": "The idea", "explanation": "Start with `total = 0`, then add each item.",
     "code": "total = 0\nfor g in grades:\n    total += g"},
], activity={"question": "What is `total` after the loop?", "answer": "The sum of all grades."})
deck.trace("total = 0\nfor g in [70, 80]:\n    total += g", [
    {"line": 1, "variables": {"total": 0}},
    {"line": 3, "variables": {"total": 70, "g": 70}},
    {"line": 3, "variables": {"total": 150, "g": 80}},
])
deck.compare("Resetting inside the loop", "for g in grades:\n    total = 0", "total = 0\nfor g in grades:")
deck.quiz("How many times does `range(3)` loop?", ["2", "3", "4"], answer=1)
deck.recap(["Initialise before the loop", "Trace variables to explain output"])

deck.export("lecture.html")                                # teacher copy
deck.export("lecture-student.html", include_answers=False)  # no answers or solutions
deck.export("lecture-slides.html", present=True)            # slideshow with speaker notes
```

## Why Lecture Studio

| | |
|---|---|
| **Teaching components** | Cover, agenda/recap, slide, code + output, execution trace, compare, quiz, exercise, callout, figure, divider, note, table |
| **Subject visuals** | LaTeX formulas (`$...$` inline too), arrays with pointers and slices, matrices and confusion matrices, line/bar/scatter charts, neural networks, trees, graphs, memory diagrams and database schemas, drawn as MathML and SVG |
| **Every programming course** | Built-in highlighting for Python, C, C++, Java, C#, JavaScript, TypeScript, Kotlin, Go, Rust, Dart, Swift, SQL, Bash, R, MATLAB, JSON, HTML and CSS, identical on every machine |
| **Interactive without JavaScript** | Quizzes grade the chosen answer, traces step through code, answers and hints reveal — in notebooks and offline files |
| **Arabic and English** | Interface labels and direction follow the locale; layouts mirror; Arabic is never letter-spaced; `C++` stays readable in Arabic text |
| **Themes** | `gold`, `emerald`, `ocean`, `violet`, `ruby` and the light `paper`; every color is a design token; register your institution's theme |
| **Notebook-native** | Re-running a cell replaces its slide; fonts are sent once (~80% smaller notebooks); identical content gives identical HTML |
| **Share anywhere** | Single-file offline HTML, student copies, presentation mode (keyboard, fullscreen, notes), PDF |
| **Content as data** | Every component maps to JSON; `deck.save()` and `LectureDeck.from_file()` round-trip; a CLI validates and exports |
| **Extensible** | Add components, themes and languages; distribute components as plugins via entry points |
| **Safe and dependency-free** | Text is escaped by default; the core needs only the standard library; typed and tested |

## Arabic quick start — بداية سريعة

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="الذكاء الاصطناعي", series="AI SERIES", lesson="01")
deck.cover("من البيانات إلى القرار", "نفهم الفكرة من مثال واضح.\nثم نجرّب ونفسّر النتيجة.",
           tags=["افهم", "توقّع", "جرّب"])
deck.slide("الفكرة الأساسية", cards=[
    {"title": "نفهم", "explanation": "نربط المفهوم بخبرة الطالب السابقة."},
    {"title": "نطبّق", "code": "print('Hello')"},
], activity={"question": "ما الناتج المتوقع؟", "answer": "تظهر كلمة Hello؛ اشرح لماذا قبل التنفيذ."})
deck.quiz("ما ناتج `len('AI')`؟", ["1", "2", "3"], answer=1)
deck.export("lecture.html")
```

اللغة الافتراضية العربية واتجاه الكتابة من اليمين. الخط Cairo للنص وJetBrains Mono للكود مضمّنان ويعملان دون اتصال. إعادة تشغيل الخلية تستبدل شريحتها بدل تكرارها. للنسخة الإنجليزية: `locale="en"`. الدليل العربي الكامل مرفق مع الحزمة: `jupyter-lecture-studio docs`.

## Command line

```bash
jupyter-lecture-studio init my-lecture --course "Artificial Intelligence" --locale en
jupyter-lecture-studio validate my-lecture/lecture.json
jupyter-lecture-studio export my-lecture/lecture.json lecture.html --student
jupyter-lecture-studio export my-lecture/lecture.json slides.html --present
jupyter-lecture-studio docs
```

## Extras

| Extra | Adds |
|---|---|
| `notebook` | IPython display in Jupyter |
| `highlight` | Pygments syntax colors for SQL, Java, C++, JavaScript and hundreds more (Python is built in) |
| `pdf` | Offline PDF export with Chromium (`jupyter-lecture-studio setup-pdf`) |

## Documentation

The complete English and Arabic documentation — components, themes, languages, presenting, JSON, API reference, extending and migration — ships with the package and works offline:

```bash
jupyter-lecture-studio docs
```

## Compatibility

Python 3.10+. Verified in JupyterLab 4 and modern browsers. `from lecture_studio import ...`, the `lecture-studio` command and the `LuxurySlideDeck` bridge keep working. Upgrading from 0.x keeps the gold design identical; HTML class names now use the `ls-` prefix (see the migration guide).

## License

Library code is **MIT**. Bundled Cairo and JetBrains Mono fonts are **SIL Open Font License 1.1**; documentation assets retain their upstream notices. See `THIRD_PARTY_NOTICES.md`.

Maintained by [aoos101](https://pypi.org/user/aoos101/) · [PyPI project](https://pypi.org/project/jupyter-lecture-studio/) · Contributions welcome: see `CONTRIBUTING.md`.

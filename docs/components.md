# Components

Every component is a method on `LectureDeck`, a model class you can pass to `deck.add(...)`, and a JSON `"type"`. All of them accept `notes="..."` (speaker notes, shown only in presentation mode), `id="..."` (replace instead of append) and `show=False` (return HTML instead of displaying it).

| Method | JSON `type` | Use it for |
|---|---|---|
| `cover` | `cover` | Lecture title page with tags, section cards and a code emblem |
| `agenda` / `recap` | `agenda` | Learning goals at the start, key takeaways at the end |
| `slide` | `slide` | A numbered concept: explanation cards, diagram and a predict-then-reveal activity |
| `code` | `code` | Code with its expected output, highlighted lines and line numbers |
| `trace` | `trace` | Step through code line by line with variables and output |
| `compare` | `compare` | A common mistake next to the better approach, or before/after |
| `quiz` | `quiz` | Multiple choice that marks the chosen answer right or wrong |
| `exercise` | `exercise` | A practice task with progressive hints and a hidden solution |
| `callout` | `callout` | Tip, warning, common mistake, key idea, info or success |
| `figure` | `figure` | An image, embedded so the lecture stays self-contained |
| `divider` | `divider` | A section break between parts of a long lecture |
| `note` | `note` | A light reading panel |
| `table` | `table` | A comparison table |

Interactive parts (quiz choices, trace steps, reveals and hints) use native form controls and `<details>`, so they work in notebooks, exported HTML and offline, with no JavaScript.

Formulas, arrays, matrices, charts, neural networks, trees, graphs, memory diagrams and database schemas have their own page: [Formulas and subject visuals](visuals.md).

## Text formatting

Plain strings are escaped, so they can never inject HTML. Three pieces of lightweight markup are applied on top:

- `` `code` `` becomes inline code, isolated left-to-right inside Arabic text;
- `**bold**` becomes strong text (`a**2` and `**kwargs` stay untouched);
- `$x^2 + 1$` becomes an inline formula ([LaTeX subset](visuals.md)); prices such as `$5 to $10` stay text and `\$` is a literal dollar sign.

In right-to-left lectures, terms such as `C++` and `C#` are isolated automatically so their symbols stay on the correct side. Pass `markup="text"` to the deck to turn markup off. For trusted HTML you wrote yourself, use `RichText("<em>...</em>")` (JSON: `{"html": "..."}`).

## Cover

```python
deck.cover(
    "Loops and iteration",
    "Repeat work without repeating code.\nTrace every pass and explain the result.",
    kicker="Lecture three", tags=["Understand", "Trace", "Practice"],
    sections=[{"title": "01 / for loops", "description": "Walk through a list"},
              {"title": "02 / Accumulators", "description": "Build a running total"}],
    hero_code=">>> for x in [1, 2]:\n...     print(x)", hero_result="1  2",
)
```

Omit `hero_code` and `hero_result` for a text-only cover. Two sections keep the two-column layout; other counts adapt. Inside a trusted description, `<span class="cover-prerequisite">` styles a secondary line.

## Agenda and recap

```python
deck.agenda(["Write a `for` loop over a list", "Trace an **accumulator** step by step"])
deck.recap(["Initialise before the loop", "Trace variables to explain output"])
```

## Slide

```python
deck.slide(
    "A running total", "The loop repeats one line for every item.",
    cards=[{"title": "The idea", "explanation": "Start with `total = 0`.", "code": "total += grade",
            "reason": "Initialise before the loop, not inside it."}],
    diagram="loop",
    activity={"question": "What does the program print?", "answer": "80.0, the average."},
)
```

A card accepts `title`, `explanation`, `code`, `reason` and `language`. A diagram accepts `title`, `nodes` (`value`, `note`, `selected`), `caption`, `direction`, `arrows` and `kind`, or the name of a Python preset: `journey`, `names`, `cast`, `arithmetic`, `index`, `decision`, `loop`, `list`, `collections`, `function`, `error`. An activity accepts `question`, `answer`, `code`, `language`, `label` and `reveal`. Close and reopen a diagram to replay its animation.

## Code example

```python
deck.code('scores = {"Ali": 88}\nfor name, score in scores.items():\n    print(name, score)',
          title="Iterating a dictionary", output="Ali 88", highlight=[2], line_numbers=True)
```

Code is displayed, never executed. Python, C, C++, Java, C#, JavaScript, TypeScript, Kotlin, Go, Rust, Dart, Swift, SQL, Bash, R, MATLAB, JSON, HTML and CSS are highlighted by the library itself, identically on every computer; other languages use the `highlight` extra (Pygments) or `register_highlighter` ([details](visuals.md)). Unknown languages fall back to escaped plain text.

## Execution trace

```python
deck.trace("total = 0\nfor g in [70, 80]:\n    total += g\nprint(total)", [
    {"line": 1, "variables": {"total": 0}},
    {"line": 3, "variables": {"total": 70, "g": 70}},
    {"line": 3, "variables": {"total": 150, "g": 80}},
    {"line": 4, "variables": {"total": 150}, "output": "150", "note": "The loop has finished."},
], title="Trace the loop")
```

Students choose a step (or use the arrow keys once the steps have focus) to see the current line, the variables and the output. Values that are not strings are shown with `repr`. A trace holds up to 60 steps.

## Compare

```python
deck.compare("Resetting inside the loop",
             "for g in grades:\n    total = 0\n    total += g",
             "total = 0\nfor g in grades:\n    total += g",
             before_note="The total restarts every pass.", after_note="Initialise once.")
```

`mode="wrong-right"` (default) labels the sides as a common mistake and a better approach; `mode="before-after"` labels them neutrally. Override either with `before_label` / `after_label`.

## Quiz

```python
deck.quiz("How many times does `for i in range(3)` run?",
          ["Twice", "Three times", "Four times"], answer=1,
          explanation="`range(3)` yields 0, 1 and 2.")
```

`answer` is the option index (from 0) or the option text. Choosing an option shows "Correct" or "Try again"; the reveal shows the answer with its explanation.

## Exercise

```python
deck.exercise("Average grade", "Print the average and the **highest** grade.",
              starter="grades = [72, 91, 85]\n# your solution",
              hints=["Use `sum` and `len`.", "`max` returns the largest item."],
              solution="print(sum(grades) / len(grades))\nprint(max(grades))")
```

## Callout

```python
deck.callout("Do not modify a list while iterating over it.", style="mistake")
```

Styles: `info`, `tip`, `warning`, `mistake`, `success`, `key`. The default title comes from the locale; pass `title=` to change it.

## Figure

```python
deck.figure("images/network.png", caption="A two-layer network", width=720)
```

Local images (PNG, JPEG, GIF, WebP, SVG and AVIF, up to 15 MB) are embedded. `http(s)` URLs are linked and need a connection. In JSON courses, relative paths resolve from the JSON file's folder.

## Divider, note and table

```python
deck.divider("Part two: nested loops", "A loop inside a loop")
deck.note("Remember", "State the assumption.\nTest a boundary case.")
deck.table("Comparison", ["Structure", "Use"], [["list", "Ordered values"], ["dict", "Named fields"]])
```

Every table row must match the number of headers. Wide tables and code scroll inside their containers.

## Answers and student copies

Activity answers, quiz keys and exercise solutions are part of the teacher's HTML. Export a student copy without them:

```python
deck.export("lecture-student.html", include_answers=False)
```

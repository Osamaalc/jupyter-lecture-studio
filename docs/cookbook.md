# Teaching recipes

## An Arabic AI lesson

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="الذكاء الاصطناعي", series="AI SERIES", lesson="03")
deck.cover("البحث في فضاء الحالات", "نمثل المشكلة ثم نتتبع البحث.", tags=["نمذجة", "توقع", "تفسير"])
deck.slide("تتبع القرار", diagram={
    "title": "من السؤال إلى الحل",
    "direction": "rtl",
    "nodes": [{"value": "حالة البداية"}, {"value": "استكشاف"}, {"value": "الهدف", "selected": True}],
})
```

## An English SQL lesson

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Databases", language="sql", direction="ltr", theme="emerald")
deck.slide("Filter rows", cards=[{
    "title": "Passing grades",
    "code": "SELECT name, grade FROM students WHERE grade >= 60;",
    "reason": "The predicate keeps only rows that meet the condition.",
}])
```

SQL is highlighted without extra packages.

## Keep motion optional

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="Algorithms", motion=False)
deck.slide("Focus on the reasoning", diagram="loop")
```

The information remains visible when animation is disabled. Closing and reopening a diagram is available even without animation.

## Reuse an identity across a course

```python
from jupyter_lecture_studio import Brand, LectureDeck, Theme

brand = Brand(course="Software Engineering", series="SOFTWARE SERIES", lesson="04", language="java")
theme = Theme(preset="ocean", direction="ltr", motion=True)
deck = LectureDeck(brand=brand, theme=theme)
```

Create a new deck for each lecture, keeping the same series and theme. Change the lesson label and its content. Reusing the same mutable deck for unrelated lectures would also share slide numbering and export contents.

## Export from a build script

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck.from_file("lecture.json", show=False)
output = deck.export("build/lecture.html", title="My lecture")
print(output)
```

This path needs no IPython. It is useful for preparing student handouts from content kept in JSON.

## One course identity, many lectures

Put the identity in a small module next to your notebooks and import it in every lecture:

```python
# course.py
from jupyter_lecture_studio import LectureDeck, register_theme

register_theme("cs-dept", accent="#7cc4ff", background="#0c1522")

def lecture(number, title_locale="ar"):
    return LectureDeck(course="هياكل البيانات", series="DATA STRUCTURES", lesson=f"{number:02d}",
                       theme="cs-dept", locale=title_locale)
```

```python
from course import lecture
deck = lecture(4)
```

## A programming lesson that students can follow

The sequence *goals → concept → trace → common mistake → quiz → exercise → recap* works for most programming topics:

```python
deck.agenda(["Explain what a dictionary stores", "Iterate over keys and values"])
deck.slide("Key → value", cards=[{"title": "Lookup", "code": "ages['Ali']"}], diagram="collections")
deck.trace("ages = {'Ali': 20}\nages['Sara'] = 22\nprint(len(ages))", [
    {"line": 1, "variables": {"ages": "{'Ali': 20}"}},
    {"line": 2, "variables": {"ages": "{'Ali': 20, 'Sara': 22}"}},
    {"line": 3, "output": "2"},
])
deck.compare("Missing keys", "print(ages['Omar'])", "print(ages.get('Omar', 0))",
             before_note="Raises KeyError.", after_note="Returns a default value.")
deck.quiz("What does `ages.get('Omar')` return?", ["0", "None", "KeyError"], answer=1)
deck.exercise("Count words", "Count how many times each word appears.", hints=["Use `dict.get`."],
              solution="counts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1")
deck.recap(["Keys are unique", "`get` avoids KeyError"])
```

## An AI lesson with figures

```python
deck = LectureDeck(course="Machine Learning", locale="en", theme="paper")
deck.figure("figures/gradient-descent.svg", caption="Each step moves against the gradient")
deck.code("w = w - lr * grad", title="Update rule", output="loss: 0.42 → 0.31", highlight=[1])
deck.callout("A learning rate that is too large makes the loss diverge.", style="warning")
```

## Teacher, student and classroom versions

```python
deck.export("dist/lecture.html")
deck.export("dist/lecture-student.html", include_answers=False)
deck.export("dist/lecture-slides.html", present=True, fragments=True)
deck.export_pdf("dist/lecture-handout.pdf", include_answers=False)   # needs the [pdf] extra
```

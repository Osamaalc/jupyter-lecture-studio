"""A tour of every Lecture Studio component, in Arabic and in English.

    python examples/tour.py            # writes examples/tour-ar.html, tour-en.html and
                                       # tour-ar-slides.html / tour-en-slides.html (presentation mode)
"""
from pathlib import Path

from jupyter_lecture_studio import LectureDeck

HERE = Path(__file__).resolve().parent
LOOP = 'total = 0\nfor grade in [70, 80, 90]:\n    total += grade\nprint(total / 3)'
TRACE_STEPS = [
    {'line': 1, 'variables': {'total': 0}},
    {'line': 2, 'variables': {'total': 0, 'grade': 70}},
    {'line': 3, 'variables': {'total': 70, 'grade': 70}},
    {'line': 3, 'variables': {'total': 150, 'grade': 80}},
    {'line': 3, 'variables': {'total': 240, 'grade': 90}},
    {'line': 4, 'variables': {'total': 240, 'grade': 90}, 'output': '80.0'},
]


def arabic():
    deck = LectureDeck(course='مقرر البرمجة', series='PYTHON SERIES', lesson='03')
    deck.cover('الحلقات والتكرار', 'نكرر العمل دون تكرار الكود.\nنتتبع كل دورة ونفهم ناتجها.',
               kicker='المحاضرة الثالثة', tags=['افهم', 'تتبّع', 'جرّب'],
               sections=[{'title': '01 / for', 'description': 'المرور على عناصر قائمة'},
                         {'title': '02 / المجموع', 'description': 'نمط التجميع المتكرر'}],
               hero_code='>>> for x in [1, 2]:\n...     print(x)', hero_result='1  2', show=False)
    deck.agenda(['تكتب حلقة `for` تمر على قائمة', 'تتبع قيمة **المجموع** في كل دورة', 'تميّز بين `print` و `return`'],
                show=False)
    deck.slide('المجموع ينمو مع كل دورة', 'الحلقة تعيد نفس السطر لكل عنصر في القائمة.',
               cards=[{'title': 'الفكرة', 'explanation': 'نبدأ بـ `total = 0` ثم نضيف كل درجة.', 'code': LOOP,
                       'reason': 'التهيئة قبل الحلقة وليس داخلها.'},
                      {'title': 'لماذا؟', 'explanation': 'بدون حلقة نكتب سطر جمع لكل درجة.'}],
               diagram='loop', activity={'question': 'ماذا يطبع البرنامج؟', 'answer': 'يطبع 80.0 وهو المتوسط.'},
               notes='اسأل الطلاب عن قيمة total بعد الدورة الثانية قبل كشف الإجابة.', show=False)
    deck.trace(LOOP, TRACE_STEPS, title='نتتبع الحلقة سطراً بسطر', show=False)
    deck.compare('إعادة التهيئة داخل الحلقة', 'for grade in grades:\n    total = 0\n    total += grade',
                 'total = 0\nfor grade in grades:\n    total += grade',
                 before_note='المجموع يبدأ من الصفر في كل دورة.', after_note='نهيئ مرة واحدة ثم نجمع.', show=False)
    deck.code('scores = {"Ali": 88, "Sara": 95}\nfor name, score in scores.items():\n    print(name, score)',
              title='المرور على قاموس', output='Ali 88\nSara 95', highlight=[2], line_numbers=True, show=False)
    deck.callout('لا تعدّل القائمة أثناء المرور عليها؛ أنشئ قائمة جديدة بدلاً من ذلك.', style='warning', show=False)
    deck.callout('الحلقة `for` في بايثون تمر على العناصر مباشرة، بخلاف C++ التي تبدأ بعدّاد.', style='key', show=False)
    deck.quiz('كم مرة ينفذ جسم الحلقة `for i in range(3)`؟', ['مرتين', 'ثلاث مرات', 'أربع مرات', 'مرة واحدة'], 1,
              explanation='`range(3)` ينتج 0 و1 و2.', show=False)
    deck.exercise('متوسط الدرجات', 'اكتب برنامجاً يحسب متوسط الدرجات ويطبع **أعلى** درجة.',
                  starter='grades = [72, 91, 85]\n# اكتب الحل هنا',
                  hints=['استخدم `sum` و `len`.', 'الدالة `max` تعيد أكبر عنصر.'],
                  solution='print(sum(grades) / len(grades))\nprint(max(grades))', show=False)
    deck.divider('الجزء الثاني: الحلقات المتداخلة', 'حلقة داخل حلقة', show=False)
    deck.recap(['التهيئة قبل الحلقة', 'نتتبع المتغيرات لنفهم الناتج', 'نختار `for` عند معرفة العناصر'], show=False)
    return deck


def english():
    deck = LectureDeck(course='Introduction to Programming', series='CS 101', lesson='03', locale='en', theme='paper')
    deck.cover('Loops and iteration', 'Repeat work without repeating code.\nTrace every pass and explain the result.',
               kicker='Lecture three', tags=['Understand', 'Trace', 'Practice'],
               sections=[{'title': '01 / for loops', 'description': 'Walk through a list'},
                         {'title': '02 / Accumulators', 'description': 'Build a running total'}],
               hero_code='>>> for x in [1, 2]:\n...     print(x)', hero_result='1  2', show=False)
    deck.agenda(['Write a `for` loop over a list', 'Trace an **accumulator** step by step', 'Tell `print` from `return`'],
                show=False)
    deck.slide('A running total', 'The loop repeats one line for every item in the list.',
               cards=[{'title': 'The idea', 'explanation': 'Start with `total = 0`, then add each grade.', 'code': LOOP,
                       'reason': 'Initialise before the loop, not inside it.'},
                      {'title': 'Why?', 'explanation': 'Without a loop you would write one line per grade.'}],
               diagram={'title': 'Total after each pass', 'nodes': [{'value': '0', 'note': 'start'},
                                                                    {'value': '70', 'note': '+ 70'},
                                                                    {'value': '150', 'note': '+ 80'},
                                                                    {'value': '240', 'note': '+ 90', 'selected': True}]},
               activity={'question': 'What does the program print?', 'answer': 'It prints 80.0, the average.'},
               notes='Ask for the value of total after the second pass before revealing.', show=False)
    deck.trace(LOOP, TRACE_STEPS, title='Trace the loop line by line', show=False)
    deck.compare('Resetting inside the loop', 'for grade in grades:\n    total = 0\n    total += grade',
                 'total = 0\nfor grade in grades:\n    total += grade',
                 before_note='The total restarts at zero on every pass.', after_note='Initialise once, then add.', show=False)
    deck.quiz('How many times does the body of `for i in range(3)` run?', ['Twice', 'Three times', 'Four times', 'Once'], 1,
              explanation='`range(3)` yields 0, 1 and 2.', show=False)
    deck.callout('Do not modify a list while iterating over it; build a new list instead.', style='mistake', show=False)
    deck.recap(['Initialise before the loop', 'Trace variables to explain output', 'Use `for` when the items are known'],
               show=False)
    return deck


if __name__ == '__main__':
    print(arabic().export(HERE / 'tour-ar.html'))
    print(arabic().export(HERE / 'tour-ar-slides.html', present=True))
    print(english().export(HERE / 'tour-en.html'))
    print(english().export(HERE / 'tour-en-slides.html', present=True, fragments=True))

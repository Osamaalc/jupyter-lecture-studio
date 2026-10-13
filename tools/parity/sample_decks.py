"""Representative lectures for visual-parity checks between library versions.

Only the public API shared by every supported version is used here, so the
same script can render a reference build and the working tree side by side:

    PYTHONPATH=<reference>/src python tools/parity/sample_decks.py out/before
    PYTHONPATH=src python tools/parity/sample_decks.py out/after
"""
from pathlib import Path
import sys

from lecture_studio import LectureDeck, RichText, diagram_names

PY_CODE = 'scores = [70, 80, 90]\nfor s in scores:\n    print(s * 2)  # double\nname = "Ali"'
SQL_CODE = "SELECT name, grade\nFROM students\nWHERE grade >= 80;"


def fill(deck, rtl=True):
    """Exercise every component variant that a lecture can contain."""
    def t(ar, en):
        return ar if rtl else en
    deck.cover(
        t('أساسيات بايثون', 'Python foundations'),
        t('من أول سطر كود إلى برنامج متكامل.\nنفهم الفكرة ثم نجربها.', 'From the first line to a full program.\nUnderstand, then try.'),
        kicker=t('المحاضرة الأولى', 'Lecture one'), tags=[t('افهم', 'Understand'), t('جرّب', 'Try'), t('فسّر', 'Explain')],
        sections=[{'title': t('01 / نفهم اللغة', '01 / The language'), 'description': t('المتغيرات والشروط', 'Variables and conditions')},
                  {'title': t('02 / نبني البرنامج', '02 / The program'), 'description': t('الدوال والملفات', 'Functions and files')}],
        hero_code='>>> value = 10\n>>> print(value)', hero_result='10', footer_label='PYTHON / FOUNDATIONS', show=False)
    deck.cover(t('غلاف بدون بطاقة', 'Cover without hero'), t('وصف قصير.', 'Short description.'),
               sections=[{'title': 'A'}, {'title': 'B'}, {'title': 'C'}], show=False)
    deck.slide(t('الاسم والقيمة', 'Names and values'), t('الاسم يرتبط بكائن.', 'A name refers to an object.'),
               subtitle=t('عنوان فرعي', 'A subtitle'),
               cards=[{'title': t('إسناد', 'Assign'), 'explanation': t('النوع خاص بالكائن.', 'Type belongs to the object.'), 'code': PY_CODE,
                       'reason': t('الاسم مرجع فقط.', 'A name is only a reference.')},
                      {'title': t('تفسير', 'Explain'), 'explanation': RichText(t('نستخدم <code>type()</code> للتحقق.', 'Use <code>type()</code> to check.'))}],
               diagram='names',
               activity={'question': t('ماذا يظهر؟', 'What is printed?'), 'answer': t('النتيجة 140.', 'It prints 140.'), 'code': 'print(70 * 2)'},
               show=False)
    deck.slide(t('بطاقة واحدة', 'One card'), cards=[{'title': 'SQL', 'code': SQL_CODE, 'language': 'sql'}], show=False)
    deck.slide(t('ثلاث بطاقات', 'Three cards'), cards=[{'title': str(i), 'explanation': t('شرح', 'Text')} for i in range(3)],
               diagram={'title': t('مسار', 'Path'), 'direction': 'rtl' if rtl else 'ltr', 'caption': t('تعليق', 'Caption'),
                        'nodes': [{'value': 'SQL', 'note': t('اكتب', 'Write')}, {'value': 'Plan', 'note': t('خطط', 'Plan')},
                                  {'value': 'Rows', 'note': t('النتيجة', 'Result'), 'selected': True}]}, show=False)
    for name in diagram_names():
        deck.slide(name, cards=[{'title': name, 'explanation': name}] * (4 if name == 'journey' else 1), diagram=name, show=False)
    deck.note(t('ملاحظة', 'Note'), RichText(t('<strong>مهم:</strong> نص <code>x</code>.', '<strong>Important:</strong> text <code>x</code>.')), show=False)
    deck.table(t('مقارنة', 'Comparison'), ['list', 'tuple'], [[t('متغيرة', 'Mutable'), t('ثابتة', 'Immutable')], ['[]', '()']], show=False)
    return deck


SCENARIOS = {
    'gold-rtl': lambda: fill(LectureDeck(course='مقرر الذكاء الاصطناعي', series='THE PYTHON SERIES', lesson='01')),
    'gold-ltr': lambda: fill(LectureDeck(course='Artificial Intelligence', series='PYTHON SERIES', lesson='01', direction='ltr'), rtl=False),
    'ocean-ltr': lambda: fill(LectureDeck(course='Databases', series='DATA LAB', theme='ocean', direction='ltr'), rtl=False),
    'emerald-rtl': lambda: fill(LectureDeck(course='قواعد البيانات', series='DATA LAB', theme='emerald')),
    'accent-rtl': lambda: fill(LectureDeck(course='مادة', theme='gold', accent='#f2a2c4', background='#1b1020')),
    'static-rtl': lambda: fill(LectureDeck(course='مادة', motion=False)),
}


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, build in SCENARIOS.items():
        build().export(out / f'{name}.html', title=name)
    print(out.resolve())


if __name__ == '__main__':
    main(sys.argv[1])

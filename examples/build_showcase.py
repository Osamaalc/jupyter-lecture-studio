"""Build offline example pages using only the public API."""
from pathlib import Path

from lecture_studio import LectureDeck

ROOT = Path(__file__).resolve().parent


def build():
    gold = LectureDeck(course='Lecture Studio · مكتبة المحاضرات', series='DESIGN SYSTEM', lesson='دليل المكونات')
    parts = [gold.cover('مادة واحدة. هوية متكاملة.', 'التصميم نفسه يخدم جميع موادك.\nغيّر المحتوى والهوية، واحتفظ بتجربة تعلم واضحة.', tags=['قابل لإعادة الاستخدام', 'ديناميكي', 'سهل الاستخدام'], sections=[{'title': 'اكتب المحتوى', 'description': 'غلاف وشرح ورسومات وأسئلة'}, {'title': 'اختر الهوية', 'description': 'ألوان واتجاه وحركة حسب المادة'}], hero_code='content → design → learning', hero_result='Ready to teach', hero_label='LECTURE STUDIO', show=False)]
    for theme, course, language, code in [
        ('gold', 'البرمجة · Gold', 'python', 'name = "Lecture Studio"\nprint(name)'),
        ('emerald', 'قواعد البيانات · Emerald', 'sql', 'SELECT name, grade\nFROM students\nWHERE grade >= 60;'),
        ('ocean', 'هندسة البرمجيات · Ocean', 'java', 'class Lesson {\n    String title = "Design";\n}')
    ]:
        deck = LectureDeck(course=course, series=theme.upper() + ' SERIES', lesson='01', theme=theme, language=language)
        parts.append(deck.slide('محتوى مختلف، تجربة متسقة', 'الهوية والكود يتغيران حسب المادة، والبطاقات تظل واضحة ومنظمة.', cards=[{'title': 'الفكرة', 'explanation': 'تكتب المحتوى مرة واحدة؛ المكتبة تتولى الهوامش والتنسيق والحركة.'}, {'title': 'تطبيق', 'code': code, 'reason': 'الأمثلة قابلة للتبديل دون كتابة تصميم جديد.'}], show=False))
    parts.append(gold.slide('من المفهوم إلى التطبيق', diagram={'title': 'خطوات التعلم', 'direction': 'rtl', 'nodes': [{'value': 'افهم', 'note': 'مفهوم واضح'}, {'value': 'توقّع', 'note': 'فكر قبل التنفيذ'}, {'value': 'جرّب', 'note': 'اختبر الفرضية', 'selected': True}, {'value': 'فسّر', 'note': 'اربط السبب بالنتيجة'}], 'caption': 'أغلق المشهد ثم افتحه لإعادة الحركة.'}, activity={'question': 'كيف تتحقق من فهم الطالب؟', 'answer': 'اطلب منه تغيير المثال وتفسير النتيجة، ثم تطبيق الفكرة في حالة جديدة.'}, show=False))
    parts.append(gold.table('المكونات المتاحة', ['المكون', 'استخدامه'], [['cover', 'غلاف المادة والمحاضرة'], ['slide', 'شرح مع بطاقات وكود'], ['diagram', 'رسم تدفق ديناميكي'], ['activity', 'توقّع وإجابة مخفية'], ['note / table', 'ملخص ومقارنة']], show=False))
    parts.append(gold.note('ابدأ بأوامر قصيرة', 'أنشئ LectureDeck ثم اكتب deck.cover وdeck.slide.\nكل التفاصيل موجودة في دليل الاستخدام العربي.', show=False))
    page = '<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lecture Studio · معرض المكونات</title><style>body{background:#e9e9e5;margin:0;padding:24px}@media(max-width:600px){body{padding:8px}}</style></head><body>' + ''.join(parts) + '</body></html>'
    (ROOT / 'showcase.html').write_text(page, encoding='utf-8')
    for filename in ('python_foundations', 'database'):
        LectureDeck.from_file(ROOT / (filename + '.json'), show=False).export(ROOT / (filename + '.html'))


if __name__ == '__main__':
    build()
    print(ROOT / 'showcase.html')

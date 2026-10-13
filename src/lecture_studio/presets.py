"""Python teaching diagrams in Arabic, kept separate from the generic renderer.

Each scene is (title, [(value, note), ...], caption). Pass a scene name as
``diagram=`` on a slide, or call ``preset_diagram(name)`` to customise one.
"""
from .models import Diagram, Node

_SCENES = {
    'journey': (
        'رحلة الفهم',
        [('01', 'افهم المفهوم'), ('02', 'توقّع النتيجة'), ('03', 'جرّب وغيّر'), ('04', 'فسّر وابنِ')],
        'الفهم يكتمل عندما تستطيع تفسير النتيجة، وليس تشغيل الكود فقط.',
    ),
    'names': (
        'الاسم يرتبط بكائن',
        [('x → 10', 'قبل إعادة الإسناد · int'), ('x → "Ali"', 'بعد إعادة الإسناد · str')],
        'إعادة الإسناد تغير ارتباط الاسم؛ لا تغير العدد 10 نفسه.',
    ),
    'cast': (
        'من نص إلى عدد',
        [('"20"', 'مدخل نصي · str'), ('int()', 'تحويل صريح'), ('20', 'قيمة عددية · int')],
        'بعد التحويل نستطيع جمع 1 للحصول على 21؛ النص "abc" لا يصلح لهذا التحويل.',
    ),
    'arithmetic': (
        'الأقواس تغير ترتيب الحساب',
        [('2 + 3 × 4', 'الضرب أولاً'), ('2 + 12', 'ثم الجمع'), ('14', 'النتيجة')],
        'في (2 + 3) × 4 ننفذ ما داخل الأقواس أولاً؛ فتكون النتيجة 20.',
    ),
    'index': (
        'text[1:4] · حد النهاية مستبعد',
        [(c, str(i)) for i, c in enumerate('Python')],
        'نختار الفهارس 1 و2 و3 فقط؛ الناتج yth. موضع 4 لا يدخل في النتيجة.',
    ),
    'decision': (
        'نتتبع الدرجة 88',
        [('88 ≥ 90', 'False · تجاوز الفرع'), ('88 ≥ 80', 'True · نفذ هذا الفرع'), ('جيد جداً', 'توقف عن فحص بقية الفروع')],
        'ابدأ بالأعلى؛ ترتيب الشروط جزء من صحة الحل.',
    ),
    'loop': (
        'المجموع ينمو مع كل دورة',
        [('0', 'تهيئة قبل الحلقة'), ('10', 'أضف 10'), ('30', 'أضف 20'), ('60', 'أضف 30')],
        'كل دورة تستخدم المجموع السابق. لا تعِد تهيئته داخل الحلقة.',
    ),
    'list': (
        'grades[1] = 85',
        [('70', 'الفهرس 0'), ('80 → 85', 'الفهرس 1 · تعديل'), ('90', 'الفهرس 2')],
        'نغير عنصراً واحداً؛ القائمة نفسها تبقى قابلة للتعديل.',
    ),
    'collections': (
        'شكل البيانات يحدد الاختيار',
        [('[]', 'list · تسلسل متغير'), ('()', 'tuple · عناصر ثابتة'), ('{key: value}', 'dict · حقول مسماة'), ('set()', 'set · قيم فريدة')],
        'الثبات في tuple يخص إسناد عناصرها؛ وقد تحتوي كائناً قابلاً للتعديل.',
    ),
    'function': (
        'قيمة تدخل ونتيجة تعود',
        [('[70, 80, 90]', 'وسيط للدالة'), ('average()', 'المعالجة داخل الدالة'), ('80.0', 'قيمة معادة إلى المستدعي')],
        'return تسمح بتخزين النتيجة أو استخدامها في قرار. print تعرضها فقط.',
    ),
    'error': (
        'فشل متوقع نعالجه بوضوح',
        [('"abc"', 'مدخل غير رقمي'), ('ValueError', 'فشل التحويل'), ('None', 'نتيجة parse_grade')],
        'نلتقط ValueError المتوقع؛ لا نخفي جميع الأخطاء باستخدام except عامة.',
    ),
}
# Nodes highlighted in each scene (by position).
_SELECTED = {'index': {1, 2, 3}, 'decision': {1}, 'list': {1}}


def preset_diagram(name: str) -> Diagram:
    if name not in _SCENES:
        raise ValueError(f"Unknown diagram {name!r}. Choose: {', '.join(_SCENES)}")
    title, nodes, caption = _SCENES[name]
    selected = _SELECTED.get(name, set())
    return Diagram(title, [Node(value, note, i in selected) for i, (value, note) in enumerate(nodes)],
                   caption=caption, direction='rtl' if name == 'journey' else 'ltr', arrows=name != 'index', kind=name)


def diagram_names() -> tuple[str, ...]:
    return tuple(_SCENES)

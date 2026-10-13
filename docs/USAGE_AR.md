# دليل الاستخدام

## التثبيت

ثبّت الحزمة في بيئة kernel الذي تستخدمه:

```bash
python -m pip install "jupyter-lecture-studio[notebook,highlight]"
```

## تنظيم العمل

ثبّت المكتبة مرة واحدة في بيئة Jupyter. لكل محاضرة أنشئ كائن `LectureDeck` في أول خلية، ثم استدعِ مكوّنًا في كل خلية عرض؛ بذلك يبقى الشرح مقسّمًا ويظهر في فهرس Jupyter.

```python
from jupyter_lecture_studio import LectureDeck

deck = LectureDeck(course="الذكاء الاصطناعي", series="AI SERIES", lesson="03")
```

**إعادة تشغيل خلية تستبدل ما أضافته الخلية نفسها**؛ لا يتكرر المكوّن ولا يتغير الترقيم، والتصدير يتبع الترتيب النهائي. هذا يعمل في JupyterLab وNotebook 7 وVS Code. لاستبدال مكوّن محدد من أي مكان أعطه معرّفًا: `deck.slide(..., id="intro")`. و`deck.clear()` يفرّغ المجموعة.

## اللغة والاتجاه

اللغة الافتراضية العربية واتجاه الكتابة من اليمين. للمواد الإنجليزية:

```python
deck = LectureDeck(course="Data Structures", locale="en")
```

تتغير عندها كل نصوص الواجهة التي تضيفها المكتبة («اكشف الإجابة»، «الفكرة:»، «الناتج»، التذييل...) ويصبح الاتجاه من اليسار. المحتوى نفسه يبقى كما كتبته. التفاصيل وإضافة لغات أخرى في [دليل اللغات](languages.md).

## تنسيق النص

النصوص العادية آمنة دائمًا، ويمكن داخلها:

- `` `print` `` لكود قصير داخل الجملة، ويُعزل من اليسار إلى اليمين تلقائيًا داخل النص العربي؛
- `**مهم**` لخط عريض؛
- `$x^2 + 1$` لمعادلة داخل الجملة (LaTeX). المبالغ مثل «$5 إلى $10» تبقى نصًا، و`\$` علامة دولار عادية.

المصطلحات مثل C++ وC# تُعزل تلقائيًا في النص العربي فلا تنقلب رموزها. لإيقاف هذا التنسيق: `LectureDeck(..., markup="text")`.

## الغلاف

```python
deck.cover(
    "البحث في فضاء الحالات",
    "نحوّل المشكلة إلى حالات وانتقالات.\nنقارن طرق الوصول إلى الحل.",
    kicker="الوحدة الثانية",
    tags=["نمذجة", "استكشاف", "تحليل"],
    sections=[
        {"title": "01 / نفهم", "description": "الحالات والهدف والانتقالات"},
        {"title": "02 / نطبق", "description": "تتبع البحث على رسم بياني"},
    ],
    hero_code="start → explore → goal",
    hero_result="Solution found",
    hero_label="SEARCH LAB",
)
```

`\n` يضع سطرًا جديدًا. البطاقة المتحركة اختيارية: احذف `hero_code` و`hero_result` ليصبح الغلاف نصيًا. `footer_label` يحدد النص الصغير أسفل الغلاف، وأسطر الكود التي تبدأ بـ `>>>` تأخذ لون المؤشر الذهبي.

## أهداف المحاضرة والخلاصة

```python
deck.agenda(["يكتب حلقة `for` تمر على قائمة", "يتتبع **المجموع** في كل دورة"])
deck.recap(["التهيئة قبل الحلقة", "نتتبع المتغيرات لنفهم الناتج"])
```

## شريحة الشرح

```python
deck.slide(
    "استراتيجية البحث",
    "اختيار العقدة التالية يحدد طريقة الاستكشاف.",
    subtitle="مقارنة مبنية على حالة واحدة",
    cards=[
        {"title": "الفكرة", "explanation": "نحتفظ بالعقد التي لم نستكشفها بعد."},
        {"title": "جرّب", "explanation": "غيّر ترتيب العناصر ولاحظ الفرق.",
         "code": "frontier = [start]", "reason": "ترتيب الجبهة يؤثر في مسار البحث."},
    ],
    activity={"question": "ماذا يحدث لو استخدمنا مكدسًا؟", "answer": "يصبح البحث بالعمق أولًا."},
    notes="اسأل الطلاب قبل كشف الإجابة.",
)
```

الكود يُعرض ولا يُنفّذ، ويبقى من اليسار إلى اليمين. لغته الافتراضية هي `language` في الهوية، ولكل بطاقة `language="java"` أو `"cpp"` أو `"sql"`. المكتبة تلوّن بنفسها: Python وC وC++ وJava وC# وJavaScript وTypeScript وKotlin وGo وRust وDart وSwift وSQL وBash وR وMATLAB وJSON وHTML وCSS، دون أي إضافة، وبنفس الشكل على كل جهاز. اللغات الأخرى تحتاج الإضافة `highlight`. التعليقات العربية داخل الكود تظهر متصلة الحروف، والرموز مثل `!=` و`>=` تظهر كما تُكتب.

`notes` ملاحظات للمحاضر؛ تظهر فقط في وضع العرض بالضغط على S، ولا تصل إلى نسخ الطلاب.

## رسم لأي مادة

```python
deck.slide("من السؤال إلى القرار", diagram={
    "title": "مسار التحليل",
    "direction": "rtl",
    "nodes": [
        {"value": "سؤال", "note": "ما المشكلة؟"},
        {"value": "بيانات", "note": "نجمع الأدلة"},
        {"value": "تحليل", "note": "نختبر الفكرة", "selected": True},
    ],
    "caption": "يمكن مراجعة كل خطوة قبل الانتقال إلى التالية.",
})
```

`selected=True` تبرز عقدة، و`arrows=False` يعرض العناصر دون أسهم. اتجاه الرسم مستقل عن اتجاه المادة. لإعادة الحركة أغلق «المشهد التوضيحي» ثم افتحه. رسومات بايثون الجاهزة: `journey`, `names`, `cast`, `arithmetic`, `index`, `decision`, `loop`, `list`, `collections`, `function`, `error`.

## المعادلات ورسومات المواد

رسومات جاهزة للذكاء الاصطناعي والبرمجة وهياكل البيانات وقواعد البيانات والرياضيات. تُرسم داخل الصفحة نفسها (MathML وSVG) دون JavaScript ودون إنترنت، وتأخذ ألوان الثيم، وتبقى نصًا حقيقيًا في PDF. مثال كامل لكل رسم في `examples/subjects.py`، والتفاصيل في [صفحة الرسومات](visuals.md).

```python
# معادلات LaTeX مع شرح الرموز
deck.math(r"\sigma(z) = \frac{1}{1 + e^{-z}}", title="الدالة اللوجستية",
          legend={"z": "المجموع الموزون", r"\sigma": "دالة التنشيط"})

# الذكاء الاصطناعي
deck.network([4, 6, 3], title="شبكة عصبية")
deck.chart({"خسارة التدريب": [0.9, 0.6, 0.4], "خسارة التحقق": [0.95, 0.7, 0.6]},
           labels=["1", "2", "3"], x_label="الحقبة", y_label="الخسارة")
deck.confusion_matrix([[48, 2], [5, 45]], ["قطة", "كلب"])        # تحسب الدقة تلقائيًا
deck.matrix([[1, 0], [2, 3]], name="W", brackets=True)

# البرمجة وهياكل البيانات
deck.array([12, 7, 25, 3], name="nums", pointers={"i": 0, "j": 3}, slice=[1, 3], negative=True)
deck.memory({"global": {"a": "@lst", "b": "@lst"}}, {"lst": [1, 2, 3]})   # "@id" يرسم سهمًا
deck.tree({"value": 8, "children": [{"value": 3}, {"value": 10}]})
deck.graph(["A", "B", "C"], [("A", "B", 4), ("B", "C", 1)], directed=True)

# قواعد البيانات
deck.schema({"students": ["id INT PK", "name TEXT"],
             "grades": ["student_id INT FK -> students.id", "grade REAL"]})
```

| الدالة | ترسم |
|---|---|
| `math` | معادلات LaTeX مع جدول «حيث» للرموز |
| `array` | قائمة بفهارسها، ومؤشرات مثل `i` و`j`، وشريحة `[start:stop]`، وفهارس سالبة |
| `matrix` / `confusion_matrix` | مصفوفة رياضية أو خريطة حرارية أو مصفوفة التباس مع الدقة |
| `chart` | منحنى (`line`) أو أعمدة (`bar`) أو نقاط (`scatter`) |
| `network` | شبكة عصبية؛ الطبقات الكبيرة تُختصر بـ ⋮ مع عددها الحقيقي |
| `tree` / `graph` | شجرة (`None` يترك مكان الابن فارغًا) وgraph بأوزان واتجاهات |
| `memory` | إطارات الاستدعاء ومتغيراتها والكائنات التي تشير إليها: Python وC++ والقوائم المترابطة والاستدعاء الذاتي |
| `schema` | جداول قاعدة البيانات ومفاتيحها والعلاقات بينها |

أي أمر LaTeX غير مدعوم يظهر خطأً واضحًا وقت كتابة المحاضرة، لا أمام الطلاب.

## مثال كود مع ناتجه

```python
deck.code('for name in ["علي", "سارة"]:\n    print(name)', title="المرور على قائمة",
          output="علي\nسارة", highlight=[2], line_numbers=True)
```

`highlight` يبرز أسطرًا، و`line_numbers` يضيف أرقام الأسطر.

## تتبّع التنفيذ سطرًا بسطر

```python
deck.trace("total = 0\nfor g in [70, 80]:\n    total += g\nprint(total)", [
    {"line": 1, "variables": {"total": 0}},
    {"line": 3, "variables": {"total": 70, "g": 70}},
    {"line": 3, "variables": {"total": 150, "g": 80}},
    {"line": 4, "variables": {"total": 150}, "output": "150", "note": "انتهت الحلقة."},
], title="نتتبع الحلقة")
```

يختار الطالب الخطوة فيظهر السطر الحالي وقيم المتغيرات والمخرجات. يعمل دون JavaScript، وبأسهم لوحة المفاتيح.

## الخطأ الشائع والطريقة الصحيحة

```python
deck.compare("إعادة التهيئة داخل الحلقة",
             "for g in grades:\n    total = 0\n    total += g",
             "total = 0\nfor g in grades:\n    total += g",
             before_note="المجموع يبدأ من الصفر في كل دورة.", after_note="نهيئ مرة واحدة ثم نجمع.")
```

`mode="before-after"` لعناوين محايدة (قبل / بعد).

## اختبار فهم

```python
deck.quiz("كم مرة ينفذ جسم الحلقة `for i in range(3)`؟",
          ["مرتين", "ثلاث مرات", "أربع مرات"], answer=1,
          explanation="`range(3)` ينتج 0 و1 و2.")
```

`answer` رقم الخيار بدءًا من الصفر أو نصه. عند اختيار خيار يظهر «إجابة صحيحة» أو «حاول مرة أخرى».

## تمرين بتلميحات وحل

```python
deck.exercise("متوسط الدرجات", "اكتب برنامجًا يحسب المتوسط ويطبع **أعلى** درجة.",
              starter="grades = [72, 91, 85]\n# اكتب الحل هنا",
              hints=["استخدم `sum` و`len`.", "الدالة `max` تعيد أكبر عنصر."],
              solution="print(sum(grades) / len(grades))\nprint(max(grades))")
```

## تنبيهات وأفكار أساسية

```python
deck.callout("لا تعدّل القائمة أثناء المرور عليها.", style="warning")
```

الأنواع: `info` معلومة، `tip` تلميح، `warning` تنبيه، `mistake` خطأ شائع، `success` أحسنت، `key` فكرة أساسية.

## صورة، فاصل، ملاحظة، جدول

```python
deck.figure("images/network.png", caption="شبكة من طبقتين", width=720)
deck.divider("الجزء الثاني: الحلقات المتداخلة", "حلقة داخل حلقة")
deck.note("قاعدة مهمة", "وضّح الافتراضات قبل اختيار الحل.\nاختبر النتيجة بحالة مختلفة.")
deck.table("مقارنة", ["الطريقة", "الفكرة"], [["BFS", "حسب المستوى"], ["DFS", "حسب العمق"]])
```

الصور المحلية تُضمَّن داخل الملف فتعمل دون اتصال (حتى 15 ميجابايت).

## الثيمات

```python
deck = LectureDeck(course="قواعد البيانات", theme="paper")   # فاتح للقاعات المضيئة والطباعة
deck = LectureDeck(course="الشبكات", theme="ocean")          # gold / emerald / ocean / violet / ruby / paper
deck = LectureDeck(course="مادة", accent="#8fd3ff")           # لون تمييز خاص
```

كل لون في التصميم متغير يمكن تعديله: `tokens={"title": "#0b3954"}`. ولهوية الجامعة أو القسم:

```python
from jupyter_lecture_studio import register_theme
register_theme("campus", accent="#2a9df4", background="#0d1726")
```

`motion=False` يعطل الحركة، وإعداد «تقليل الحركة» في النظام يعطلها دائمًا. `notebook_style=True` ينسق الدفتر المحيط في JupyterLab، ويتبع الوضع النهاري أو الليلي لـ JupyterLab تلقائيًا؛ أما الشرائح فتبقى بتصميمها في الوضعين. الخطوط Cairo وJetBrains Mono مضمّنة وتعمل دون اتصال. التفاصيل في [دليل الثيمات](themes.md).

## HTML موثوق

```python
from jupyter_lecture_studio import RichText
deck.slide("تقطيع النص", RichText('الصيغة <code>start:stop:step</code>، والنهاية غير مشمولة.'))
```

`RichText` لا ينقّي HTML؛ استخدمه لما كتبته أنت فقط، لا لمدخلات الطلاب. في JSON يُكتب `{"html": "..."}`.

## ملف محتوى JSON

```python
deck = LectureDeck.from_file("lecture.json")
deck.save("lecture.json")   # والعكس: أي محاضرة إلى JSON
```

```json
{
  "brand": {"course": "اسم المادة", "series": "SERIES", "lesson": "01", "language": "python"},
  "theme": {"preset": "gold"},
  "locale": "ar",
  "components": [
    {"type": "cover", "title": "عنوان المحاضرة", "description": "مقدمة"},
    {"type": "slide", "title": "المفهوم", "cards": [{"title": "تطبيق", "code": "print(1)"}]},
    {"type": "quiz", "question": "ما الناتج؟", "options": ["1", "2"], "answer": 0}
  ]
}
```

كل المكونات متاحة في JSON بالأسماء نفسها. الحقول غير المعروفة تعطي خطأ واضحًا. للتحقق دون تصدير: `jupyter-lecture-studio validate lecture.json`.

## التصدير والعرض

```python
deck.export("lecture.html")                                # نسخة المحاضر مع الإجابات
deck.export("lecture-student.html", include_answers=False)  # نسخة الطلاب: بلا إجابات ولا حلول
deck.export("lecture-slides.html", present=True)            # وضع العرض في القاعة
```

في وضع العرض: الأسهم أو المسافة للتنقل (معكوسة تلقائيًا للعربية)، F ملء الشاشة، S ملاحظات المحاضر. كل شريحة تتكيف مع حجم الشاشة. `fragments=True` يظهر البطاقات واحدة تلو الأخرى. للـ PDF: `deck.export_pdf("lecture.pdf")` بعد تثبيت الإضافة `pdf` ([دليل PDF](pdf.md)).

## حل المشاكل

| المشكلة | الحل |
|---|---|
| `ModuleNotFoundError` | ثبّت المكتبة بواسطة `%pip` داخل kernel الحالي ثم أعد تشغيله. |
| HTML يظهر دون تنسيق | استخدم دفترًا موثوقًا وأعد تنفيذ خلايا العرض. |
| الخط تغيّر إلى خط النظام | مُسحت مخرجات أول خلية التي تحمل الخطوط؛ نفّذ `deck.styles()` مرة واحدة. |
| تكرر المكونات في التصدير | بيئتك لا ترسل معرّف الخلية؛ استخدم `id="..."` أو `deck.clear()` ثم شغّل بالترتيب. |
| لغة برمجة دون تلوين | أكثر من 19 لغة ملوّنة مدمجًا؛ للغات الأخرى ثبّت الإضافة `highlight` أو استخدم `register_highlighter`. |
| معادلة تظهر خطأ | الرسالة تذكر أمر LaTeX غير المدعوم؛ القائمة في [صفحة الرسومات](visuals.md). |
| الاختبار أو التتبّع لا يستجيب | بعض البيئات تحذف عناصر النماذج من المخرجات غير الموثوقة؛ ثق بالدفتر أو استخدم HTML المصدَّر. |

التصميم يستهدف JupyterLab والمتصفحات الحديثة. بعض البيئات السحابية قد تنقّي CSS؛ تحقق منها قبل التدريس. لا تحتاج المكتبة إلى JavaScript إلا في ملفات وضع العرض.

# الانتقال إلى الإصدار 1.0

## ما الذي لا يتغير

- واجهة Python كما هي: `LectureDeck` و`cover` و`slide` و`note` و`table` و`render` و`from_file` و`export` و`export_pdf` بالمعاملات نفسها.
- ملفات JSON القديمة تعمل دون تعديل، وكذلك `LuxurySlideDeck` والاستيرادان `jupyter_lecture_studio` و`lecture_studio` والأمر `lecture-studio`.
- التصميم الذهبي مطابق للأصل: تم التحقق من الأنماط المحسوبة لكل عنصر في ثلاثة عروض شاشة، وعلى محاضرة «أساسيات بايثون» الحقيقية.
- المخرجات المحفوظة في الدفاتر القديمة تبقى كما هي لأنها تحمل تنسيقها معها.

## ما الذي تحسّن تلقائيًا

| قبل | بعد |
|---|---|
| كل شريحة تحمل الخطوط كاملة (~246 كيلوبايت) | الخطوط مرة واحدة في الدفتر؛ الشريحة ~50 كيلوبايت |
| إعادة تشغيل خلية تكرر المكوّن وتزيد الترقيم | إعادة التشغيل تستبدل ما أضافته الخلية في مكانه |
| نصوص عربية ثابتة تظهر في المحاضرات الإنجليزية | نصوص الواجهة تتبع لغة المحاضرة (`locale`) |
| مخرجات تختلف في كل تشغيل | نفس المحتوى يعطي نفس HTML بالضبط |
| الإجابات مكشوفة في ملف HTML | `export(..., include_answers=False)` لنسخة الطلاب |
| `C++` تنقلب داخل النص العربي في التذييل فقط | تُعزل في كل النصوص تلقائيًا |
| تعليقات عربية داخل الكود متقطعة الحروف | خط Cairo احتياطي داخل الكود |
| تخطيط LTR غير منعكس بالكامل | الخصائص المنطقية تعكس التخطيط تلقائيًا |

## تغييرات قد تلاحظها

1. **أسماء الأصناف في HTML (CSS classes):** أصبحت كلها بالبادئة `ls-`. إذا كتبت CSS خاصًا يستهدف الأسماء القديمة فحدّثه، والأفضل استخدام متغيرات التصميم (`tokens`) بدل CSS مباشر.

   | القديم | الجديد |
   |---|---|
   | `luxury-slide-container` / `luxury-cover` | `ls-slide` / `ls-cover` (وكلاهما `ls-frame`) |
   | `luxury-topline`, `luxury-label`, `luxury-wordmark` | `ls-topline`, `ls-course`, `ls-series` |
   | `main-title`, `chapter-eyebrow`, `chapter-watermark` | `ls-title`, `ls-eyebrow`, `ls-watermark` |
   | `slide-description` | `ls-description` |
   | `luxury-steps`, `luxury-step`, `step-number`, `step-explanation`, `reason-text` | `ls-cards`, `ls-card`, `ls-card-number`, `ls-card-text`, `ls-reason` |
   | `luxury-code`, `luxury-code-bar` | `ls-code`, `ls-code-bar` |
   | `concept-stage`, `concept-visual`, `visual-node`, `visual-connector`, `visual-caption` | `ls-stage`, `ls-diagram`, `ls-node`, `ls-arrow`, `ls-caption` |
   | `visual-{kind}` | `data-kind="{kind}"` |
   | `selected`, `single`, `no-hero` | `ls-selected`, `ls-single`, `ls-no-hero` |
   | `lesson-check`, `check-label`, `answer-body` | `ls-activity`, `ls-activity-label`, `ls-answer` |
   | `studio-note`, `studio-table` | `ls-note`, `ls-table` |
   | `keyword`, `string`, `number`, `comment`, `built_in` | `k`, `s`, `m`, `c`, `nb` (أسماء Pygments) |

   الصنف `cover-prerequisite` داخل وصف الغلاف ما زال مدعومًا، وكذلك أصناف `notebook_style` في خلايا Markdown.

2. **القيم الافتراضية:** `Brand.course` و`Brand.series` و`Brand.footer` و`Activity.label` و`Activity.reveal` أصبحت `None`، وتأخذ قيمتها من اللغة عند العرض. النتيجة المرئية في المحاضرات العربية لم تتغير.

3. **`Theme.direction`** أصبح `None` افتراضيًا ويتبع اللغة. `direction="ltr"` ما زال يعمل ويجعل اللغة الإنجليزية افتراضية.

4. **تنسيق خفيف داخل النص:** النص بين علامتي `` ` `` يصبح كودًا، و`**...**` خطًا عريضًا. إذا احتجت هذه الرموز حرفيًا استخدم `LectureDeck(..., markup="text")`.

5. **`deck._components`** خاصية داخلية تعيد الآن HTML مُعادًا توليده؛ استخدم `deck.components` (النماذج) أو `deck.html()`.

6. حُذف `tokens.css`؛ كل الأنماط في `studio.css` المبني على المتغيرات.

## استخدام جسر التوافق للمحاضرات الأقدم

```python
from jupyter_lecture_studio.compat import LuxurySlideDeck
from jupyter_lecture_studio import Brand

deck = LuxurySlideDeck(brand=Brand(
    course="المادة الجديدة", series="NEW SERIES", lesson="01", language="java"
))
# deck.show(lecture_slides["variables"])
```

| القديم | الجديد |
|---|---|
| `LuxurySlideDeck()` | `LectureDeck(course=...)` |
| `deck.show(data)` | `deck.slide(...)` أو `deck.render(data)` |
| `steps_data` / `code_snippet` | `cards` / `code` |
| `visual` / `checkpoint` | `diagram` / `activity` |
| HTML داخل النص | `RichText(...)` أو `` `code` `` و`**bold**` |

## خطوات الترقية

1. `python -m pip install -U "jupyter-lecture-studio[notebook,highlight]"`
2. أعد تشغيل kernel.
3. شغّل خلايا المحاضرة بالترتيب، ثم صدّر من جديد.

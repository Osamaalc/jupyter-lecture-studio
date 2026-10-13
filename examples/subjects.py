"""Subject visuals for AI, programming, data structures, databases and maths.

    python examples/subjects.py        # writes examples/subjects-ar.html and subjects-en.html
"""
from pathlib import Path

from jupyter_lecture_studio import LectureDeck

HERE = Path(__file__).resolve().parent


def build(locale: str) -> LectureDeck:
    ar = locale == 'ar'

    def t(arabic: str, english: str) -> str:
        return arabic if ar else english

    deck = LectureDeck(course=t('مقرر الذكاء الاصطناعي', 'Artificial Intelligence'), series='VISUAL TOOLKIT',
                       lesson='04', locale=locale, theme='gold' if ar else 'paper')

    # Mathematics and machine learning
    deck.math([r'\sigma(z) = \frac{1}{1 + e^{-z}}', r'\theta \gets \theta - \eta \, \nabla_\theta J(\theta)'],
              title=t('التنشيط وتحديث الأوزان', 'Activation and the update rule'),
              legend={'z': t('المجموع الموزون', 'weighted sum'), r'\eta': t('معدل التعلم', 'learning rate'),
                      r'J(\theta)': t('دالة الخسارة', 'loss function')},
              description=t('نحسب $z = w^T x + b$ ثم نطبق الدالة اللوجستية.', 'We compute $z = w^T x + b$, then apply the logistic function.'),
              show=False)
    deck.math(r'L = -\frac{1}{n} \sum_{i=1}^{n} \left[ y_i \log \hat{y}_i + (1 - y_i) \log (1 - \hat{y}_i) \right]',
              title=t('دالة الخسارة: Cross-Entropy', 'Binary cross-entropy'), show=False)
    deck.network([4, 6, 6, 3], title=t('شبكة عصبية بطبقتين مخفيتين', 'A network with two hidden layers'),
                 caption=t('كل خلية متصلة بكل خلايا الطبقة التالية.', 'Every neuron connects to every neuron in the next layer.'),
                 show=False)
    deck.chart({t('خسارة التدريب', 'Training loss'): [0.92, 0.61, 0.44, 0.35, 0.29, 0.26, 0.24, 0.23],
                t('خسارة التحقق', 'Validation loss'): [0.95, 0.66, 0.52, 0.47, 0.45, 0.46, 0.49, 0.53]},
               labels=[str(i) for i in range(1, 9)], title=t('منحنى التعلم: متى يبدأ الـ Overfitting؟', 'Learning curves: when does overfitting start?'),
               x_label=t('الحقبة (Epoch)', 'Epoch'), y_label=t('الخسارة', 'Loss'), show=False)
    deck.chart({'Python': [68, 74], 'C++': [55, 61], 'Java': [49, 52]}, mode='bar', labels=['2024', '2025'],
               title=t('نسبة الاستخدام في المقررات', 'Use in courses (%)'), y_label='%', show=False)
    deck.confusion_matrix([[48, 2, 0], [5, 40, 5], [1, 3, 46]], [t('قطة', 'cat'), t('كلب', 'dog'), t('طائر', 'bird')],
                          title=t('مصفوفة الالتباس لمصنّف الصور', 'Confusion matrix of an image classifier'), show=False)
    deck.matrix([[1, 0, 2], [-1, 3, 1]], name='W', brackets=True, title=t('مصفوفة الأوزان', 'A weight matrix'),
                caption=t('صفوف = خلايا الطبقة التالية، أعمدة = المدخلات.', 'Rows are next-layer neurons, columns are inputs.'),
                show=False)

    # Programming and data structures
    deck.array([12, 7, 25, 3, 18, 9], name='nums', highlight=[2], pointers={'low': 0, 'mid': 2, 'high': 5},
               slice=[1, 4], negative=True, title=t('الفهارس والشرائح في القوائم', 'Indexes and slices'),
               description=t('`nums[1:4]` تأخذ العناصر من 1 حتى 3، والفهرس السالب يعد من النهاية.',
                             '`nums[1:4]` takes items 1 to 3; negative indexes count from the end.'),
               show=False)
    deck.memory({'global': {'scores': '@a', 'alias': '@a', 'n': 3}, 'average(values)': {'values': '@a', 'total': 235}},
                [{'id': 'a', 'type': 'list', 'value': [70, 80, 85]}],
                title=t('الأسماء والكائنات: نسخة أم مرجع؟', 'Names and objects: copy or reference?'),
                caption=t('`alias` و `scores` و `values` تشير كلها إلى القائمة نفسها.',
                          '`alias`, `scores` and `values` all refer to the same list.'),
                show=False)
    deck.memory({'main()': {'head': '@n1'}}, [
        {'id': 'n1', 'type': 'Node', 'value': {'data': 5, 'next': '@n2'}},
        {'id': 'n2', 'type': 'Node', 'value': {'data': 8, 'next': '@n3'}},
        {'id': 'n3', 'type': 'Node', 'value': {'data': 13, 'next': 'nullptr'}}],
        title=t('قائمة مترابطة في C++', 'A linked list in C++'), heap_label='Heap', show=False)
    deck.tree({'value': 8, 'children': [
        {'value': 3, 'children': [{'value': 1}, {'value': 6, 'children': [{'value': 4}, {'value': 7}]}]},
        {'value': 10, 'children': [None, {'value': 14, 'selected': True, 'children': [{'value': 13}, None]}]}]},
        title=t('شجرة بحث ثنائية', 'A binary search tree'),
        caption=t('البحث عن 14: يمين ← يمين.', 'Searching for 14: right, then right.'), show=False)
    deck.graph([{'id': 'A', 'x': 5, 'y': 50}, {'id': 'B', 'x': 35, 'y': 10}, {'id': 'C', 'x': 35, 'y': 90},
                {'id': 'D', 'x': 68, 'y': 50, 'selected': True}, {'id': 'E', 'x': 95, 'y': 50}],
               [('A', 'B', 4), ('A', 'C', 2), ('C', 'B', 1), {'source': 'B', 'target': 'D', 'label': '5', 'selected': True},
                ('C', 'D', 8), ('D', 'E', 3)], directed=True,
               title=t('أقصر مسار (Dijkstra)', "Shortest paths (Dijkstra)"), show=False)

    # Databases
    deck.schema({'students': ['id INT PK', 'name VARCHAR', 'major_id INT FK -> majors.id'],
                 'enrollments': ['student_id INT PK FK -> students.id', 'course_id INT PK FK -> courses.id', 'grade REAL'],
                 'courses': ['id INT PK', 'title VARCHAR', 'credits INT'],
                 'majors': ['id INT PK', 'name VARCHAR UQ']},
                title=t('مخطط قاعدة بيانات التسجيل', 'Registration database schema'), per_row=3, show=False)
    return deck


if __name__ == '__main__':
    print(build('ar').export(HERE / 'subjects-ar.html'))
    print(build('en').export(HERE / 'subjects-en.html'))

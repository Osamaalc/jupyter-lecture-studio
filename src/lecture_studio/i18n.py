"""Interface text and writing direction for each lecture language.

Lecture content always belongs to the author. Locales only supply the small
labels the library adds around it (button captions, panel headings, defaults),
so an English lecture never shows Arabic interface text and vice versa.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import re
from types import MappingProxyType

__all__ = ['Locale', 'available_locales', 'get_locale', 'register_locale']

_AR = {
    'course': 'مختبر التعلم',
    'series': 'LECTURE STUDIO',
    'footer': 'افهم ← توقّع ← جرّب ← فسّر',
    'eyebrow': 'THE CONCEPT',
    'stage': 'المشهد التوضيحي',
    'stage_toggle': 'إغلاق / إعادة العرض',
    'diagram_eyebrow': 'CONCEPT IN MOTION',
    'reason': 'الفكرة:',
    'activity': 'توقّع قبل التنفيذ',
    'reveal': 'اكشف الإجابة وفسّرها',
    'callout.info': 'معلومة',
    'callout.tip': 'تلميح',
    'callout.warning': 'تنبيه',
    'callout.mistake': 'خطأ شائع',
    'callout.success': 'أحسنت',
    'callout.key': 'فكرة أساسية',
    'compare.before': 'قبل',
    'compare.after': 'بعد',
    'compare.wrong': 'خطأ شائع',
    'compare.right': 'الطريقة الصحيحة',
    'code.output': 'الناتج',
    'quiz': 'اختبر فهمك',
    'quiz.reveal': 'اعرض الإجابة الصحيحة',
    'quiz.correct': 'إجابة صحيحة',
    'quiz.incorrect': 'حاول مرة أخرى',
    'quiz.keys': 'أبجدهوزح',
    'trace': 'تتبّع التنفيذ',
    'trace.step': 'الخطوة',
    'trace.line': 'السطر',
    'trace.variables': 'المتغيرات',
    'trace.output': 'المخرجات',
    'exercise': 'تمرين',
    'exercise.hint': 'تلميح',
    'exercise.solution': 'الحل المقترح',
    'agenda.goals': 'أهداف المحاضرة',
    'agenda.recap': 'الخلاصة',
    'figure': 'شكل',
    'divider': 'الجزء',
    'math.where': 'حيث',
    'matrix.actual': 'الفئة الفعلية',
    'matrix.predicted': 'الفئة المتوقعة',
    'matrix.accuracy': 'الدقة',
    'network.input': 'طبقة الإدخال',
    'network.hidden': 'طبقة مخفية',
    'network.output': 'طبقة الإخراج',
    'memory.stack': 'إطارات الاستدعاء',
    'memory.heap': 'الكائنات في الذاكرة',
    'present.previous': 'السابقة',
    'present.next': 'التالية',
    'present.notes': 'ملاحظات المحاضر',
    'present.fullscreen': 'ملء الشاشة',
    'present.help': '← → للتنقل · F ملء الشاشة · S الملاحظات',
}

_EN = {
    'course': 'Learning Lab',
    'series': 'LECTURE STUDIO',
    'footer': 'Understand → Predict → Try → Explain',
    'eyebrow': 'THE CONCEPT',
    'stage': 'Concept scene',
    'stage_toggle': 'Hide / replay',
    'diagram_eyebrow': 'CONCEPT IN MOTION',
    'reason': 'Key idea:',
    'activity': 'Predict before running',
    'reveal': 'Reveal the answer',
    'callout.info': 'Note',
    'callout.tip': 'Tip',
    'callout.warning': 'Warning',
    'callout.mistake': 'Common mistake',
    'callout.success': 'Well done',
    'callout.key': 'Key idea',
    'compare.before': 'Before',
    'compare.after': 'After',
    'compare.wrong': 'Common mistake',
    'compare.right': 'Better approach',
    'code.output': 'Output',
    'quiz': 'Check your understanding',
    'quiz.reveal': 'Show the correct answer',
    'quiz.correct': 'Correct',
    'quiz.incorrect': 'Try again',
    'quiz.keys': 'ABCDEFGH',
    'trace': 'Execution trace',
    'trace.step': 'Step',
    'trace.line': 'Line',
    'trace.variables': 'Variables',
    'trace.output': 'Output',
    'exercise': 'Exercise',
    'exercise.hint': 'Hint',
    'exercise.solution': 'Suggested solution',
    'agenda.goals': 'Learning goals',
    'agenda.recap': 'Key takeaways',
    'figure': 'Figure',
    'divider': 'Part',
    'math.where': 'where',
    'matrix.actual': 'Actual',
    'matrix.predicted': 'Predicted',
    'matrix.accuracy': 'Accuracy',
    'network.input': 'Input layer',
    'network.hidden': 'Hidden layer',
    'network.output': 'Output layer',
    'memory.stack': 'Call frames',
    'memory.heap': 'Objects',
    'present.previous': 'Previous',
    'present.next': 'Next',
    'present.notes': 'Speaker notes',
    'present.fullscreen': 'Fullscreen',
    'present.help': '← → navigate · F fullscreen · S notes',
}

LABEL_KEYS = frozenset(_EN)


@dataclass(frozen=True)
class Locale:
    """A language code, its writing direction and the interface labels."""
    code: str
    direction: str
    labels: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.code, str) or not re.fullmatch(r'[a-z]{2,3}(-[A-Za-z0-9]{2,8})*', self.code):
            raise ValueError('Locale code must look like "ar", "en" or "pt-BR"')
        if self.direction not in ('rtl', 'ltr'):
            raise ValueError('Locale direction must be rtl or ltr')
        missing = LABEL_KEYS - set(self.labels)
        if missing:
            raise ValueError('Locale is missing labels: ' + ', '.join(sorted(missing)))
        if not all(isinstance(v, str) for v in self.labels.values()):
            raise TypeError('Locale labels must be strings')
        object.__setattr__(self, 'labels', MappingProxyType(dict(self.labels)))

    def __getitem__(self, key: str) -> str:
        return self.labels[key]

    def with_labels(self, **overrides: str) -> Locale:
        """Return a copy with some labels replaced (use underscores for dots)."""
        labels = dict(self.labels)
        for key, value in overrides.items():
            name = key if key in labels else key.replace('__', '.')
            if name not in labels:
                raise KeyError(f'Unknown label {key!r}')
            labels[name] = value
        return Locale(self.code, self.direction, labels)


_LOCALES: dict[str, Locale] = {'ar': Locale('ar', 'rtl', _AR), 'en': Locale('en', 'ltr', _EN)}


def register_locale(code: str, labels: Mapping[str, str], *, direction: str = 'ltr', base: str = 'en') -> Locale:
    """Add or replace a locale. Missing labels fall back to ``base``.

    >>> register_locale('fr', {'reveal': 'Voir la réponse'})  # doctest: +ELLIPSIS
    Locale(code='fr', ...)
    """
    unknown = set(labels) - LABEL_KEYS
    if unknown:
        raise KeyError('Unknown labels: ' + ', '.join(sorted(unknown)))
    merged = dict(get_locale(base).labels)
    merged.update(labels)
    locale = Locale(code, direction, merged)
    _LOCALES[code] = locale
    return locale


def get_locale(code: str | Locale) -> Locale:
    if isinstance(code, Locale):
        return code
    try:
        return _LOCALES[code]
    except (KeyError, TypeError):
        raise ValueError(f'Unknown locale {code!r}. Available: {", ".join(_LOCALES)}') from None


def available_locales() -> tuple[str, ...]:
    return tuple(_LOCALES)

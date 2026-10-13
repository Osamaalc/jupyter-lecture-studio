"""Built-in highlighters for the languages taught most often.

Each grammar is a small table of words and patterns scanned left to right, so
lectures look the same on every machine and need no dependency. Output uses
the Pygments short classes (``k`` keyword, ``kt`` type, ``kc`` constant,
``nb`` built-in, ``nc`` class name, ``s`` string, ``m`` number, ``c``
comment, ``cp`` preprocessor, ``nd`` decorator, ``nt`` tag, ``na`` attribute,
``nv`` variable). Code is always escaped; nothing is executed.

Add or replace a language with ``register_highlighter``::

    register_highlighter(['pseudo'], lambda code: my_html(code))
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import html
import re

__all__ = ['Grammar', 'register_highlighter', 'get_highlighter', 'highlighter_names', 'language_label']

Highlighter = Callable[[str], str]


def _words(text: str) -> frozenset[str]:
    return frozenset(text.split())


_DQ = r'"(?:\\.|[^"\\\n])*"?'
_SQ = r"'(?:\\.|[^'\\\n])*'?"
_CHAR = r"'(?:\\[^\n]{1,6}|[^'\\\n])'"
_SLASH_COMMENTS = (r'//[^\n]*', r'/\*[\s\S]*?(?:\*/|\Z)')
_NUMBER = (r"\b0[xX][0-9a-fA-F_']+[uUlLnN]*\b|\b0[bB][01_']+[uUlLnN]*\b"
           r"|(?<![\w.])\d[\d_']*(?:\.\d[\d_']*)?(?:[eE][+-]?\d+)?[uUlLfFdDmMn]*\b"
           r"|(?<![\w.])\.\d+(?:[eE][+-]?\d+)?[fFdD]?\b")
_IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'


@dataclass(frozen=True)
class Grammar:
    """Words and patterns of one language.

    ``first`` and ``extra`` are ``(class, regex)`` pairs tried before
    comments and before numbers respectively. Words in ``declarators`` (such
    as ``class``) mark the next identifier as a class name.
    """
    keywords: frozenset[str]
    types: frozenset[str] = frozenset()
    constants: frozenset[str] = frozenset()
    builtins: frozenset[str] = frozenset()
    comments: tuple[str, ...] = _SLASH_COMMENTS
    strings: tuple[str, ...] = (_DQ, _SQ)
    first: tuple[tuple[str, str], ...] = ()
    extra: tuple[tuple[str, str], ...] = ()
    identifier: str = _IDENTIFIER
    declarators: frozenset[str] = _words('class struct interface enum record trait')
    ignore_case: bool = False

    def compile(self) -> Highlighter:
        rules = ([*self.first] + [('c', p) for p in self.comments] + [('s', p) for p in self.strings]
                 + [*self.extra] + [('m', _NUMBER), ('word', self.identifier)])
        scanner = re.compile('|'.join(f'(?P<g{i}>{pattern})' for i, (_, pattern) in enumerate(rules)), re.M)
        classes = [name for name, _ in rules]
        sets: tuple[tuple[str, frozenset[str]], ...] = (
            ('k', self.keywords), ('kt', self.types), ('kc', self.constants), ('nb', self.builtins))
        if self.ignore_case:
            sets = tuple((name, frozenset(w.upper() for w in words)) for name, words in sets)
            declarators = frozenset(w.upper() for w in self.declarators)
        else:
            declarators = self.declarators

        def render(code: str) -> str:
            parts: list[str] = []
            cursor = 0
            declare = False
            for match in scanner.finditer(code):
                style: str | None = classes[int(match.lastgroup[1:])]  # type: ignore[index]
                value = match.group()
                if style == 'word':
                    key = value.upper() if self.ignore_case else value
                    style = 'nc' if declare else next((name for name, words in sets if key in words), None)
                    declare = key in declarators
                if not style or not value:
                    continue
                parts.append(html.escape(code[cursor:match.start()]))
                parts.append(f'<span class="{style}">{html.escape(value)}</span>')
                cursor = match.end()
            parts.append(html.escape(code[cursor:]))
            return ''.join(parts)
        return render


# --------------------------------------------------------------------------
# Grammars

_C_KEYWORDS = ('break case const continue default do else enum extern for goto if inline register restrict return '
               'sizeof static struct switch typedef union volatile while')
_C_TYPES = ('int char float double long short void unsigned signed bool _Bool size_t FILE '
            'int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t')
_PREPROCESSOR = (('cp', r'^[ \t]*#[ \t]*[a-z]+\b[^\n]*'),)

C = Grammar(
    _words(_C_KEYWORDS), _words(_C_TYPES), _words('NULL true false'),
    _words('printf scanf malloc calloc realloc free strlen strcpy strcmp strcat memcpy memset fopen fclose '
           'fprintf fscanf fgets puts putchar getchar exit assert'),
    strings=(_DQ, _CHAR), first=_PREPROCESSOR)

CPP = Grammar(
    _words(_C_KEYWORDS + ' alignas alignof and asm catch class concept consteval constexpr constinit const_cast '
           'co_await co_return co_yield decltype delete dynamic_cast explicit export final friend mutable namespace '
           'new noexcept not operator or override private protected public reinterpret_cast requires static_assert '
           'static_cast template this thread_local throw try typeid typename using virtual xor auto'),
    _words(_C_TYPES + ' wchar_t char8_t char16_t char32_t string vector map set unordered_map unordered_set '
           'pair array deque list queue stack priority_queue shared_ptr unique_ptr'),
    _words('true false nullptr NULL'),
    _words('std cout cin cerr endl printf scanf getline make_pair make_shared make_unique sort swap max min'),
    strings=(r'(?:u8|[uUL])?' + _DQ, _CHAR), first=_PREPROCESSOR)

JAVA = Grammar(
    _words('abstract assert break case catch class continue default do else enum extends final finally for if '
           'implements import instanceof interface native new package private protected public return static '
           'strictfp super switch synchronized this throw throws transient try volatile while var record yield '
           'sealed permits'),
    _words('boolean byte char double float int long short void String Integer Double Boolean Character Long '
           'Object List ArrayList Map HashMap Set HashSet Scanner StringBuilder'),
    _words('true false null'),
    _words('System Math Arrays Collections Objects Optional Thread'),
    strings=(r'"""[\s\S]*?(?:"""|\Z)', _DQ, _CHAR), extra=(('nd', r'@[A-Za-z_]\w*'),))

CSHARP = Grammar(
    _words('abstract as base break case catch checked class const continue default delegate do else enum event '
           'explicit extern finally fixed for foreach goto if implicit in interface internal is lock namespace new '
           'operator out override params private protected public readonly ref return sealed sizeof stackalloc '
           'static struct switch this throw try typeof unchecked unsafe using virtual volatile while async await '
           'var get set init record yield when where partial'),
    _words('bool byte char decimal double float int long object sbyte short string uint ulong ushort void dynamic '
           'List Dictionary String Int32 Task'),
    _words('true false null'),
    _words('Console Math Convert Array Enumerable'),
    strings=(r'\$?@"(?:""|[^"])*"?', r'\$?' + _DQ, _CHAR), first=(('cp', r'^[ \t]*#[ \t]*[a-z]+\b[^\n]*'),))

_JS_KEYWORDS = ('async await break case catch class const continue debugger default delete do else export extends '
                'finally for from function if import in instanceof let new of return static super switch this '
                'throw try typeof var void while with yield get set')
_JS_BUILTINS = ('console document window Math JSON Array Object String Number Boolean Promise Map Set Date RegExp '
                'Error parseInt parseFloat setTimeout setInterval fetch require module exports alert')
_TEMPLATE = r'`(?:\\[\s\S]|[^`\\])*`?'

JAVASCRIPT = Grammar(
    _words(_JS_KEYWORDS), frozenset(), _words('true false null undefined NaN Infinity'), _words(_JS_BUILTINS),
    strings=(_TEMPLATE, _DQ, _SQ), identifier=r'[A-Za-z_$][\w$]*')

TYPESCRIPT = Grammar(
    _words(_JS_KEYWORDS + ' interface type enum implements declare namespace abstract private protected public '
           'readonly as keyof infer is satisfies'),
    _words('string number boolean any unknown never object bigint symbol'),
    _words('true false null undefined NaN Infinity'), _words(_JS_BUILTINS),
    strings=(_TEMPLATE, _DQ, _SQ), extra=(('nd', r'@[A-Za-z_]\w*'),), identifier=r'[A-Za-z_$][\w$]*')

KOTLIN = Grammar(
    _words('as break class continue do else for fun if in interface is object package return super this throw '
           'try typealias val var when while by catch constructor finally get import init set where abstract '
           'annotation companion const data enum final infix inline inner internal lateinit open operator out '
           'override private protected public sealed suspend vararg'),
    _words('Int Long Double Float Boolean String Char Byte Short Unit Any Nothing List MutableList Map Array'),
    _words('true false null'),
    _words('println print listOf mutableListOf mapOf mutableMapOf setOf arrayOf readLine'),
    strings=(r'"""[\s\S]*?(?:"""|\Z)', _DQ, _CHAR), extra=(('nd', r'@[A-Za-z_]\w*'),))

GO = Grammar(
    _words('break case chan const continue default defer else fallthrough for func go goto if import interface '
           'map package range return select struct switch type var'),
    _words('bool byte complex64 complex128 error float32 float64 int int8 int16 int32 int64 rune string uint '
           'uint8 uint16 uint32 uint64 uintptr any'),
    _words('true false nil iota'),
    _words('append cap close complex copy delete imag len make new panic print println real recover fmt'),
    strings=(r'`[^`]*`?', _DQ, _CHAR), declarators=frozenset())

RUST = Grammar(
    _words('as async await break const continue crate dyn else enum extern fn for if impl in let loop match mod '
           'move mut pub ref return self Self static struct super trait type unsafe use where while'),
    _words('i8 i16 i32 i64 i128 isize u8 u16 u32 u64 u128 usize f32 f64 bool char str String Vec Option Result '
           'Box HashMap'),
    _words('true false None Some Ok Err'), frozenset(),
    strings=(r'b?' + _DQ, _CHAR), extra=(('nb', r'\b[a-z_]\w*!'), ('nd', r'#!?\[[^\]\n]*\]')))

DART = Grammar(
    _words('abstract as assert async await break case catch class const continue covariant default deferred do '
           'else enum export extends extension external factory final finally for get hide if implements import '
           'in interface is late library mixin new on operator part required rethrow return set show static '
           'super switch sync this throw try typedef var while with yield'),
    _words('int double num String bool List Map Set dynamic Object Future Stream void'),
    _words('true false null'), _words('print'),
    strings=(r"'''[\s\S]*?(?:'''|\Z)", r'"""[\s\S]*?(?:"""|\Z)', _DQ, _SQ), extra=(('nd', r'@[A-Za-z_]\w*'),))

SWIFT = Grammar(
    _words('associatedtype class deinit enum extension fileprivate func import init inout internal let open '
           'operator private protocol public rethrows static struct subscript typealias var break case continue '
           'default defer do else fallthrough for guard if in repeat return switch where while as catch is super '
           'self Self throw throws try await async'),
    _words('Int Double Float String Bool Character Array Dictionary Set Optional Any Void'),
    _words('true false nil'), _words('print'),
    strings=(r'"""[\s\S]*?(?:"""|\Z)', _DQ), extra=(('nd', r'@[A-Za-z_]\w*'),),
    declarators=_words('class struct protocol enum extension'))

SQL = Grammar(
    _words('select from where and or not in is like between join inner left right full outer cross on as group '
           'by order having limit offset distinct insert into values update set delete create table alter drop '
           'index view primary key foreign references unique default check constraint union all exists case when '
           'then else end asc desc begin commit rollback transaction grant revoke database if with recursive '
           'returning trigger procedure function returns declare auto_increment autoincrement cascade add column '
           'rename to use show describe explain truncate over partition row rows fetch next only top any some '
           'intersect except natural using'),
    _words('int integer smallint bigint tinyint decimal numeric float real double precision char varchar nvarchar '
           'text date time timestamp datetime boolean bool blob serial json uuid'),
    _words('true false null'),
    _words('count sum avg min max coalesce nullif cast convert upper lower length substring trim round now '
           'current_date current_timestamp concat ifnull isnull row_number rank dense_rank lag lead abs extract '
           'string_agg group_concat'),
    comments=(r'--[^\n]*', r'/\*[\s\S]*?(?:\*/|\Z)'), strings=(r"'(?:''|[^'])*'?",),
    declarators=frozenset(), ignore_case=True)

BASH = Grammar(
    _words('if then else elif fi for while until do done case esac function in return export local select'),
    frozenset(), _words('true false'),
    _words('echo cd ls pwd mkdir rm cp mv cat grep sed awk sudo pip python python3 git chmod source exit read '
           'printf touch apt brew conda jupyter cut sort uniq head tail wc find curl wget'),
    comments=(r'(?<![\w$#])#[^\n]*',), strings=(r'"(?:\\.|[^"\\])*"?', r"'[^']*'?"),
    extra=(('nv', r'\$(?:\{[^}\n]*\}?|[A-Za-z_]\w*|[0-9#?@*$!-])'),), identifier=r'[A-Za-z_][\w-]*',
    declarators=frozenset())

R = Grammar(
    _words('if else repeat while function for in next break return'),
    frozenset(), _words('TRUE FALSE NULL Inf NaN NA T F'),
    _words('print cat c list library require data.frame matrix vector mean median sum length nrow ncol head '
           'tail summary str paste paste0 seq rep apply sapply lapply plot hist lm read.csv'),
    comments=(r'#[^\n]*',), identifier=r'[A-Za-z_.][\w.]*', declarators=frozenset())

MATLAB = Grammar(
    _words('function end if elseif else for while switch case otherwise break continue return try catch global '
           'persistent'),
    frozenset(), _words('true false pi inf Inf NaN eps'),
    _words('disp fprintf sprintf zeros ones eye rand randn size length numel plot figure hold xlabel ylabel '
           'title legend linspace sum mean max min abs sqrt exp log'),
    comments=(r'%\{[\s\S]*?(?:%\}|\Z)', r'%[^\n]*'),
    strings=(_DQ, r"(?<![\w)\].'])'(?:''|[^'\n])*'?"), declarators=frozenset())

JSON = Grammar(
    frozenset(), frozenset(), _words('true false null'), frozenset(), comments=(),
    strings=(), first=(('nt', r'"(?:\\.|[^"\\\n])*"(?=\s*:)'), ('s', _DQ)),
    extra=(('m', r'-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b'),), declarators=frozenset())


# HTML and CSS depend on context (inside a tag, inside a rule) -------------

_MARKUP = re.compile(r'(?P<c><!--[\s\S]*?(?:-->|\Z))|(?P<d><![^>]*>?)'
                     r'|(?P<open></?)(?P<tag>[A-Za-z][\w:.-]*)(?P<attrs>[^<>]*?)(?P<close>/?>)')
_ATTRIBUTE = re.compile(r'(?P<name>[^\s=/>"\']+)(?:\s*=\s*(?P<value>"[^"]*"?|\'[^\']*\'?|[^\s>"\']+))?')


def _span(style: str, value: str) -> str:
    return f'<span class="{style}">{html.escape(value)}</span>' if value else ''


def highlight_markup(code: str) -> str:
    """HTML and XML: tags, attributes, values and comments."""
    parts: list[str] = []
    cursor = 0
    for match in _MARKUP.finditer(code):
        parts.append(html.escape(code[cursor:match.start()]))
        cursor = match.end()
        if match['c'] is not None or match['d'] is not None:
            parts.append(_span('c' if match['c'] is not None else 'cp', match.group()))
            continue
        attrs, inner, last = match['attrs'], [], 0
        for item in _ATTRIBUTE.finditer(attrs):
            inner.append(html.escape(attrs[last:item.start()]) + _span('na', item['name']))
            if item['value'] is not None:
                inner.append(html.escape(attrs[item.end('name'):item.start('value')]) + _span('s', item['value']))
            last = item.end()
        inner.append(html.escape(attrs[last:]))
        parts.append(html.escape(match['open']) + _span('nt', match['tag']) + ''.join(inner) + html.escape(match['close']))
    parts.append(html.escape(code[cursor:]))
    return ''.join(parts)


_STYLE = re.compile(r'(?P<c>/\*[\s\S]*?(?:\*/|\Z))|(?P<s>"(?:\\.|[^"\\\n])*"?|\'(?:\\.|[^\'\\\n])*\'?)'
                    r'|(?P<brace>[{}])|(?P<at>@[\w-]+)|(?P<important>!important)'
                    r'|(?P<color>#[0-9a-fA-F]{3,8}\b)|(?P<number>(?<![\w-])-?\d*\.?\d+(?:[a-zA-Z]+|%)?)'
                    r'|(?P<prop>[\w-]+(?=\s*:(?!:)))|(?P<selector>[.#][\w-]+|::?[\w-]+)|(?P<word>[\w-]+)')


def highlight_css(code: str) -> str:
    """CSS: selectors outside rules, properties and values inside them."""
    parts: list[str] = []
    cursor = 0
    depth = 0
    for match in _STYLE.finditer(code):
        kind = match.lastgroup
        if kind == 'brace':
            depth = depth + 1 if match.group() == '{' else max(0, depth - 1)
            continue
        if kind == 'prop' and not depth:
            kind = 'word'
        style = {'c': 'c', 's': 's', 'at': 'k', 'important': 'k', 'color': 'm' if depth else 'nc', 'number': 'm', 'prop': 'na',
                 'selector': 'nc' if not depth or match.group()[0] != ':' else None,
                 'word': None if depth else 'nt'}[kind]  # type: ignore[index]
        if not style:
            continue
        parts.append(html.escape(code[cursor:match.start()]))
        parts.append(_span(style, match.group()))
        cursor = match.end()
    parts.append(html.escape(code[cursor:]))
    return ''.join(parts)


# --------------------------------------------------------------------------
# Registry

_HIGHLIGHTERS: dict[str, Highlighter] = {}
_LABELS = {'cpp': 'C++', 'c++': 'C++', 'cxx': 'C++', 'cc': 'C++', 'hpp': 'C++', 'cs': 'C#', 'csharp': 'C#', 'c#': 'C#',
           'js': 'JavaScript', 'javascript': 'JavaScript', 'jsx': 'JSX', 'ts': 'TypeScript', 'typescript': 'TypeScript',
           'tsx': 'TSX', 'sh': 'Bash', 'shell': 'Shell', 'zsh': 'Zsh', 'py': 'Python', 'kt': 'Kotlin', 'rs': 'Rust',
           'golang': 'Go', 'objective-c': 'Objective-C', 'md': 'Markdown', 'yml': 'YAML'}


def register_highlighter(names: Iterable[str], highlighter: Highlighter, *, label: str | None = None,
                         replace: bool = False) -> None:
    """Use ``highlighter(code) -> html`` for these language names.

    The function must escape the code it returns (only ``<span class>``
    markup is expected). ``label`` is shown in the code toolbar.
    """
    if isinstance(names, str):
        names = [names]
    keys = [name.lower() for name in names]
    if not keys or not all(re.fullmatch(r'[a-z0-9#+._-]+', key) for key in keys):
        raise ValueError('Language names must be non-empty identifiers such as "cpp" or "c#"')
    if not callable(highlighter):
        raise TypeError('highlighter must be a function taking code and returning HTML')
    taken = [key for key in keys if key in _HIGHLIGHTERS]
    if taken and not replace:
        raise ValueError(f'A highlighter is already registered for: {", ".join(taken)}')
    for key in keys:
        _HIGHLIGHTERS[key] = highlighter
        if label is not None:
            _LABELS[key] = label


def get_highlighter(language: str) -> Highlighter | None:
    return _HIGHLIGHTERS.get(language.lower())


def highlighter_names() -> tuple[str, ...]:
    return tuple(sorted(_HIGHLIGHTERS))


def language_label(language: str) -> str:
    """The name shown in a code block's toolbar, e.g. ``cpp`` -> ``C++``."""
    return _LABELS.get(language.lower(), language).upper()


for _names, _grammar in (
    (['c', 'h'], C),
    (['cpp', 'c++', 'cxx', 'cc', 'hpp', 'arduino'], CPP),
    (['java'], JAVA),
    (['csharp', 'cs', 'c#'], CSHARP),
    (['javascript', 'js', 'jsx', 'node', 'mjs'], JAVASCRIPT),
    (['typescript', 'ts', 'tsx'], TYPESCRIPT),
    (['kotlin', 'kt'], KOTLIN),
    (['go', 'golang'], GO),
    (['rust', 'rs'], RUST),
    (['dart', 'flutter'], DART),
    (['swift'], SWIFT),
    (['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'plsql', 'tsql'], SQL),
    (['bash', 'sh', 'shell', 'zsh', 'console', 'terminal'], BASH),
    (['r'], R),
    (['matlab', 'octave'], MATLAB),
    (['json', 'jsonc'], JSON),
):
    register_highlighter(_names, _grammar.compile())
register_highlighter(['html', 'xml', 'svg', 'xhtml', 'vue'], highlight_markup)
register_highlighter(['css', 'scss'], highlight_css)

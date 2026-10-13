"""A small LaTeX-to-MathML converter for lecture formulas.

Browsers render MathML natively (Chrome, Edge, Firefox, Safari), so formulas
need no JavaScript, no web fonts and no network, and they export to PDF as
real text. The supported subset covers what courses in AI, statistics and
algorithms usually write: fractions, roots, scripts, sums and integrals with
limits, Greek letters, relations, accents, ``\\mathbf``/``\\mathbb``,
``\\text``, ``\\left``/``\\right`` and matrix environments. Unknown commands
raise ``ValueError`` when the lecture is built, never at display time.

    >>> to_mathml(r'\\frac{1}{1 + e^{-z}}')  # doctest: +ELLIPSIS
    '<math ...><mfrac><mn>1</mn>...</math>'
"""
from __future__ import annotations

import html
import re

__all__ = ['to_mathml', 'MathError']


class MathError(ValueError):
    """The formula uses LaTeX this converter does not support."""


_GREEK = {
    'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ϵ', 'varepsilon': 'ε', 'zeta': 'ζ',
    'eta': 'η', 'theta': 'θ', 'vartheta': 'ϑ', 'iota': 'ι', 'kappa': 'κ', 'lambda': 'λ', 'mu': 'μ', 'nu': 'ν',
    'xi': 'ξ', 'pi': 'π', 'varpi': 'ϖ', 'rho': 'ρ', 'varrho': 'ϱ', 'sigma': 'σ', 'varsigma': 'ς', 'tau': 'τ',
    'upsilon': 'υ', 'phi': 'ϕ', 'varphi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'omega': 'ω', 'ell': 'ℓ',
    'infty': '∞', 'partial': '∂', 'nabla': '∇', 'emptyset': '∅', 'varnothing': '∅', 'hbar': 'ℏ', 'Re': 'ℜ', 'Im': 'ℑ',
}
_UPRIGHT = {'Gamma': 'Γ', 'Delta': 'Δ', 'Theta': 'Θ', 'Lambda': 'Λ', 'Xi': 'Ξ', 'Pi': 'Π', 'Sigma': 'Σ',
            'Upsilon': 'Υ', 'Phi': 'Φ', 'Psi': 'Ψ', 'Omega': 'Ω'}
_OPERATORS = {
    'cdot': '⋅', 'times': '×', 'div': '÷', 'pm': '±', 'mp': '∓', 'ast': '∗', 'star': '⋆', 'circ': '∘', 'bullet': '∙',
    'le': '≤', 'leq': '≤', 'ge': '≥', 'geq': '≥', 'ne': '≠', 'neq': '≠', 'approx': '≈', 'equiv': '≡', 'sim': '∼',
    'simeq': '≃', 'cong': '≅', 'propto': '∝', 'll': '≪', 'gg': '≫', 'in': '∈', 'notin': '∉', 'ni': '∋',
    'subset': '⊂', 'subseteq': '⊆', 'supset': '⊃', 'supseteq': '⊇', 'cup': '∪', 'cap': '∩', 'setminus': '∖',
    'to': '→', 'rightarrow': '→', 'leftarrow': '←', 'gets': '←', 'leftrightarrow': '↔', 'Rightarrow': '⇒',
    'Leftarrow': '⇐', 'Leftrightarrow': '⇔', 'implies': '⟹', 'iff': '⟺', 'mapsto': '↦', 'uparrow': '↑',
    'downarrow': '↓', 'forall': '∀', 'exists': '∃', 'neg': '¬', 'lnot': '¬', 'land': '∧', 'wedge': '∧',
    'lor': '∨', 'vee': '∨', 'oplus': '⊕', 'otimes': '⊗', 'odot': '⊙', 'perp': '⊥', 'parallel': '∥', 'mid': '∣',
    'ldots': '…', 'dots': '…', 'cdots': '⋯', 'vdots': '⋮', 'ddots': '⋱', 'prime': '′', 'colon': ':',
    'langle': '⟨', 'rangle': '⟩', 'lfloor': '⌊', 'rfloor': '⌋', 'lceil': '⌈', 'rceil': '⌉', 'vert': '|',
    'Vert': '‖', '|': '‖', '{': '{', '}': '}', '%': '%', '#': '#', '&': '&', '_': '_', '$': '$',
}
_LARGE = {'sum': '∑', 'prod': '∏', 'coprod': '∐', 'bigcup': '⋃', 'bigcap': '⋂', 'int': '∫', 'iint': '∬',
          'iiint': '∭', 'oint': '∮'}
_INTEGRALS = {'int', 'iint', 'iiint', 'oint'}
_FUNCTIONS = {'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh',
              'log', 'ln', 'lg', 'exp', 'det', 'dim', 'ker', 'deg', 'gcd', 'Pr', 'arg', 'sgn'}
_LIMITS = {'lim', 'max', 'min', 'sup', 'inf', 'argmax', 'argmin', 'limsup', 'liminf'}
# Spacing modifier letters, as MathJax uses: they sit on the base like a TeX accent.
_ACCENTS = {'hat': 'ˆ', 'widehat': 'ˆ', 'check': 'ˇ', 'bar': '¯', 'overline': '¯', 'vec': '→', 'overrightarrow': '→',
            'dot': '˙', 'ddot': '¨', 'tilde': '˜', 'widetilde': '˜'}
# Operator names are upright and spaced like TeX's \mathop.
_NAMED = '<mo{limits} lspace="0.1667em" rspace="0.1667em">{name}</mo>'
_SPACES = {',': '0.1667em', ':': '0.2222em', ';': '0.2778em', ' ': '0.25em', 'quad': '1em', 'qquad': '2em',
           '!': '0', 'enspace': '0.5em'}
_FENCES = {'matrix': ('', ''), 'pmatrix': ('(', ')'), 'bmatrix': ('[', ']'), 'Bmatrix': ('{', '}'),
           'vmatrix': ('|', '|'), 'Vmatrix': ('‖', '‖'), 'cases': ('{', ''), 'aligned': ('', ''),
           'align': ('', ''), 'align*': ('', ''), 'array': ('', ''), 'smallmatrix': ('', '')}
_DELIMITERS = {'(': '(', ')': ')', '[': '[', ']': ']', '|': '|', '.': '', '/': '/', '<': '⟨', '>': '⟩'}

_TOKEN = re.compile(r'\\[A-Za-z]+\*?|\\.|\d+(?:\.\d+)?|\s+|.', re.S)


def _alphabet(text: str, upper: int, lower: int, digits: int | None = None, exceptions=None) -> str:
    """Map ASCII letters to a Unicode mathematical alphabet (bold, double-struck...)."""
    exceptions = exceptions or {}
    out = []
    for char in text:
        if char in exceptions:
            out.append(exceptions[char])
        elif 'A' <= char <= 'Z':
            out.append(chr(upper + ord(char) - 65))
        elif 'a' <= char <= 'z':
            out.append(chr(lower + ord(char) - 97))
        elif digits is not None and char.isdigit():
            out.append(chr(digits + ord(char) - 48))
        else:
            out.append(char)
    return ''.join(out)


_STYLES = {
    'mathbf': lambda t: _alphabet(t, 0x1D400, 0x1D41A, 0x1D7CE),
    'boldsymbol': lambda t: _alphabet(t, 0x1D468, 0x1D482, 0x1D7CE),
    'mathbb': lambda t: _alphabet(t, 0x1D538, 0x1D552, 0x1D7D8, {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ',
                                                               'R': 'ℝ', 'Z': 'ℤ'}),
    'mathcal': lambda t: _alphabet(t, 0x1D49C, 0x1D4B6, None, {'B': 'ℬ', 'E': 'ℰ', 'F': 'ℱ', 'H': 'ℋ', 'I': 'ℐ',
                                                             'L': 'ℒ', 'M': 'ℳ', 'R': 'ℛ', 'e': 'ℯ', 'g': 'ℊ', 'o': 'ℴ'}),
    'mathit': lambda t: t,
}


def _e(text: str) -> str:
    return html.escape(text, quote=False)


class _Parser:
    def __init__(self, source: str):
        self.tokens = _TOKEN.findall(source)
        self.i = 0

    # -- token helpers ------------------------------------------------------
    def _skip_space(self) -> None:
        while self.i < len(self.tokens) and self.tokens[self.i].isspace():
            self.i += 1

    def peek(self) -> str | None:
        self._skip_space()
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def take(self, *, raw: bool = False) -> str:
        if not raw:
            self._skip_space()
        if self.i >= len(self.tokens):
            raise MathError('Formula ends too early (missing argument or closing brace)')
        token = self.tokens[self.i]
        self.i += 1
        return token

    def expect(self, token: str) -> None:
        if self.take() != token:
            raise MathError(f'Expected {token!r} in formula')

    def raw_group(self) -> str:
        """The literal text of a {...} argument, spaces included (\\text, \\begin)."""
        self.expect('{')
        depth, out = 1, list[str]()
        while True:
            token = self.take(raw=True)
            if token == '{':
                depth += 1
            elif token == '}':
                depth -= 1
                if not depth:
                    return ''.join(out)
            out.append(token[1:] if token in ('\\{', '\\}', '\\_', '\\%', '\\&', '\\#', '\\$') else token)

    # -- grammar --------------------------------------------------------------
    def sequence(self, stops=('}',)) -> list[str]:
        items: list[str] = []
        while self.peek() is not None and self.peek() not in stops:
            items.append(self.scripts(self.atom()))
        return items

    def row(self, items: list[str]) -> str:
        return items[0] if len(items) == 1 else f'<mrow>{"".join(items)}</mrow>'

    def argument(self) -> str:
        if self.peek() == '{':
            self.take()
            items = self.sequence()
            self.expect('}')
            return self.row(items)
        return self.atom()

    def scripts(self, base: str) -> str:
        sub: str | None = None
        sups: list[str] = []
        prime = '<mo>′</mo>'
        while self.peek() in ('^', '_', "'"):
            token = self.take()
            if token == "'":
                sups.append(prime)
            elif token == '^':
                if any(part != prime for part in sups):
                    raise MathError('Double superscript; use braces, e.g. x^{ab}')
                sups.append(self.argument())
            else:
                if sub is not None:
                    raise MathError('Double subscript; use braces, e.g. x_{ij}')
                sub = self.argument()
        sup = None if not sups else self.row(sups)
        if base.startswith('<mo movablelimits'):
            if sub is not None and sup is not None:
                return f'<munderover>{base}{sub}{sup}</munderover>'
            if sub is not None:
                return f'<munder>{base}{sub}</munder>'
            if sup is not None:
                return f'<mover>{base}{sup}</mover>'
            return base
        if sub is not None and sup is not None:
            return f'<msubsup>{base}{sub}{sup}</msubsup>'
        if sub is not None:
            return f'<msub>{base}{sub}</msub>'
        if sup is not None:
            return f'<msup>{base}{sup}</msup>'
        return base

    def atom(self) -> str:
        token = self.take()
        if token == '{':
            items = self.sequence()
            self.expect('}')
            return self.row(items)
        if token in ('}', '&') or token == '\\\\':
            raise MathError(f'Unexpected {token!r} in formula')
        if token in ('^', '_', "'"):
            self.i -= 1  # scripts without a base, e.g. {}^{14}C
            return '<mrow></mrow>'
        if token[0].isdigit():
            return f'<mn>{token}</mn>'
        if token.isalpha():
            return f'<mi>{_e(token)}</mi>'
        if token.startswith('\\'):
            return self.command(token[1:])
        if token == '-':
            return '<mo>−</mo>'
        if token in '()[]':
            return f'<mo stretchy="false">{token}</mo>'
        if token == '~':
            return '<mspace width="0.25em"></mspace>'
        return f'<mo>{_e(token)}</mo>'

    def command(self, name: str) -> str:
        if name in _GREEK:
            return f'<mi>{_GREEK[name]}</mi>'
        if name in _UPRIGHT:
            return f'<mi mathvariant="normal">{_UPRIGHT[name]}</mi>'
        if name in _OPERATORS:
            return f'<mo>{_e(_OPERATORS[name])}</mo>'
        if name in _SPACES:
            return f'<mspace width="{_SPACES[name]}"></mspace>'
        if name in _LARGE:
            if name in _INTEGRALS:
                return f'<mo>{_LARGE[name]}</mo>'
            return f'<mo movablelimits="true">{_LARGE[name]}</mo>'
        if name in _FUNCTIONS:
            return _NAMED.format(limits='', name=name)
        if name in _LIMITS:
            label = {'argmax': 'arg max', 'argmin': 'arg min', 'limsup': 'lim sup', 'liminf': 'lim inf'}.get(name, name)
            return _NAMED.format(limits=' movablelimits="true"', name=label)
        if name in ('frac', 'dfrac', 'tfrac', 'cfrac'):
            return f'<mfrac>{self.argument()}{self.argument()}</mfrac>'
        if name == 'binom':
            return (f'<mrow><mo>(</mo><mfrac linethickness="0">{self.argument()}{self.argument()}</mfrac>'
                    f'<mo>)</mo></mrow>')
        if name == 'sqrt':
            if self.peek() == '[':
                self.take()
                index = self.row(self.sequence(stops=(']',)))
                self.expect(']')
                return f'<mroot>{self.argument()}{index}</mroot>'
            return f'<msqrt>{self.argument()}</msqrt>'
        if name in _ACCENTS:
            return f'<mover accent="true">{self.argument()}<mo>{_ACCENTS[name]}</mo></mover>'
        if name == 'underline':
            return f'<munder accentunder="true">{self.argument()}<mo>_</mo></munder>'
        if name in ('overbrace', 'underbrace'):
            tag, mark = ('mover', '⏞') if name == 'overbrace' else ('munder', '⏟')
            return f'<{tag}>{self.argument()}<mo>{mark}</mo></{tag}>'
        if name in _STYLES:
            text = self.raw_group() if self.peek() == '{' else self.take()
            return f'<mi>{_e(_STYLES[name](text))}</mi>'
        if name in ('operatorname', 'operatorname*'):
            text = self.raw_group() if self.peek() == '{' else self.take()
            return _NAMED.format(limits=' movablelimits="true"' if name.endswith('*') else '', name=_e(text))
        if name in ('mathrm', 'mathsf', 'mathtt'):
            text = self.raw_group() if self.peek() == '{' else self.take()
            return f'<mi mathvariant="normal">{_e(text)}</mi>' if len(text) == 1 else f'<mi>{_e(text)}</mi>'
        if name in ('text', 'textrm', 'textbf', 'textit', 'mbox'):
            return f'<mtext>{_e(self.raw_group())}</mtext>'
        if name == 'left':
            return self.fenced()
        if name in ('right', 'end'):
            raise MathError(f'\\{name} without a matching opening')
        if name == 'begin':
            return self.environment(self.raw_group())
        if name in ('big', 'Big', 'bigg', 'Bigg', 'bigl', 'bigr', 'Bigl', 'Bigr', 'displaystyle', 'textstyle', 'limits',
                    'nolimits'):
            return '<mrow></mrow>'
        raise MathError(f'Unsupported LaTeX command \\{name}')

    def delimiter(self) -> str:
        token = self.take()
        value = _DELIMITERS.get(token)
        if value is None:
            value = _OPERATORS.get(token[1:]) if token.startswith('\\') else None
        if value is None:
            raise MathError(f'{token!r} is not a delimiter for \\left or \\right')
        return f'<mo stretchy="true">{_e(value)}</mo>' if value else ''

    def fenced(self) -> str:
        opening = self.delimiter()
        items = self.sequence(stops=('\\right',))
        if self.peek() != '\\right':
            raise MathError('\\left without a matching \\right')
        self.take()
        return f'<mrow>{opening}{"".join(items)}{self.delimiter()}</mrow>'

    def environment(self, name: str) -> str:
        if name not in _FENCES:
            raise MathError(f'Unsupported environment {name!r}')
        if name == 'array' and self.peek() == '{':
            self.raw_group()  # column specification
        rows: list[list[str]] = [[]]
        while True:
            cell = self.sequence(stops=('&', '\\\\', '\\end'))
            token = self.take()
            rows[-1].append(self.row(cell) if cell else '')
            if token == '&':
                continue
            if token == '\\\\':
                rows.append([])
                continue
            if self.raw_group() != name:
                raise MathError(f'\\begin{{{name}}} ends with a different \\end')
            break
        if rows[-1] == ['']:
            rows.pop()
        align = ' columnalign="left"' if name == 'cases' else (' columnalign="right left"' if name.startswith('align') else '')
        body = ''.join('<mtr>' + ''.join(f'<mtd>{cell}</mtd>' for cell in row) + '</mtr>' for row in rows)
        left, right = _FENCES[name]
        table = f'<mtable{align}>{body}</mtable>'
        if not (left or right):
            return table
        fence = (f'<mo stretchy="true">{_e(left)}</mo>' if left else '') + table + (
            f'<mo stretchy="true">{_e(right)}</mo>' if right else '')
        return f'<mrow>{fence}</mrow>'


def to_mathml(latex: str, *, display: bool = True) -> str:
    """Convert a LaTeX formula (without ``$`` delimiters) to a MathML element."""
    if not isinstance(latex, str):
        raise TypeError('Formula must be a string')
    parser = _Parser(latex.strip())
    items = parser.sequence(stops=())
    mode = ' display="block"' if display else ''
    annotation = f'<annotation encoding="application/x-tex">{_e(latex.strip())}</annotation>'
    return (f'<math xmlns="http://www.w3.org/1998/Math/MathML"{mode} dir="ltr"><semantics>'
            f'<mrow>{"".join(items)}</mrow>{annotation}</semantics></math>')

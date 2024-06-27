from typing import Callable
from numbers import Number
from dataclasses import dataclass
import re
from typing import List, Any


class Reader:
    def __init__(self, tokens: List[str] = None) -> None:
        self._tokens = tokens
        self._current_idx = 0

    def next(self) -> str:
        cur = self._tokens[self._current_idx]
        self._current_idx += 1
        return cur

    def peek(self) -> str:
        if self._current_idx == len(self._tokens):
            return ''
        return self._tokens[self._current_idx]

    def rest(self) -> str:
        return ''.join(self._tokens[self._current_idx:])


REGEX = r"[\s,]*(~@|[\[\]{}()'`~^@]|\"(?:\\.|[^\\\"])*\"?|;.*|[^\s\[\]{}('\"`,;)]*)"
PATTERN = re.compile(REGEX)


@dataclass
class LispNil:
    pass


@dataclass
class LispBool:
    value: bool

    def __bool__(self):
        return self.value


Nil = LispNil()
LispTrue = LispBool(True)
LispFalse = LispBool(False)


@dataclass
class LispDeref:
    value: Any


@dataclass(frozen=True)
class LispSymbol:
    value: str


@dataclass
class LispStr:
    value: str


@dataclass
class LispKeyword:
    value: str


@dataclass
class LispNumber:
    value: Number


@dataclass
class LispList:
    value: List['LispType']


@dataclass
class LispVec:
    value: List


@dataclass
class LispHashMap:
    value: List


@dataclass
class LispClosure:
    value: Callable
    ast: Any
    params: Any
    env: Any


LispType = LispNumber | LispList | LispSymbol | LispVec | LispClosure


@dataclass
class Atom:
    value: LispType


def tokenize(s: str) -> List[str]:
    matches = PATTERN.findall(s)
    tokens = []
    for m in matches:
        if m == '' or m == ',':
            continue
        if m[0] == ';':
            continue
        else:
            tokens.append(m)

    return tokens


class FailToParseError(ValueError):
    pass


class UnbalancedError(ValueError):
    pass


def read_list(reader: Reader):
    results = []
    while True:
        t = reader.peek()
        if t == '':
            raise FailToParseError(reader.rest())
        if t == ')':
            reader.next()
            return LispList(results)
        else:
            results.append(read_form(reader))


def read_hashmap(reader: Reader):
    results = []
    while True:
        t = reader.peek()
        if t == '':
            raise FailToParseError(reader.rest())
        if t == '}':
            reader.next()
            return LispHashMap(results)
        else:
            results.append(read_form(reader))


def read_vec(reader: Reader):
    results = []
    while True:
        t = reader.peek()
        if t == '':
            raise FailToParseError(reader.rest())
        if t == ']':
            reader.next()
            return LispVec(results)
        else:
            results.append(read_form(reader))


def is_integer(value):
    try:
        x = int(value)
        return True, x
    except ValueError:
        return False, None


def _u(x): return x
def _s2u(x): return x


def _unescape(s):
    return s.replace('\\\\', _u('\u029e')).replace('\\"', '"').replace('\\n', '\n').replace(_u('\u029e'), '\\')


def read_atom(reader: Reader):
    int_re = re.compile(r"-?[0-9]+$")
    float_re = re.compile(r"-?[0-9][0-9.]*$")
    string_re = re.compile(r'"(?:[\\].|[^\\"])*"')
    token = reader.next()
    if re.match(int_re, token):
        i = int(token)
        return LispNumber(i)
    elif re.match(float_re, token):
        i = int(token)
        return LispNumber(i)
    elif re.match(string_re, token):
        return LispStr(_s2u(_unescape(token[1:-1])))
    elif token[0] == '"':
        raise UnbalancedError
    elif token[0] == ':':
        return LispKeyword(token[1:])
    else:
        if token == "nil":
            return Nil
        return LispSymbol(token)


def read_form(reader: Reader):
    t = reader.peek()
    if t == '':
        return
    if t == '@':
        reader.next()
        return LispList([LispSymbol("deref"), read_form(reader)])
    if t == '\'':
        reader.next()
        return LispList([LispSymbol("quote"), read_form(reader)])
    if t == '`':
        reader.next()
        return LispList([LispSymbol("quasiquote"), read_form(reader)])
    if t == '~@':
        reader.next()
        return LispList([LispSymbol("splice-unquote"), read_form(reader)])
    if t == '~':
        reader.next()
        return LispList([LispSymbol("unquote"), read_form(reader)])
    if t[0] == '(':
        reader.next()
        return read_list(reader)
    if t[0] == '[':
        reader.next()
        return read_vec(reader)
    if t[0] == '{':
        reader.next()
        return read_hashmap(reader)
    if t[0] == '@':
        reader.next()
        return LispDeref(read_form(reader))
    else:
        return read_atom(reader)


def read_str(s: str):
    tokens = tokenize(s)
    reader = Reader(tokens=tokens)
    return read_form(reader)

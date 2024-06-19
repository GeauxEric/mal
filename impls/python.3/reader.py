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


LispType = LispNumber | LispList | LispSymbol | LispVec | LispClosure


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


def read_atom(reader: Reader):
    t = reader.next()
    is_int, n = is_integer(t)
    if is_int:
        return LispNumber(n)
    if t[0] == '"':
        if len(t) == 1:
            raise UnbalancedError
        if t[len(t) - 1] != '"':
            raise UnbalancedError

        i = 1
        while i < len(t) - 1:
            if t[i] == '\\':
                i += 2
            else:
                i += 1
        if i == len(t):
            raise UnbalancedError
        return LispStr(t)
    return LispSymbol(t)


def read_form(reader: Reader):
    t = reader.peek()
    if t == '':
        return
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

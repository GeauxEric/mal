from env import Env
from reader import (LispSymbol, LispNumber, LispList, LispVec, LispStr, Atom,
                    LispType, LispClosure, LispTrue, LispFalse, Nil, LispNil,
                    read_str)
from printer import pr_str
REPL_ENV = Env()

REPL_ENV.set(LispSymbol('+'), lambda a, b: LispNumber(a.value+b.value))
REPL_ENV.set(LispSymbol('-'), lambda a, b: LispNumber(a.value-b.value))
REPL_ENV.set(LispSymbol('*'), lambda a, b: LispNumber(a.value*b.value))
REPL_ENV.set(LispSymbol('/'), lambda a, b: LispNumber(a.value/b.value))
REPL_ENV.set(LispSymbol('nil'), Nil)
REPL_ENV.set(LispSymbol('true'), LispTrue)
REPL_ENV.set(LispSymbol('false'), LispFalse)


def _create_list(*args):
    return LispList(list(args))


def _is_list(*args):
    if isinstance(args[0], LispList):
        return LispTrue
    else:
        return LispFalse


def _check_is_list(x):
    if not isinstance(x, LispList):
        raise TypeError('argument is not a list')


def _is_empty_list(*args):
    a = args[0]
    length = _count(a)
    if length.value == 0:
        return LispTrue
    else:
        return LispFalse


def _count(*args):
    a = args[0]

    match a:
        case LispNil():
            return LispNumber(0)
        case LispList(l):
            return LispNumber(len(l))
        case LispVec(l):
            return LispNumber(len(l))
        case _:
            raise TypeError("not a list or vec")


def _eq(*args):
    a0 = args[0]
    a1 = args[1]

    match a0, a1:
        case LispVec(l0), LispList(l1):
            if len(l0) != len(l1):
                return LispFalse
            for i in range(len(l0)):
                if not _eq(l0[i], l1[i]):
                    return LispFalse
            return LispTrue
        case LispList(l0), LispVec(l1):
            if len(l0) != len(l1):
                return LispFalse
            for i in range(len(l0)):
                if not _eq(l0[i], l1[i]):
                    return LispFalse
            return LispTrue
        case LispList(l0), LispList(l1):
            if len(l0) != len(l1):
                return LispFalse
            for i in range(len(l0)):
                if not _eq(l0[i], l1[i]):
                    return LispFalse
            return LispTrue
        case LispVec(l0), LispVec(l1):
            if len(l0) != len(l1):
                return LispFalse
            for i in range(len(l0)):
                if not _eq(l0[i], l1[i]):
                    return LispFalse
            return LispTrue
        case LispNil(), LispNil():
            return LispTrue
        case _:
            if not isinstance(a0, type(a1)):
                return LispFalse
            if a0 is Nil:
                if a1 is Nil:
                    return LispTrue
                else:
                    return LispFalse
            if a0.value == a1.value:
                return LispTrue
            else:
                return LispFalse


def _pr_str(*args):
    s = ' '.join([pr_str(x, print_readably=True) for x in args])
    return LispStr(s)


def _str(*args):
    s = ''.join([pr_str(x, print_readably=False) for x in args])
    return LispStr(s)


def _prn(*args):
    joined = ' '.join([pr_str(x, print_readably=True) for x in args])
    print(joined)
    return Nil


def _println(*args):
    joined = ' '.join([pr_str(x, print_readably=False) for x in args])
    print(joined)
    return Nil


def _read_string(s: LispStr):
    return read_str(s.value)


def _slurp(path: LispStr):
    with open(path.value, 'r') as ifs:
        c = ifs.read()
        return LispStr(c)


def _is_atom(x):
    match x:
        case Atom(_):
            return LispTrue
        case _:
            return LispFalse


def _deref(atom: Atom):
    return atom.value


def _reset(atom: Atom, value: LispType):
    atom.value = value
    return value


def _swap(atom: Atom, fn, *args):
    match fn:
        case LispClosure(function, _, _, _):
            value = function(atom.value, *args)
            atom.value = value
            return value
        case _:
            value = fn(atom.value, *args)
            atom.value = value
            return value


REPL_ENV.set(LispSymbol('swap!'), _swap)
REPL_ENV.set(LispSymbol('reset!'), _reset)
REPL_ENV.set(LispSymbol('deref'), _deref)
REPL_ENV.set(LispSymbol('atom?'), _is_atom)
REPL_ENV.set(LispSymbol('atom'), lambda x: Atom(x))
REPL_ENV.set(LispSymbol('list'), _create_list)
REPL_ENV.set(LispSymbol('list?'), _is_list)
REPL_ENV.set(LispSymbol('empty?'), _is_empty_list)
REPL_ENV.set(LispSymbol('count'), _count)
REPL_ENV.set(LispSymbol('prn'), _prn)
REPL_ENV.set(LispSymbol('pr-str'), _pr_str)
REPL_ENV.set(LispSymbol('str'), _str)
REPL_ENV.set(LispSymbol('println'), _println)
REPL_ENV.set(LispSymbol('read-string'), _read_string)
REPL_ENV.set(LispSymbol('slurp'), _slurp)
REPL_ENV.set(LispSymbol('='), _eq)
REPL_ENV.set(LispSymbol('<'), lambda n1,
             n2: LispTrue if n1.value < n2.value else LispFalse)
REPL_ENV.set(LispSymbol('<='), lambda n1,
             n2: LispTrue if n1.value <= n2.value else LispFalse)
REPL_ENV.set(LispSymbol('>'), lambda n1,
             n2: LispTrue if n1.value > n2.value else LispFalse)
REPL_ENV.set(LispSymbol('>='), lambda n1,
             n2: LispTrue if n1.value >= n2.value else LispFalse)

from reader import read_str
from printer import pr_str
from typing import Dict
from reader import (LispType, FailToParseError, UnbalancedError,
                    LispSymbol, LispList, LispNumber, LispVec, LispHashMap)

REPL_ENV = {'+': lambda a, b: a+b,
            '-': lambda a, b: a-b,
            '*': lambda a, b: a*b,
            '/': lambda a, b: int(a/b)}


def READ(x: str) -> LispType:
    return read_str(x)


class UnknownSymbolError(ValueError):
    pass


def eval_ast(ast: LispType, repl_env: Dict = None) -> LispType:
    match ast:
        case LispSymbol(v):
            if v not in repl_env:
                raise UnknownSymbolError
            return repl_env[v]
        case LispList(v):
            return LispList([EVAL(e, repl_env=repl_env) for e in v])
        case LispVec(v):
            return LispVec([EVAL(e, repl_env=repl_env) for e in v])
        case LispHashMap(v):
            ret = []
            for i in range(0, len(v), 2):
                key = v[i]
                val = v[i + 1]
                ret.append(key)
                ret.append(EVAL(val, repl_env=repl_env))
            return LispHashMap(ret)
        case _:
            return ast


def EVAL(x: LispType, repl_env=None) -> LispType:
    match x:
        case LispList(v):
            if len(v) == 0:
                return x
            li = eval_ast(x, repl_env=repl_env)
            fn = li.value[0]
            args = [d.value for d in li.value[1:]]
            ret = fn(*args)
            return LispNumber(ret)
        case _:
            return eval_ast(x, repl_env=repl_env)


def PRINT(x: LispType) -> str:
    return pr_str(x)


def rep(x: str) -> str:
    return PRINT(EVAL(READ(x), repl_env=REPL_ENV))


if __name__ == "__main__":
    # repl loop
    while True:
        try:
            line = input("user> ")
            print(rep(line))
        except UnknownSymbolError:
            print("Unkown symbol")
            continue
        except FailToParseError:
            print("EOF")
            continue
        except UnbalancedError:
            print("unbalanced")
            continue
        except EOFError:
            break

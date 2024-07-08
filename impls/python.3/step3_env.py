from reader import read_str
from printer import pr_str
from typing import Optional
from reader import (LispType, FailToParseError, UnbalancedError,
                    LispSymbol, LispList, LispNumber, LispVec, LispHashMap)

from env import Env, EnvNotFoundError

REPL_ENV = Env()

REPL_ENV.set(LispSymbol('+'), lambda a, b: LispNumber(a.value+b.value))
REPL_ENV.set(LispSymbol('-'), lambda a, b: LispNumber(a.value-b.value))
REPL_ENV.set(LispSymbol('*'), lambda a, b: LispNumber(a.value*b.value))
REPL_ENV.set(LispSymbol('/'), lambda a, b: LispNumber(a.value/b.value))


def READ(x: str) -> LispType:
    return read_str(x)


class UnknownSymbolError(ValueError):
    pass


def eval_ast(ast: LispType, repl_env: Optional[Env] = None) -> LispType:
    match ast:
        case LispSymbol(v):
            return repl_env.get(ast)
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


def EVAL(x: LispType, repl_env=Optional[Env]) -> LispType:
    match x:
        case LispList(v):
            if len(v) == 0:
                return x
            match v[0]:
                case LispSymbol('def!'):
                    value = EVAL(v[2], repl_env=repl_env)
                    return repl_env.set(v[1], value)
                case LispSymbol('let*'):
                    env = Env(outer=repl_env)
                    assert isinstance(v[1], LispList)
                    bindings = v[1].value
                    assert len(bindings) % 2 == 0, \
                        "biniding list length should be even"
                    for i in range(0, len(bindings), 2):
                        key = bindings[i]
                        value = EVAL(bindings[i + 1], repl_env=env)
                        env.set(key, value)
                    return EVAL(v[2], repl_env=env)
                case _:
                    fn, *args = eval_ast(x, repl_env=repl_env).value
                    return fn(*args)
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
        except EnvNotFoundError as e:
            print(f"{e.get_missing_env_key()} not found")
            continue
        except FailToParseError:
            print("EOF")
            continue
        except UnbalancedError:
            print("unbalanced")
            continue
        except EOFError:
            break
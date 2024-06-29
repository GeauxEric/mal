from reader import read_str
import sys
from printer import pr_str
from typing import Optional
from reader import (LispType, FailToParseError, UnbalancedError, LispClosure,
                    LispStr, Nil, LispFalse, LispSymbol, LispList, LispVec,
                    LispHashMap)

from env import Env, EnvNotFoundError
from core import REPL_ENV


def _eval(ast):
    return EVAL(ast, repl_env=REPL_ENV)


REPL_ENV.set(LispSymbol('eval'), _eval)


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


def _quasiquote(ast: LispType) -> LispType:

    def helper(li):
        results = []
        for elt in li[::-1]:
            match elt:
                case LispList([LispSymbol('splice-unquote'), *rest]):
                    results = [LispSymbol('concat')] + \
                        rest + [LispList(results)]
                case _:
                    results = [LispSymbol('cons'), _quasiquote(elt)] + [
                        LispList(results)]
        return results

    match ast:
        case LispVec(li):
            return LispList([LispSymbol('vec'), LispList(helper(li))])
        case LispList([LispSymbol('unquote'), arg]):
            return arg
        case LispList(li):
            return LispList(helper(li))
        case LispSymbol(_):
            return LispList([LispSymbol('quote'), ast])
        case LispHashMap(_):
            return LispList([LispSymbol('quote'), ast])
        case _:
            return ast


def EVAL(ast: LispType, repl_env=Optional[Env]) -> LispType:
    while True:
        match ast:
            case LispList(v):
                if len(v) == 0:
                    return ast
                match v[0]:
                    case LispSymbol('quasiquote'):
                        ast = _quasiquote(v[1])
                        continue
                    case LispSymbol('quasiquoteexpand'):
                        return _quasiquote(v[1])
                    case LispSymbol('quote'):
                        return v[1]
                    case LispSymbol('def!'):
                        value = EVAL(v[2], repl_env=repl_env)
                        return repl_env.set(v[1], value)
                    case LispSymbol('let*'):
                        let_env = Env(outer=repl_env)
                        assert isinstance(v[1], LispList)
                        bindings = v[1].value
                        assert len(bindings) % 2 == 0, \
                            "biniding list length should be even"
                        for i in range(0, len(bindings), 2):
                            key = bindings[i]
                            value = EVAL(bindings[i + 1], repl_env=let_env)
                            let_env.set(key, value)
                        repl_env = let_env
                        ast = v[2]
                        continue
                    case LispSymbol('do'):
                        for i in range(1, len(v) - 1):
                            EVAL(v[i], repl_env=repl_env)
                        ast = v[len(v) - 1]
                        continue
                    case LispSymbol('if'):
                        condition = EVAL(v[1], repl_env=repl_env)
                        if condition is Nil or condition is LispFalse:
                            if len(v) == 3:
                                return Nil
                            ast = v[3]
                            continue
                        else:
                            ast = v[2]
                            continue
                    case LispSymbol('fn*'):
                        def closure(*args):
                            env = Env(outer=repl_env,
                                      binds=v[1].value, exprs=args)
                            return EVAL(v[2], repl_env=env)
                        return LispClosure(value=closure, ast=v[2],
                                           env=repl_env, params=v[1])
                    case _:
                        fn, *args = eval_ast(ast, repl_env=repl_env).value
                        if isinstance(fn, LispClosure):
                            ast = fn.ast
                            repl_env = Env(
                                outer=fn.env, binds=fn.params.value,
                                exprs=args)

                            continue
                        return fn(*args)
            case _:
                return eval_ast(ast, repl_env=repl_env)


def PRINT(x: LispType) -> str:
    print(x)
    return pr_str(x, print_readably=True)


def rep(x: str) -> str:
    return PRINT(EVAL(READ(x), repl_env=REPL_ENV))


if __name__ == "__main__":
    argv = LispList([LispStr(x) for x in sys.argv[2:]])
    REPL_ENV.set(LispSymbol("*ARGV*"), argv)
    # repl loop
    rep('(def! not (fn* (a) (if a false true)))')
    rep('(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))')
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

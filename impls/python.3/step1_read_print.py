from reader import read_str
from printer import pr_str
from reader import LispType, FailToParseError, UnbalancedError


def READ(x: str) -> LispType:
    return read_str(x)


def EVAL(x: str) -> str:
    return x


def PRINT(x: LispType) -> str:
    return pr_str(x)


def rep(x: str) -> str:
    return PRINT(EVAL(READ(x)))


# repl loop
while True:
    try:
        line = input("user> ")
        print(rep(line))
    except FailToParseError:
        print("EOF")
        continue
    except UnbalancedError:
        print("unbalanced")
        continue
    except EOFError:
        break

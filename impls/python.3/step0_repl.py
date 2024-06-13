def READ(x: str) -> str:
    return x


def EVAL(x: str) -> str:
    return x


def PRINT(x: str) -> str:
    return x


def rep(x: str) -> str:
    return PRINT(EVAL(READ(x)))


# repl loop
while True:
    try:
        line = input("user> ")
        print(rep(line))
    except EOFError:
        break

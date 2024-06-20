from reader import (LispType, LispList, LispNumber, LispSymbol, LispClosure, LispNil,
                    LispStr, LispVec, LispHashMap, LispDeref, LispBool)


def pr_str(value: LispType, print_readably: bool = True) -> str:
    match value:
        case LispClosure(_):
            return '#<function>'
        case LispSymbol(v):
            return v
        case LispNumber(v):
            return str(v)
        case LispStr(v):
            if print_readably:
                return repr(v)
            else:
                return v
        case LispList(v):
            inner = ' '.join(
                [pr_str(e, print_readably=print_readably) for e in v])
            return f"({inner})"
        case LispBool(v):
            if v:
                return "true"
            else:
                return "false"
        case LispNil():
            return "nil"
        case LispVec(v):
            inner = ' '.join(
                [pr_str(e, print_readably=print_readably) for e in v])
            return f"[{inner}]"
        case LispDeref(v):
            return f"(deref {pr_str(v, print_readably=print_readably)})"
        case LispHashMap(v):
            inner = ' '.join(
                [pr_str(e, print_readably=print_readably) for e in v])
            return "{" + inner + "}"

from reader import (LispType, LispList, LispNumber, LispSymbol, LispClosure,
                    LispStr, LispVec, LispHashMap, LispDeref)


def pr_str(value: LispType) -> str:
    match value:
        case LispClosure(_):
            return '#<function>'
        case LispSymbol(v):
            return v
        case LispNumber(v):
            return str(v)
        case LispStr(v):
            return v
        case LispList(v):
            inner = ' '.join([pr_str(e) for e in v])
            return f"({inner})"
        case LispVec(v):
            inner = ' '.join([pr_str(e) for e in v])
            return f"[{inner}]"
        case LispDeref(v):
            return f"(deref {pr_str(v)})"
        case LispHashMap(v):
            inner = ' '.join([pr_str(e) for e in v])
            return "{" + inner + "}"

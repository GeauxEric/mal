exception Nothing
exception SyntaxError of string
exception ReaderError of string

structure Ss = Substring

datatype token =
    SPACE
    | COMMENT of string
    | BRACKET_LEFT | BRACKET_RIGHT
    | BRACE_LEFT   | BRACE_RIGHT
    | PAREN_LEFT   | PAREN_RIGHT
    | QUOTE | BACK_TICK | TILDE | TILDE_AT
    | CARET
    | AT
    | ATOM of string
    | STR_ATOM of string

fun tokenString SPACE         = "SPACE"
  | tokenString (COMMENT s)   = "COMMENT (" ^ s ^ ")"
  | tokenString BRACKET_LEFT  = "BRACKET_LEFT"
  | tokenString BRACKET_RIGHT = "BRACKET_RIGHT"
  | tokenString BRACE_LEFT    = "BRACE_LEFT"
  | tokenString BRACE_RIGHT   = "BRACE_RIGHT"
  | tokenString PAREN_LEFT    = "PAREN_LEFT"
  | tokenString PAREN_RIGHT   = "PAREN_RIGHT"
  | tokenString QUOTE         = "QUOTE"
  | tokenString BACK_TICK     = "BACK_TICK"
  | tokenString TILDE         = "TILDE"
  | tokenString TILDE_AT      = "TILDE_AT"
  | tokenString CARET         = "CARET"
  | tokenString AT            = "AT"
  | tokenString (ATOM s)      = "ATOM (" ^ s ^ ")"
  | tokenString (STR_ATOM s)  = "STR_ATOM \"" ^ s ^ "\""

datatype reader = READER of token list

fun next (READER (x::xs)) = SOME (x, READER xs)
  | next r                = NONE

fun peek (READER (x::_)) = SOME x
  | peek r               = NONE

fun rest (READER (_::xs)) = READER xs
  | rest r = raise ReaderError "out of tokens"

fun findSpecial #"[" = SOME BRACKET_LEFT
  | findSpecial #"]" = SOME BRACKET_RIGHT
  | findSpecial #"(" = SOME PAREN_LEFT
  | findSpecial #")" = SOME PAREN_RIGHT
  | findSpecial #"{" = SOME BRACE_LEFT
  | findSpecial #"}" = SOME BRACE_RIGHT
  | findSpecial #"'" = SOME QUOTE
  | findSpecial #"`" = SOME BACK_TICK
  | findSpecial #"~" = SOME TILDE
  | findSpecial #"^" = SOME CARET
  | findSpecial #"@" = SOME AT
  | findSpecial _ = NONE

fun scanSpace ss =
    let fun isSpace c = Char.isSpace c orelse c = #","
        val (tok, rest) = Ss.splitl isSpace ss in
        if Ss.isEmpty tok then NONE else SOME (SPACE, rest)
    end

fun scanComment ss =
    if Ss.isPrefix ";" ss
    then SOME (Ss.slice (ss, 1, NONE) |> Ss.string |> COMMENT,
               Ss.slice (ss, Ss.size ss, SOME 0))
    else NONE

fun scanSpecial ss =
    if Ss.isPrefix "~@" ss
    then SOME (TILDE_AT, Ss.slice (ss, 2, NONE))
    else let fun findToken (c, rest) = findSpecial c |> Option.map (fn t => (t, rest)) in
        Option.composePartial (findToken, Ss.getc) ss
    end

fun scanString ss =
    Ss.getc ss
        |> Option.mapPartial (fn (#"\"", rest) => spanString rest rest | _ => NONE)

and spanString from to = case Ss.getc to of
    SOME (#"\\", rest)   => Ss.getc rest |> Option.mapPartial (fn (_, more) => spanString from more)
    | SOME (#"\"", rest) => SOME (STR_ATOM (spanString' from to), rest)
    | SOME (_, rest)     => spanString from rest
    | NONE => raise SyntaxError "end of input reached when parsing string literal"
and spanString' from stop =
    Ss.span (from, Ss.slice (stop, 0, SOME 0)) |> Ss.string

fun scanAtom ss =
    let fun isAtomChar c = Char.isGraph c andalso (findSpecial c = NONE)
        val (tok, rest) = Ss.splitl isAtomChar ss in
        if Ss.isEmpty tok then NONE else SOME (ATOM (Ss.string tok), rest)
    end

fun scanToken ss =
    let val scanners = [scanSpace, scanComment, scanSpecial, scanString, scanAtom]
        val findScanner = List.find (fn f => isSome (f ss))
        fun applyScanner s = s ss
    in
        Option.composePartial (applyScanner, findScanner) scanners
    end

fun tokenize s = tokenize' [] (Ss.full s)
and tokenize' acc ss =
    case scanToken ss of
        SOME (token, rest) => tokenize' (token::acc) rest
        | NONE => rev acc

fun makeAtom "nil" = NIL
  | makeAtom "true" = BOOL true
  | makeAtom "false" = BOOL false
  | makeAtom s = case Int.fromString s of SOME i => INT i | NONE => SYMBOL s

fun readAtom r = case next r of
    SOME (ATOM "nil", r')     => (NIL, r')
    | SOME (ATOM "true", r')  => (BOOL true, r')
    | SOME (ATOM "false", r') => (BOOL false, r')
    | SOME (ATOM s, r')       => (Int.fromString s |> Option.map INT |> valIfNone (fn _ => SYMBOL s), r')
    | SOME (STR_ATOM s, r')   => (malUnescape s |> STRING, r')
    | SOME (token, _) => raise SyntaxError ("unexpected token reading atom: " ^ (tokenString token))
    | NONE => raise SyntaxError "end of input reached when reading atom"

fun readList acc r =
    if peek r = SOME PAREN_RIGHT
    then (LIST (rev acc), (rest r))
    else let val (a, r') = readForm r in readList (a::acc) r' end

and readForm r =
    if peek r = SOME PAREN_LEFT
    then readList [] (rest r)
    else readAtom r

fun clean ts =
    ts |> List.filter (fn x => x <> SPACE)
       |> takeWhile (fn COMMENT _ => false | _ => true)

fun readStr s =
    case tokenize s |> clean of
        [] => raise Nothing
        | ts => ts |> READER |> readForm |> #1 (* TODO: check line is empty after *)
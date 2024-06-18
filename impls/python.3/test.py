import unittest
from reader import (tokenize, Reader, read_form, LispList,
                    LispNumber, FailToParseError, UnbalancedError, LispSymbol)
from printer import pr_str
from step3_env import rep


class TestReader(unittest.TestCase):

    def test_reader(self):
        reader = Reader(tokens=['(', '123', ')'])
        self.assertEqual('(', reader.peek())
        self.assertEqual('(', reader.next())
        self.assertEqual('123', reader.peek())

    def test_tokenize(self):
        s = '(  123   456 789   ) '
        tokens = tokenize(s)
        self.assertEqual(5, len(tokens))

        s = "(  + 2   (*  3  4)  )"
        self.assertEqual(9, len(tokenize(s)))

    def test_unbalanced(self):
        s = r'"\\\\\\\\\\\\\\\\\\\"'
        tokens = tokenize(s)
        reader = Reader(tokens=tokens)
        with self.assertRaises(UnbalancedError):
            read_form(reader)

        s = "(1 2\n"
        tokens = tokenize(s)
        reader = Reader(tokens=tokens)
        with self.assertRaises(FailToParseError):
            read_form(reader)

        s = "[1 2\n"
        tokens = tokenize(s)
        reader = Reader(tokens=tokens)
        with self.assertRaises(FailToParseError):
            read_form(reader)

        s = '"abc'
        tokens = tokenize(s)
        reader = Reader(tokens=tokens)
        with self.assertRaises(UnbalancedError):
            read_form(reader)

    def test_read_form(self):
        reader = Reader(tokens=['(', '123', ')'])
        read_form(reader)
        s = "(  + 2   (*  3  4)  )"
        read_form(Reader(tokenize(s)))

    def test_printer(self):
        a = LispList([LispSymbol('a'), LispNumber(1)])
        self.assertEqual('(a 1)', pr_str(a))


class TestEval(unittest.TestCase):
    def test_env(self):
        s = "(def! a 6)"
        self.assertEqual('6', rep(s))
        self.assertEqual('6', rep('a'))
        self.assertEqual('8', rep('(def! b (+ a 2))'))
        self.assertEqual('14', rep('(+ a b)'))
        self.assertEqual('2', rep('(let* (c 2) c)'))


if __name__ == "__main__":
    unittest.main()

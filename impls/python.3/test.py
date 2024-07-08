import unittest
from reader import (tokenize, Reader, read_form, LispList, LispBool, LispStr,
                    LispNumber, FailToParseError, UnbalancedError, LispSymbol)
from printer import pr_str
from step8_macros import rep, EVAL, READ
from core import _read_string


class TestEval(unittest.TestCase):

    def test_eq(self):
        # self.assertEqual(r'"\""', rep(r'"\""'))
        # self.assertEqual('true', rep('(= nil (read-string "nil"))'))
        self.assertEqual('[1 a 3]', rep('(quasiquote [1 a 3])'))


if __name__ == "__main__":
    unittest.main()

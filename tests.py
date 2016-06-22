import unittest
from change import change_money, validate_transaction


class TestCase(unittest.TestCase):

    def test_valid_transaction(self):
        # No money - no transaction
        assert validate_transaction(0, {1: 1}) == None
        # User want more than we have
        assert validate_transaction(20, {1: 1, 2: 8}) == False
        # User want exactly the available summ
        assert validate_transaction(20, {1: 2, 2: 9}) == True
        # User want less then we have
        assert validate_transaction(20, {1: 3, 2: 9}) == True

    def test_make_change(self):
        assert change_money(167, {1: 10, 2: 5, 5: 3, 10: 15}) == {10: 15, 5: 3, 2: 1}


if __name__ == '__main__':
    unittest.main()

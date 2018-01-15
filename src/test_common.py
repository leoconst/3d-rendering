from pytest import main, raises

from common import next_randint, represent, sequence_str, special_string


def test_next_randint():
    with raises(ValueError):
        next_randint(3, 3)
        next_randint(3, 3)


class TestRepresent:

    def setup(self):
        class FooBar(object):
            pass
        self.fb = FooBar()

    def test_no_args(self):
        assert represent(self.fb) == 'FooBar()'

    def test_positional_args(self):
        assert (represent(self.fb, 'bar', 3.43, [2, '2', 1])
            == "FooBar('bar', 3.43, [2, '2', 1])")

    def test_keyword_args(self):
        assert (represent(self.fb, bar='a', a='bar')
            == "FooBar(bar='a', a='bar')")
        assert (represent(self.fb, bar=([2.1, 'a'], {}, 'foo', set()))
            == "FooBar(bar=([2.1, 'a'], {}, 'foo', set()))")
        assert (represent('bar', a=2.1, biz=['a'], foo=None, b=(4, 'moo'))
            == "str(a=2.1, biz=['a'], foo=None, b=(4, 'moo'))")

    def test_positional_and_keyword_args(self):
        assert (represent(self.fb, 2.1, a=3, b='bar')
            == "FooBar(2.1, a=3, b='bar')")
        assert (represent(self.fb, 2, 'bar', bar='v')
            == "FooBar(2, 'bar', bar='v')")


class TestSequenceStr:

    def setup(self):
        self.int_list = [3, 2, 4, 5, 2]
        self.string = 'abcdefg'

    def test_list(self):
        assert sequence_str(self.int_list) == '[3, <3 hidden items>, 2]'
        assert (sequence_str(self.int_list, limit=3)
            == '[3, 2, <2 hidden items>, 2]')

    def test_string(self):
        assert (sequence_str(self.string, brackets='()')
            == "('a', <5 hidden items>, 'g')")


def test_special_string():
    class Test(object):
        pass
    Test.__name__ = 'Test'
    test = Test()
    assert special_string(test) == '<Test>'
    assert special_string(test, a='', f=...) == "<Test a='' f=Ellipsis>"


if __name__ == '__main__':
    main()

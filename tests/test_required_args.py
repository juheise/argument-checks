import inspect
import pytest

from argument_checks.decorators import required_args
from argument_checks.verifications import _get_default_value


def test_that_missing_required_arg_results_in_syntax_error():

    with pytest.raises(ValueError) as err:

        @required_args("one")
        def op(one):
            pass

        op(None)

    assert str(err.value) == 'one is required'


def test_that_checking_for_required_args_does_execute_wrapped_fn_properly():

    @required_args("one")
    def op(one):
        return True

    assert op(1)


def test_that_required_default_arg_works_with_default():

    @required_args("one")
    def op(one=1):
        return True

    assert op()


def test_that_required_default_arg_still_gets_an_error_if_default_is_none():

    with pytest.raises(ValueError) as err:

        @required_args("one")
        def op(one=None):
            pass

        op()

    assert str(err.value) == 'one is required'


def test_that_required_default_arg_still_gets_an_error_if_default_is_empty_string():

    with pytest.raises(ValueError) as err:

        @required_args("one")
        def op(one=""):
            pass

        op()

    assert str(err.value) == 'one is required'


def test_that_required_default_arg_does_not_produce_an_error_if_its_a_false_boolean():

    @required_args("one")
    def op(one=False):
        pass

    op()


def test_get_default_value_multiple_args():

    def op(x, one="ONE"):
        pass

    argspec = inspect.getfullargspec(op)
    assert _get_default_value(1, argspec) == "ONE"


def test_get_default_value_single_arg():

    def op(one="ONE"):
        pass

    argspec = inspect.getfullargspec(op)
    assert _get_default_value(0, argspec) == "ONE"


def test_get_default_value_no_default():

    def op(x, one, two="two"):
        pass

    argspec = inspect.getfullargspec(op)
    assert _get_default_value(1, argspec) is None


def test_argspec_must_remain_the_same():

    @required_args("arg1", "arg2")
    def test_fn(arg1: str, arg2: int) -> bool:
        return True

    argspec = inspect.getfullargspec(test_fn)
    assert argspec.annotations == {"arg1": str, "arg2": int, "return": bool}


def test_that_invalid_argument_identifier_raises_key_error():

    with pytest.raises(KeyError):
        @required_args("one")
        def op(two):
            pass


def test_argless_call_makes_all_arguments_required():

    @required_args
    def test_fn(arg1: str, arg2: int) -> bool:
        return True

    with pytest.raises(ValueError):
        test_fn(None, 1)

    with pytest.raises(ValueError):
        test_fn(1, None)

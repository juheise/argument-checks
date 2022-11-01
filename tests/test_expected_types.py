import inspect
from typing import List, Union, Dict, Optional, Sequence

import pytest

from argument_checks import UnexpectedArgumentTypeError, verify_call_args_have_expected_types


@pytest.mark.parametrize("args, kwargs", [
    (["definitely not an int"], {}),
    ([1.99], {}),
    ([], {"x": "no int either"})
])
def test_that_type_error_is_raised_if_unexpected_types_are_given(args, kwargs):

    def fn(x: int):
        pass

    with pytest.raises(TypeError):
        verify_call_args_have_expected_types(args, kwargs, inspect.getfullargspec(fn))


@pytest.mark.parametrize("args, kwargs", [
    ([5], {}),
    ([], {"x": 9})
])
def test_that_no_error_is_raised_if_types_are_correct(args, kwargs):

    def fn(x: int):
        pass

    verify_call_args_have_expected_types(args, kwargs, inspect.getfullargspec(fn))


def test_that_call_without_args_raises_no_error_if_no_args_are_expected():

    def fn():
        pass

    verify_call_args_have_expected_types([], {}, inspect.getfullargspec(fn))


@pytest.mark.parametrize("args, kwargs", [
    (["random stuff"], {}),
    ([], {"x": "random stuff"})
])
def test_that_call_with_any_arg_raises_no_error_if_no_types_are_expected(args, kwargs):

    def fn(x):
        pass

    verify_call_args_have_expected_types(args, kwargs, inspect.getfullargspec(fn))


def test_that_type_error_is_raised_if_generic_types_are_violated():

    def fn(x: List[int]):
        pass

    with pytest.raises(TypeError):
        verify_call_args_have_expected_types([[0, 1, "2"]], {}, inspect.getfullargspec(fn))


def test_that_verification_succeeds_if_generic_types_are_obeyed():

    def fn(x: List[int]):
        pass

    with pytest.raises(TypeError):
        verify_call_args_have_expected_types([[0, 1, "2"]], {}, inspect.getfullargspec(fn))


def test_that_verification_can_handle_unions():

    def fn(x: Union[int, str]):
        pass

    verify_call_args_have_expected_types(["1"], {}, inspect.getfullargspec(fn))
    verify_call_args_have_expected_types([2], {}, inspect.getfullargspec(fn))
    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([1.2], {}, inspect.getfullargspec(fn))


def test_successful_verification_with_dictionary():

    def fn(x: Dict[int, str]):
        pass

    verify_call_args_have_expected_types([{1: "ha", 2: "haha"}], {}, inspect.getfullargspec(fn))


def test_failed_verification_with_dictionary():

    def fn(x: Dict[int, str]):
        pass

    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([{"haha": 1}], {}, inspect.getfullargspec(fn))
    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([{1: 1}], {}, inspect.getfullargspec(fn))


def test_successful_verification_with_dictionary_and_union():

    def fn(x: Dict[int, Union[str, bool]]):
        pass

    verify_call_args_have_expected_types([{1: "ha", 2: True}], {}, inspect.getfullargspec(fn))


def test_failed_verification_with_dictionary_and_union():

    def fn(x: Dict[int, Union[str, bool]]):
        pass

    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([{"haha": 1}], {}, inspect.getfullargspec(fn))
    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([{1: 1}], {}, inspect.getfullargspec(fn))


def test_failed_verification_with_optional_collection():

    def fn(x: Optional[Sequence[str]]):
        pass

    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([[1, 2, 3]], {}, inspect.getfullargspec(fn))


def test_failed_verification_with_optional_value():

    def fn(x: Optional[str]):
        pass

    with pytest.raises(UnexpectedArgumentTypeError):
        verify_call_args_have_expected_types([1], {}, inspect.getfullargspec(fn))


@pytest.mark.parametrize("value", ["foo", None])
def test_verification_with_optional_value_success(value):
    def fn(x: Optional[str]):
        pass
    verify_call_args_have_expected_types([value], {}, inspect.getfullargspec(fn))

from typing import List

import pytest

from argument_checks import enforce_arg_types


@pytest.mark.parametrize("args", [
    (0, "1", 2.22),
    (0, "1", None)
])
def test_that_no_error_is_raised_if_types_are_correct(args):

    @enforce_arg_types
    def fff(x: int, y: str, z):
        pass

    fff(*args)


@pytest.mark.parametrize("args", [
    ("0", "1"),
    (0, 1),
    (0.1, "1"),
    (0, b"1"),
])
def test_that_type_error_is_raised_if_unexpected_types_are_given(args):

    @enforce_arg_types
    def fff(x: int, y: str):
        pass

    with pytest.raises(TypeError):
        fff(*args)


def test_that_type_error_is_raised_if_generic_types_are_violated():

    @enforce_arg_types
    def fff(x: List[int]):
        pass

    with pytest.raises(TypeError):
        fff([1, 2, "3"])

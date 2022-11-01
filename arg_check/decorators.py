import inspect
from functools import wraps

from arg_check import verify_call_args_have_expected_types, verify_required_args_are_provided


def required_args(*arg_list):
    """Decorator that enforces the arguments specified by `*arg_list` are present in a call. If any of the required
    args is missing, `None` or in any way empty (e.g.: `[]`, `{}`, `""`, etc.), a `ValueError` is raised.

    If the decorator is applied without an `arglist` specified, the target function's arguments are all required."""

    if inspect.isfunction(arg_list[0]):
        is_argless_call = True
        fn = arg_list[0]
        argspec = inspect.getfullargspec(fn)
        arg_list = argspec.args
    else:
        is_argless_call = False

    def wrapper(fn):

        argspec = inspect.getfullargspec(fn)
        for arg in arg_list:
            if arg not in argspec.args:
                raise KeyError(f"expected argument '{arg}' not in signature of {fn.__name__}")

        @wraps(fn)
        def wrapped(*args, **kwargs):
            verify_required_args_are_provided(args, kwargs, argspec, arg_list)
            return fn(*args, **kwargs)

        _update_wrapper_signature(fn, wrapped)
        return wrapped



    if is_argless_call:
        return wrapper(fn)

    return wrapper


def enforce_arg_types(fn):
    """Decorator that raises an error if any of the arguments given in the call are not subclasses of the types
    specified via type annotations. Does not verify `None`."""

    argspec = inspect.getfullargspec(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_call_args_have_expected_types(args, kwargs, argspec)
        return fn(*args, **kwargs)

    _update_wrapper_signature(fn, wrapper)
    return wrapper


def strict_args(fn):
    """Convenience wrapper which is the same as applying @required_args and @enforce_arg_types"""
    return required_args(enforce_arg_types(fn))


def _update_wrapper_signature(fn, wrapped):
    """Replaces the signature of `ẁrapped` with the signature of `fn`."""

    sig = inspect.signature(fn)

    if inspect.ismethod(fn):
        parameters = tuple(sig.parameters.values())[1:]
    else:
        parameters = tuple(sig.parameters.values())

    sig = sig.replace(parameters=parameters)
    wrapped.__signature__ = sig

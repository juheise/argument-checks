import typing as t


_SEQUENTIAL_TYPES = [x._name for x in (t.List, t.Collection, t.Sequence, t.Tuple, t.Set, t.MutableSequence)]


class UnexpectedArgumentTypeError(TypeError):
    def __init__(self, arg_name, expected, actual):
        super().__init__(
            f"argument_name='{arg_name}' expected_type='{expected}' actual_type='{actual}'"
        )


def verify_required_args_are_provided(args, kwargs, argspec, arg_list):
    """
    Verifies that all required arguments (specified by `args` and `kwargs`) are present in a
    function operation, where `argspec` is the signature of the called function and `arg_list`
    the actual arguments of the operation.
    """
    for arg in arg_list:
        if arg in kwargs and kwargs[arg] is not None:
            continue

        index = argspec.args.index(arg)
        if _is_default_defined(index, argspec) and _get_default_value(index, argspec) not in [None, ""]:
            continue

        if index >= len(args):
            raise ValueError(f"{arg} is required")

        value = args[index]
        if value is not None and value != [None]:
            continue

        raise ValueError(f"{arg} is required")


def verify_call_args_have_expected_types(args, kwargs, argspec):
    """
    Verifies that all arguments in the operation have types that comply to the type annotations in the called
    function/method. The contents of generic lists will also be verified. Returns `None` in case of success,
    raises TypeError in case of failure.
    """
    bound_length = len(args)
    argspec_length = len(argspec.args)

    if bound_length > argspec_length:
        raise IndexError(f"operation called with {bound_length} arguments, but takes only {argspec_length}")

    for i in range(bound_length):
        if args[i] is None:
            continue
        arg_name = argspec.args[i]
        type_annotation = argspec.annotations.get(arg_name)
        if not type_annotation:
            continue
        verify_arg_type_is_expected_subclass(args[i], arg_name, type_annotation)

    for key in kwargs:
        if kwargs[key] is None:
            continue
        type_annotation = argspec.annotations.get(key)
        if not type_annotation:
            continue
        verify_arg_type_is_expected_subclass(kwargs[key], key, type_annotation)


def verify_arg_type_is_expected_subclass(item, arg_name, expected_type):
    """
    Verifies that the type of `item` is either the expected type or a subclass of it. In case that the expected
    type is a generic list, all elements in the list are checked for the correct type/subclass. `arg_name` is for
    error messaging and identifies the argument that didn't satisfy the type constraint.
    """
    type_class = expected_type.__class__

    if type_class is t._GenericAlias:

        if expected_type._name in _SEQUENTIAL_TYPES and item is not None:
            expected_items_type = expected_type.__args__[0]
            for i in item:
                verify_arg_type_is_expected_subclass(i, arg_name, expected_items_type)
            return

        elif expected_type._name is t.Dict._name:
            expected_key_type = expected_type.__args__[0]
            expected_value_type = expected_type.__args__[1]
            for k, v in item.items():
                verify_arg_type_is_expected_subclass(k, arg_name, expected_key_type)
                verify_arg_type_is_expected_subclass(v, arg_name, expected_value_type)
            return

    actual_type = type(item)
    if type_class is tuple:
        expected_type = expected_type[0]

    # in case of union
    if hasattr(expected_type, "__args__"):
        for type_ in expected_type.__args__:
            if type_.__class__ is t._GenericAlias:
                try:
                    verify_arg_type_is_expected_subclass(item, arg_name, type_)
                    return
                except UnexpectedArgumentTypeError:
                    continue
            elif issubclass(actual_type, type_):
                return
        else:
            raise UnexpectedArgumentTypeError(arg_name, f"(one of) {expected_type.__args__}", actual_type)

    elif not issubclass(actual_type, expected_type):
        raise UnexpectedArgumentTypeError(arg_name, expected_type.__name__, actual_type.__name__)


def _get_default_value(argument_index, argspec):
    """Returns the default value that is specified in the given `argspec` for the argument at the given
    `argument_ index`. There is no distinction between defaulting to None and no default specified. In both of these
    cases `None` is returned."""

    if not argspec.defaults:
        return None

    defaultslen = len(argspec.defaults)
    argslen = len(argspec.args)
    no_defaults = argslen - defaultslen
    default_index = argument_index - no_defaults

    if default_index < 0:
        return None

    return argspec.defaults[default_index]


def _is_default_defined(index, argspec):
    """
    Returns `True` if the argument at `ìndex` of `argspec` has a default value.
    Otherwise, returns `False`.
    """
    arglen = len(argspec.args) if argspec.args else 0
    defaultslen = len(argspec.defaults) if argspec.defaults else 0
    defaults_defined = defaultslen > 0
    all_args_have_defaults = arglen == defaultslen
    index_is_in_defaults_range = index >= arglen - defaultslen
    return defaults_defined and (all_args_have_defaults or index_is_in_defaults_range)

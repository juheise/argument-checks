# Arg Check

A Python utility for checking that call args have the expected types and all required args are provided.

**Works only with Python 3.7** (fixing that soon)

## Installation

```commandline
pip install arg-check
```

## Usage

This library uses simple decorators.

### Argument Type Checking

```Python
@enforce_arg_types
def foobar(a: int, b: str):
    ...
```

- Type checking is performed via the annotations. If an argument does not have an
  annotation, type checking is skipped just for that argument.
- If an argument is a collection, all items in the collection are checked.
- Can handle `Union` and `Optional`

### Required Arguments

```Python
@required_args("a", "b")
def foobar(a, b, c=None):
    ...
```

- Tests the given arguments and raises a `ValueError` if the value is either
  `None` or an empty string
- To make all arguments required, use `@required_args` without parenthesis

### All checks in one decorator

```Python
@strict_args
def foobar(a: int, b: str):
    ...
```

- All arguments are type checked
- All arguments are required

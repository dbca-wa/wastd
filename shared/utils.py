"""Shared utilities."""
import re
from collections import namedtuple
from collections.abc import Iterable


Breadcrumb = namedtuple("Breadcrumb", ["name", "url"])


def sanitize_tag_label(label_string):
    """Return string slugified, uppercased and without dashes."""
    return re.sub(
        r"[-\s]+", "-", (re.sub(r"[^\w\s]", "", label_string).strip().upper())
    )


def flatten(x):
    """Yield all elements of a nested iterable or an empty list."""

    # Anything that's not a number or string becomes []
    if (not isinstance(x, (int, str))) or x == {} or x == "NA":
        yield

    # Anything non-iterable is returned
    if not isinstance(x, Iterable):
        yield x

    # Iterables are recursively unnested
    for i in x:
        if isinstance(i, (list, tuple)):
            yield from flatten(i)
        else:
            if i == {} or i == "NA":
                yield
            else:
                yield i


def force_as_list(x):
    """Return a single element or an iterable as flattened list."""
    return [
        x
        for x in list(
            flatten(
                [
                    x,
                ]
            )
        )
        if x is not None
    ]


class BigIntConverter:
    """Define a custom path converter suitable for BigInt values.
    Reference: https://docs.djangoproject.com/en/2.2/topics/http/urls/#registering-custom-path-converters
    """

    regex = "-?[0-9]+"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return "{}".format(value)

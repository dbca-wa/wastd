"""Shared utilities."""
import slugify
import itertools
from collections import namedtuple
from collections.abc import Iterable


Breadcrumb = namedtuple('Breadcrumb', ['name', 'url'])


def sanitize_tag_label(label_string):
    """Return string slugified, uppercased and without dashes."""
    return slugify.slugify(label_string).upper().replace("-", "")


def flatten(x):
    """Yield all elements of a nested iterable or an empty list."""
    
    # Anything that's not a number or string becomes []
    if (not isinstance(x, (int, str))) or x == {} or x == 'NA':
    	yield
    
    # Anything non-iterable is returned
    if not isinstance(x, Iterable):
    	yield x

    # Iterables are recursively unnested
    for i in x:
        if isinstance(i, (list,tuple)):
            yield from flatten(i)
        else:
            if i == {} or i == 'NA':
                yield
            else:
                yield i


def force_as_list(x):
	"""Return a single element or an iterable as flattened list."""
	return [x for x in list(flatten([x, ])) if x is not None]
"""Shared utilities."""
import slugify
from collections import namedtuple


Breadcrumb = namedtuple('Breadcrumb', ['name', 'url'])


def sanitize_tag_label(label_string):
    """Return string slugified, uppercased and without dashes."""
    return slugify.slugify(label_string).upper().replace("-", "")

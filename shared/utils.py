"""Shared utilities."""
import slugify


def sanitize_tag_label(label_string):
    """Return string slugified, uppercased and without dashes."""
    return slugify.slugify(label_string).upper().replace("-", "")

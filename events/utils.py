"""Collection of utils functions."""
import math
import re
import secrets
import string

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.text import slugify

chars_string = string.ascii_lowercase + string.digits + string.ascii_uppercase


def random_string(
    *,
    size: int = getattr(settings, "SLUG_ADDITIONAL_SIZE", 6),
    chars: str = getattr(settings, "SLUG_RANDOM_CHARS", chars_string),
) -> str:
    """Generate random string.

    Args:
        size: Size of the random sting.
        chars: A sting of chars to use.

    Returns:
        Random string.

    """
    return "".join(secrets.choice(chars) for _ in range(size))


def unique_slug(*, title: str, new_slug: str = None) -> str:
    """Create unique slug.

    Args:
        title: The text where the slug will be generate.
        new_slug: Custom slug to hard code.

    Returns:
        The created slug or hard code slug
    """
    if new_slug is None:

        slug = slugify(title)

        new_slug = f"{slug}-{random_string()}"

    return new_slug


def get_read_time(*, words: str) -> int:
    """Get the read time of word in minutes.

    Args:
        words: A text to calculate the read time.

    Returns:
        read time in minutes.
    """
    word = strip_tags(value=words)

    count = len(re.findall(r"\w+", word))

    return math.ceil(count / 200)

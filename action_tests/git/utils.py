"""Common git utility functions."""

import secrets
import string

SECURE_STRING_LENGTH = 16

# define the character pool (letters, digits, and punctuation)
alphabet = string.ascii_letters + string.digits + string.punctuation


def generate_secure_string(length: int = SECURE_STRING_LENGTH) -> str:
    """Generate a secure random string using letters, digits, and punctuation.

    Args:
        length (int, default: 16) : The length of the secure string to generate

    """
    return "".join(secrets.choice(alphabet) for _ in range(length))

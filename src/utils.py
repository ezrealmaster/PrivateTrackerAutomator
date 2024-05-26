import string
import random


def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x).rstrip('/'), args))


def id_generator(size=5, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def bytes_to_gib(bytes):
    return bytes / (1 << 30)


def gib_to_bytes(gib):
    return gib * (1 << 30)

def bytes_to_gb(bytes):
    return bytes / 1e9

def gb_to_bytes(bytes):
    return bytes * 1e9
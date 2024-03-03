import base64
import random
import string

import scrypt


def rand_string() -> str:
    rand = random.SystemRandom()
    chars = string.digits + string.ascii_letters + string.punctuation
    return "".join(rand.choices(chars, k=100))


def hash_password(password: str, salt: str) -> str:
    data = scrypt.hash(password, salt, N=1 << 14, r=8, p=1, buflen=64)
    return base64.b64encode(data).decode()

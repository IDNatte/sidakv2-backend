"""Randomizer Helper Function"""


import secrets
import string
import random


def random_public_id():
    a = string.ascii_letters + string.digits
    return ''.join(secrets.choice(a) for i in range(10))


def random_id_generator():
    return ''.join((random.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(50)))

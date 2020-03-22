import random
import string
def make_rand():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)).lower()

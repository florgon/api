import hashlib


def get_hashed_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    return get_hashed_password(password) == hashed_password
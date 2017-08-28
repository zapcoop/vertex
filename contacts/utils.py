import hashlib

__all__ = ['gravatar_hash']


def gravatar_hash(email_address):
    md5 = hashlib.md5()
    md5.update(email_address.strip().lower().encode())
    return md5.hexdigest()

import time

def get_expiry_timestamp(expires_in):
    return int(time.time()) + expires_in

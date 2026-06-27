from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

RATE_LIMIT_UPLOAD = "5/hour"
RATE_LIMIT_AUTH = "20/minute"
RATE_LIMIT_API = "100/minute"

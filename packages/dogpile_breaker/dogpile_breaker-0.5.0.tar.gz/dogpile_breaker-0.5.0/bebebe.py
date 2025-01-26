import time

import redis
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff

r = redis.Redis(host='127.0.0.1', port=7480, retry=Retry(ExponentialBackoff(cap=10, base=1), 25), retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError, ConnectionRefusedError], health_check_interval=1)

while True:
    print(r.ping())
    time.sleep(0.5)
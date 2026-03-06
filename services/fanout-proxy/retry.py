import requests
import time
from prometheus_client import Counter

# Metric for retries
RETRY_ATTEMPTS = Counter(
    "retry_attempts_total",
    "Total retry attempts to auth servers"
)

def retry_request(server, path, data):
    delay = 0.1
    max_delay = 5

    while True:
        RETRY_ATTEMPTS.inc()

        try:
            r = requests.post(f"{server}{path}", json=data, timeout=2)

            if r.status_code == 201:
                return True

        except Exception:
            pass

        time.sleep(delay)
        delay = min(delay * 2, max_delay)
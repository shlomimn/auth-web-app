import threading
import requests
from retry import retry_request

# Represents multiple pods behind a service.
# auth-service pods
AUTH_SERVERS = [
    "http://auth-service:80"
]


def send_request(server, path, data):
    try:
        r = requests.post(f"{server}{path}", json=data, timeout=2)
        return r.status_code
    except Exception:
        return None


def fanout_request(path, data):
    responses = []
    threads = []

    def worker(server):
        status = send_request(server, path, data)

        if status == 201:
            responses.append(True)
        else:
            retry_request(server, path, data)

    for server in AUTH_SERVERS:
        t = threading.Thread(target=worker, args=(server,))
        t.start()
        threads.append(t)

    # Wait until the thread finishes
    for t in threads:
        t.join()

    return any(responses)
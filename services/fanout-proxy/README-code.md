## **Fanout Proxy Implementation**

The fanout proxy is implemented using three Python files,  
each responsible for a specific part of the logic.
___

```app.py```

This file contains the HTTP server (Flask application) that exposes the API endpoints handled by the fanout proxy.

Responsibilities:

* Receives incoming requests from the load balancer

* Handles the following endpoints:

   * POST /register

   * POST /changePassword

* Forwards the request to the fanout logic

* Returns the first successful 201 response to the client

```
Client
   ↓
AWS ALB
   ↓
app.py
   ↓
fanout_logic.py
```

___
```fanout_logic.py```
This file implements the fan-out mechanism.

Responsibilities:

* Sends the incoming POST request to all auth-server instances

* Runs requests concurrently

* Detects the first successful response (HTTP 201)

* Triggers retries for any failed servers


```
fanout_logic.py
    │
    ├── auth pod 1
    ├── auth pod 2
    ├── auth pod 3
    └── auth pod N
```

___

```retry.py```
This file implements the retry mechanism with exponential backoff.

Responsibilities:

* Retries failed upstream servers

* Uses exponential backoff between attempts

* Ensures each server eventually processes the POST request


Backoff example:
```
retry delays:
0.1s → 0.2s → 0.4s → 0.8s → 1.6s ...
```
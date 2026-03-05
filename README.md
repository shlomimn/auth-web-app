# Auth Web App – Scalable Load Balancer
## Overview
This project implements a scalable authentication system with a custom load-balancing strategy.

The system exposes the following API endpoints:

* POST /register

* POST /changePassword

* GET /login

The load balancer behaves differently for GET and POST requests:

| Request | Behavior |
|--------|----------|
| GET | Forwarded to one auth server using round-robin |
| POST | Forwarded to all auth servers (fan-out) |
| POST | Returns the first successful **201** response while retrying failed upstream servers with exponential backoff |

## Architecture diagram
```
Client
  │
  ▼
AWS ALB
  │
  ├── GET /login
  │       │
  │       ▼
  │   auth-service
  │       │
  │       ├── auth pod 1  (image supplied)
  │       ├── auth pod 2  (image supplied)
  │       ├── auth pod 3  (image supplied)
  │       ├── ...
  │       └── auth pod N  (image supplied)
  │       (round robin)
  │
  └── POST /register
       POST /changePassword
            │
            ▼
       fanout-proxy pod
       (image built from this repository)
            │
            ├── auth pod 1  (image supplied)
            ├── auth pod 2  (image supplied)
            ├── auth pod 3  (image supplied)
            ├── ...
            └── auth pod N  (image supplied)
            (fan-out to all servers)
```

## Explanation
### GET requests
```Client → ALB → auth-service → auth pods```

Kubernetes distributes requests across pods using round-robin.


### POST requests
```Client → ALB → fanout-proxy → all auth pods```

The fanout proxy:

1. Sends the POST request to all auth servers

2. Returns the first 201 response

3. Retries failed servers using exponential backoff

## Project Structure
```
auth-web-app
│
├── services
│   └── fanout_proxy
│       ├── app.py
│       ├── fanout_logic.py
│       ├── retry.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── k8s
│   ├── namespace.yaml
│   ├── auth-deployment.yaml
│   ├── auth-service.yaml
│   ├── fanout-deployment.yaml
│   ├── fanout-service.yaml
│   └── ingress.yaml
│
└── README.md
```
## Assumption
**The auth-server image is supplied externally by the assignment provider.**  
(The original website image)

## Prerequisites
* AWS Kubernetes cluster
* kubectl
* Docker

## Build the Fanout Proxy
```docker build -t fanout-proxy ./services/fanout_proxy```

## Deploy K8s
### Create namespace:
```kubectl apply -f k8s/namespace.yaml```

### Deploy services:
```kubectl apply -f k8s/```

### Verify pods:
```kubectl get pods -n auth-web-app```

### Expected output:
```
auth-server-xxxxx
auth-server-xxxxx
auth-server-xxxxx
fanout-proxy-xxxxx
```

## Testing the System
Get the load balancer address:
```kubectl get ingress -n auth-web-app```

Example:
```http://<LOAD_BALANCER_URL>```

### Test Register (POST)
```
curl -X POST http://<LOAD_BALANCER_URL>/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123"}'
```

Expected response:
``` HTTP 201 ```

### Test Change Password (POST)
```
curl -X POST http://<LOAD_BALANCER_URL>/changePassword \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"456"}'
```

### Test Login (GET)
```
curl "http://<LOAD_BALANCER_URL>/login?username=alice"
```
Multiple requests should be distributed across auth pods.

## Performance Targets
The solution supports:

* 100 POST requests/sec

* 1000 GET requests/sec

by:

1. using concurrent fan-out requests

2. returning the first successful response

3. retrying failed servers asynchronously


## Summary
This solution provides:

* scalable stateless load balancing

* fan-out POST replication

* retry with exponential backoff

* Kubernetes-based deployment


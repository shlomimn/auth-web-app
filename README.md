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
  │       ├── auth pod 1
  │       ├── auth pod 2
  │       ├── auth pod 3
  │       ├── ...
  │       └── auth pod N  (image supplied)
  │       (round robin)
  │
  └── POST /register
      POST /changePassword
            │
            ▼
       fanout-proxy service ◄──────── scrape /metrics ───────── Prometheus ───────► Grafana
            │
            ▼
       fanout-proxy pod
       (image built from this repository)
            │
            ├── auth pod 1
            ├── auth pod 2
            ├── auth pod 3
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
auth-web-app/
│
├── assignment/
│   ├── README-problems.md
│   └── Treeverse Home Assignment - Infra.pdf
│
├── k8s/
│   ├── namespace.yaml          # Kubernetes namespace definition
│   ├── auth-deployment.yaml    # Deployment for auth server pods
│   ├── auth-service.yaml       # ClusterIP service exposing auth pods
│   ├── fanout-deployment.yaml  # Deployment for fanout proxy pods
│   ├── fanout-service.yaml     # Service exposing the fanout proxy
│   └── ingress.yaml            # Ingress exposing the system externally
│
├── services/
│   └── fanout-proxy/
│       ├── docker/
│       │   └── Dockerfile          # Builds the fanout proxy container image
│       │
│       ├── python/
│       │   ├── app.py              # Flask gateway handling HTTP requests
│       │   ├── fanout_logic.py     # Fan-out request logic for POST operations
│       │   ├── retry.py            # Exponential backoff retry mechanism
│       │   └── requirements.txt    # Python dependencies
│       │
│       └── README-code.md          # Explanation of the proxy implementation
│
└── README.md                       # Main project documentation
```

## Key Components

| Component                | Purpose                                                             |
| ------------------------ | ------------------------------------------------------------------- |
| **Fanout Proxy**         | Python Flask gateway that implements the smart load balancing logic |
| **Auth Service**         | Backend service that stores authentication data locally             |
| **Kubernetes Manifests** | Deploy and expose the services in the cluster                       |
| **Ingress**              | Exposes the fanout proxy externally                                 |
| **Dockerfile**           | Packages the proxy into a container image                           |

## Assumption
**The "auth pods" run a pre-built image supplied as part of the assignment, while the
"fanout-proxy" image is built from the code in this repository.**  
("auth pods" = The original website image)

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

## Monitoring
### Metrics:
How monitoring works:
```
Prometheus
    │
    ▼
fanout-proxy:8080/metrics
```

What metrics look like when calling ```/metrics```:
```
post_requests_total{endpoint="register"} 120
post_requests_total{endpoint="changePassword"} 45
retry_attempts_total 8
```

### Prometheus Scraping:

The fanout proxy exposes metrics at: ```/metrics```

Prometheus scrapes the service using the Kubernetes DNS name:
```
fanout-proxy.auth-system.svc.cluster.local:8080
```

Example for Prometheus configuration:
```
scrape_configs:
  - job_name: fanout-proxy
    metrics_path: /metrics
    static_configs:
      - targets:
        - fanout-proxy.auth-system.svc.cluster.local:8080
```
This configuration instructs Prometheus to periodically scrape the fanout proxy
metrics endpoint in order to collect operational metrics such as request counts
and retry attempts.

### Grafana Dashboards: 
Build Grafana dashboards like:

* Register requests/sec

* Password change requests/sec

* Retry spikes (detect auth node failures)


## Summary
This solution provides:

* scalable stateless load balancing

* fan-out POST replication

* retry with exponential backoff

* Kubernetes-based deployment


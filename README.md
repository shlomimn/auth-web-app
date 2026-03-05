# auth-web-app
Auth web-app assignment

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
  │   auth pods (round robin)
  │
  └── POST /register
      POST /changePassword
            │
            ▼
       fanout-proxy
            │
            ├── auth pod 1
            ├── auth pod 2
            ├── auth pod 3
            └── auth pod N
```


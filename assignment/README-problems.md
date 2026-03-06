# System Before the Solution
The system has multiple auth servers, and each server stores data locally in a JSON file.

There is no smart load balancer, so requests may reach any server.

## The Core Problem
Each server has its own file:
```
server1/users.json
server2/users.json
server3/users.json
```
These files are not shared.

### Example: User Registration
#### Step 1 — User sends POST
```
POST /register
{ "username": "alice" }
```
Request happens to reach Server 2.
```
// server2/users.json
{
  "users": ["alice"]
}
```
But the other servers remain unchanged.
```
// server1/users.json
{
  "users": []
}
```
```
// server3/users.json
{
  "users": []
}
```
#### Step 2 — User Sends Next Request
User tries to log in.
```
GET /login
username=alice
```
This time the request reaches Server 1.
```
Client
  │
  ▼
Auth Server 1
```
Server 1 checks its JSON:
```
{
  "users": []
}
```
Result:
```
401 Unauthorized
```

This happens because servers store data independently.

### The Result
The system becomes inconsistent:
```
Server1 users.json → []
Server2 users.json → ["alice"]
Server3 users.json → []
```
Different servers have different data.


## Problem summary
```
POST updates only one server
GET may go to another server
→ user data becomes inconsistent
```
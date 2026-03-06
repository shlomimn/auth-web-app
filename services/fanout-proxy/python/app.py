from flask import Flask, request, jsonify
from fanout_logic import fanout_request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Metrics
POST_REQUESTS = Counter(
    "post_requests_total",
    "Total POST requests handled by endpoint",
    ["endpoint"]
)

@app.route("/register", methods=["POST"])
@app.route("/changePassword", methods=["POST"])
def handle_post():
    """
    Receives POST requests from ALB and triggers fan-out
    to all auth servers.
    """

    data = request.json
    path = request.path

    # increment metric per endpoint
    if path == "/register":
        POST_REQUESTS.labels(endpoint="register").inc()
    elif path == "/changePassword":
        POST_REQUESTS.labels(endpoint="changePassword").inc()

    success = fanout_request(path, data)

    if success:
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failed"}), 500

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Flask server
    app.run(host="0.0.0.0", port=8080)
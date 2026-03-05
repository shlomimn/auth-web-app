from flask import Flask, request, jsonify
from fanout_logic import fanout_request

app = Flask(__name__)


@app.route("/register", methods=["POST"])
@app.route("/changePassword", methods=["POST"])
def handle_post():
    """
    Receives POST requests from ALB and triggers fan-out
    to all auth servers.
    """

    data = request.json
    path = request.path

    success = fanout_request(path, data)

    if success:
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failed"}), 500


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Flask server
    app.run(host="0.0.0.0", port=8080)
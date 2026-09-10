import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# Baked into the image at build time by the CD workflow (see Dockerfile ARGs)
APP_VERSION = os.environ.get("APP_VERSION", "dev")
GIT_COMMIT = os.environ.get("GIT_COMMIT", "unknown")
MODEL_VERSION = "model-8"


@app.route("/")
def home():
    return jsonify({
        "service": "mlops-demo",
        "status": "running"
    })


@app.route("/health")
def health():
    return jsonify({
        "application_version": APP_VERSION,
        "model_version": MODEL_VERSION,
        "git_commit": GIT_COMMIT,
        "status": "healthy"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    value = float(data["value"])

    # Dummy ML prediction for teaching
    prediction = value * 2

    return jsonify({
        "input": value,
        "prediction": prediction,
        "model_version": MODEL_VERSION
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

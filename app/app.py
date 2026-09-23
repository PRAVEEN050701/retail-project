from flask import Flask, jsonify
import os

app = Flask(__name__)

# Configuration comes from environment variables.
APP_VERSION = os.getenv("APP_VERSION", "4.2.0")
APP_ENV = os.getenv("APP_ENV", "UAT")
PAYMENT_STATUS = os.getenv("PAYMENT_STATUS", "FIXED")


# Home endpoint
@app.route("/")
def home():
    return jsonify({
        "application": "retail-platform",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "payment_status": PAYMENT_STATUS
    })


# Health endpoint
@app.route("/health")
def health():
    # Version 4.2.2 is intentionally unhealthy
    # for the Jenkins rollback demonstration.
    if APP_VERSION == "4.2.2":
        return jsonify({
            "status": "unhealthy",
            "version": APP_VERSION
        }), 500

    return jsonify({
        "status": "healthy",
        "version": APP_VERSION
    }), 200


# Payment endpoint
@app.route("/payment", methods=["GET"])
def payment():
    if PAYMENT_STATUS == "DEFECTIVE":
        return jsonify({
            "payment": "failed",
            "message": "Payment processing defect exists",
            "version": APP_VERSION
        }), 500

    return jsonify({
        "payment": "successful",
        "message": "Payment processed successfully",
        "version": APP_VERSION
    }), 200


# Version endpoint
@app.route("/version")
def version():
    return jsonify({
        "application": "retail-platform",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "payment_status": PAYMENT_STATUS
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8081
    )
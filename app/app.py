from flask import Flask, jsonify
import os

app = Flask(__name__)

# Configuration comes from environment variables.
APP_VERSION = os.getenv("APP_VERSION", "4.2.0")
APP_ENV = os.getenv("APP_ENV", "DEVELOPMENT")
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
    # Normal versions should pass health check.
    # We will intentionally make 4.2.2 unhealthy later
    # for the rollback demonstration.
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
    
@app.route("/products")
def products():
    return jsonify({
        "products": [
            {
                "id": 101,
                "name": "Laptop",
                "price": 65000
            },
            {
                "id": 102,
                "name": "Phone",
                "price": 30000
            }
        ]
    })


@app.route("/customers")
def customers():
    customer_list = [
        {
            "id": 1001,
            "name": "John",
            "email": "john@example.com"
        },
        {
            "id": 1002,
            "name": "David",
            "email": "david@example.com"
        },
        {
            "id": 1003,
            "name": "Priya",
            "email": "priya@example.com"
        }
    ]

    search = request.args.get("search")

    if search:
        search = search.lower()

        customer_list = [
            customer for customer in customer_list
            if search in customer["name"].lower()
            or search in customer["email"].lower()
        ]

    return jsonify({
        "customers": customer_list
    })



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8081
    )
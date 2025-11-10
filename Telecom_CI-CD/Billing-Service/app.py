
from flask import Flask, jsonify
import requests

app = Flask(__name__)

CUSTOMER_SERVICE_URL = "http://localhost:5000/customers"

@app.route('/')
def home():
    return jsonify({"message": "Billing Service is running!"})

@app.route('/bill/<int:customer_id>', methods=['GET'])
def get_bill(customer_id):
    try:
        response = requests.get(f"{CUSTOMER_SERVICE_URL}/{customer_id}")
        if response.status_code != 200:
            return jsonify({"error": "Customer not found"}), 404

        customer = response.json()
        bill_amount = 100 if customer["status"] == "active" else 0
        return jsonify({
            "customer": customer["name"],
            "status": customer["status"],
            "bill_amount": bill_amount
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
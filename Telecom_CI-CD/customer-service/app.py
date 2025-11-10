
from flask import Flask, jsonify

app = Flask(__name__)

customers = {
    1: {"name": "Alice", "status": "active"},
    2: {"name": "Bob", "status": "inactive"},
    3: {"name": "Charlie", "status": "active"}
}

@app.route('/')
def home():
    return jsonify({"message": "Customer Service is running!"})

@app.route('/customers', methods=['GET'])
def get_all_customers():
    return jsonify(customers)

@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = customers.get(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
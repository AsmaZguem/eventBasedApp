from flask import Flask, jsonify
from flask_cors import CORS
from db import get_customer_by_cin

app = Flask(__name__)
CORS(app)

@app.route('/api/credit-check/<cin>', methods=['GET'])
def check_credit(cin):

    customer = get_customer_by_cin(cin)
    
    if customer is None:
        return 'false', 404
    
    result = 'true' if customer['has_unpaid_commitments'] else 'false'
    return result, 200

if __name__ == '__main__':
    print("=" * 50)
    print("Central Bank API")
    print("=" * 50)
    print("Endpoint: GET /api/credit-check/<cin>")
    print("Example: http://localhost:5000/api/credit-check/11111111")
    print("=" * 50)
    print("Starting server on http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
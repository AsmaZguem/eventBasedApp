from flask import request, jsonify, session, make_response, send_file, current_app
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.loan_db import get_loans_by_cin, get_loan_by_id, get_approved_loans_by_cin

from flask import current_app as app

@app.route("/api/loans", methods=["GET", "OPTIONS"])
def get_my_loans():
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    print(f"Loans request - Session data: {dict(session)}")
    
    if "cin" not in session:
        print("Loans request failed: No CIN in session")
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    cin = session["cin"]
    
    try:
        loans = get_loans_by_cin(cin)
        
        for loan in loans:
            if loan.get('application_date'):
                loan['application_date'] = loan['application_date'].strftime('%Y-%m-%d %H:%M:%S')
            if loan.get('approved_date'):
                loan['approved_date'] = loan['approved_date'].strftime('%Y-%m-%d %H:%M:%S')
            if loan.get('signed_date'):
                loan['signed_date'] = loan['signed_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Found {len(loans)} loans for CIN {cin}")
        
        response = make_response(jsonify({
            "loans": loans,
            "count": len(loans)
        }), 200)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error fetching loans: {e}")
        import traceback
        traceback.print_exc()
        
        response = make_response(jsonify({
            "error": "Failed to fetch loans",
            "details": str(e)
        }), 500)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

@app.route("/api/loans/<int:loan_id>", methods=["GET", "OPTIONS"])
def get_loan_details(loan_id):
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if "cin" not in session:
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    cin = session["cin"]
    
    try:
        loan = get_loan_by_id(loan_id)
        
        if not loan:
            response = make_response(jsonify({"error": "Loan not found"}), 404)
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        if loan['cin'] != cin:
            response = make_response(jsonify({"error": "Unauthorized"}), 403)
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        if loan.get('application_date'):
            loan['application_date'] = loan['application_date'].strftime('%Y-%m-%d %H:%M:%S')
        if loan.get('approved_date'):
            loan['approved_date'] = loan['approved_date'].strftime('%Y-%m-%d %H:%M:%S')
        if loan.get('signed_date'):
            loan['signed_date'] = loan['signed_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        response = make_response(jsonify(loan), 200)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error fetching loan details: {e}")
        response = make_response(jsonify({
            "error": "Failed to fetch loan details",
            "details": str(e)
        }), 500)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

@app.route("/api/loans/<int:loan_id>/contract", methods=["GET", "OPTIONS"])
def download_contract(loan_id):
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if "cin" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    cin = session["cin"]
    
    try:
        loan = get_loan_by_id(loan_id)
        
        if not loan or loan['cin'] != cin:
            return jsonify({"error": "Loan not found or unauthorized"}), 404
        
        if not loan.get('contract_path') or not os.path.exists(loan['contract_path']):
            return jsonify({"error": "Contract not available"}), 404
        
        return send_file(
            loan['contract_path'],
            as_attachment=True,
            download_name=f'contract_{loan_id}.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        print(f"Error downloading contract: {e}")
        return jsonify({"error": "Failed to download contract"}), 500

@app.route("/api/loans/<int:loan_id>/amortization", methods=["GET", "OPTIONS"])
def download_amortization(loan_id):
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if "cin" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    cin = session["cin"]
    
    try:
        loan = get_loan_by_id(loan_id)
        
        if not loan or loan['cin'] != cin:
            return jsonify({"error": "Loan not found or unauthorized"}), 404
        
        if not loan.get('amortization_path') or not os.path.exists(loan['amortization_path']):
            return jsonify({"error": "Amortization table not available"}), 404
        
        return send_file(
            loan['amortization_path'],
            as_attachment=True,
            download_name=f'amortization_{loan_id}.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        print(f"Error downloading amortization: {e}")
        return jsonify({"error": "Failed to download amortization table"}), 500

@app.route("/api/loans/<int:loan_id>/contract/view", methods=["GET", "OPTIONS"])
def view_contract(loan_id):
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if "cin" not in session:
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    cin = session["cin"]
    
    try:
        loan = get_loan_by_id(loan_id)
        
        if not loan or loan['cin'] != cin:
            return jsonify({"error": "Loan not found or unauthorized"}), 404
        
        if not loan.get('contract_path') or not os.path.exists(loan['contract_path']):
            return jsonify({"error": "Contract not available"}), 404
        
        with open(loan['contract_path'], 'r', encoding='utf-8') as f:
            contract_content = f.read()
        
        response = make_response(jsonify({
            "loan_id": loan_id,
            "content": contract_content
        }), 200)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error viewing contract: {e}")
        response = make_response(jsonify({"error": "Failed to load contract"}), 500)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

@app.route("/api/loans/<int:loan_id>/amortization/view", methods=["GET", "OPTIONS"])
def view_amortization(loan_id):
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    if "cin" not in session:
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    cin = session["cin"]
    
    try:
        loan = get_loan_by_id(loan_id)
        
        if not loan or loan['cin'] != cin:
            return jsonify({"error": "Loan not found or unauthorized"}), 404
        
        if not loan.get('amortization_path') or not os.path.exists(loan['amortization_path']):
            return jsonify({"error": "Amortization table not available"}), 404
        
        with open(loan['amortization_path'], 'r', encoding='utf-8') as f:
            amortization_content = f.read()
        
        response = make_response(jsonify({
            "loan_id": loan_id,
            "content": amortization_content
        }), 200)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error viewing amortization: {e}")
        response = make_response(jsonify({"error": "Failed to load amortization table"}), 500)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
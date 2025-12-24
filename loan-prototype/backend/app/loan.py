from flask import request, jsonify, session, make_response, current_app
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))
from services.events import publish_loan_submitted

from flask import current_app as app

@app.route("/api/loan/submit", methods=["POST", "OPTIONS"])
def submit_loan():
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    print(f"Loan submission - Session data: {dict(session)}")
    
    if "cin" not in session:
        print("Loan submission failed: No CIN in session")
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    data = request.get_json()
    
    if not data or "loan_amount" not in data or "duration" not in data:
        return jsonify({"error": "Loan amount and duration required"}), 400
    
    cin = session["cin"]
    loan_amount = float(data["loan_amount"])
    duration = int(data["duration"])
    
    if loan_amount <= 0 or duration <= 0:
        return jsonify({"error": "Invalid loan amount or duration"}), 400
    
    if loan_amount > 100000:
        return jsonify({"error": "Loan amount exceeds maximum (100,000 TND)"}), 400
    
    if duration > 120:
        return jsonify({"error": "Duration exceeds maximum (120 months)"}), 400
    
    print(f"Submitting loan application:")
    print(f"  CIN: {cin}")
    print(f"  Amount: {loan_amount} TND")
    print(f"  Duration: {duration} months")
    
    try:
        success = publish_loan_submitted(cin, loan_amount, duration)
        
        if success:
            print(f"Loan application submitted successfully")
            response = make_response(jsonify({
                "success": True,
                "message": "Loan application submitted successfully",
                "cin": cin,
                "loan_amount": loan_amount,
                "duration": duration
            }), 200)
        else:
            print(f"Failed to submit loan application")
            response = make_response(jsonify({
                "error": "Failed to submit loan application"
            }), 500)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error submitting loan: {e}")
        import traceback
        traceback.print_exc()
        
        response = make_response(jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500)
        
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
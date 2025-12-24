from flask import request, jsonify, session, make_response
from database.bank_db import verify_login

from flask import current_app as app

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response
    
    data = request.get_json()
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    client = verify_login(data["email"], data["password"])
    
    if client is None:
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session['cin'] = client["cin"]
    session['name'] = client["name"]
    session['email'] = client["email"]
    session.permanent = True
    
    print(f"Session created for user: {client['name']} (CIN: {client['cin']})")
    print(f"Session data: {dict(session)}")
    print(f"Request origin: {origin}")

    response = make_response(jsonify({"success": True, "user": client}), 200)
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    print(f"Response Set-Cookie: {response.headers.get('Set-Cookie', 'No cookie set!')}")
    
    return response

@app.route("/api/logout", methods=["POST", "OPTIONS"])
def logout():
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    print(f"Logging out user. Session before clear: {dict(session)}")
    session.clear()
    
    response = make_response(jsonify({"success": True}), 200)
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@app.route("/api/user", methods=["GET", "OPTIONS"])
def get_current_user():
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    print(f"Checking user session: {dict(session)}")
    print(f"Cookies received: {dict(request.cookies)}")
    print(f"Request origin: {origin}")
    print(f"Session cookie name: {app.config.get('SESSION_COOKIE_NAME')}")

    if "cin" not in session:
        print("No CIN in session - not authenticated")
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    print(f"User authenticated: {session['name']}")
    
    response = make_response(jsonify({
        "cin": session["cin"],
        "name": session["name"],
        "email": session["email"]
    }), 200)
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@app.route("/api/test-session", methods=["GET"])
def test_session():
    return jsonify({
        "session_active": "cin" in session,
        "session_data": dict(session) if session else {},
        "cookies": dict(request.cookies),
        "origin": request.headers.get('Origin', 'unknown'),
        "expected_cookie_name": app.config.get('SESSION_COOKIE_NAME')
    }), 200
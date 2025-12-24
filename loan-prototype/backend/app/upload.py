from flask import request, jsonify, session, current_app, make_response
import os
from flask import current_app as app

def allowed_file(filename):
    """
    Check if file is allowed - accepts PDF and images
    """
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload", methods=["POST", "OPTIONS"])
def upload_file():
    """Upload a file for the authenticated user - replaces existing file"""
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    print(f"→ Upload request - Session data: {dict(session)}")
    print(f"→ Cookies received: {dict(request.cookies)}")
    
    if "cin" not in session:
        print("Upload failed: No CIN in session")
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF and images allowed."}), 400

    cin = session["cin"]
    
    original_ext = os.path.splitext(file.filename)[1]
    if not original_ext:
        original_ext = ".pdf"
    
    filename = f"{cin}{original_ext}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    folder = current_app.config["UPLOAD_FOLDER"]
    if os.path.exists(folder):
        for old_file in os.listdir(folder):
            if old_file.startswith(str(cin)):
                old_path = os.path.join(folder, old_file)
                try:
                    os.remove(old_path)
                    print(f"Deleted old file: {old_file}")
                except Exception as e:
                    print(f"Could not delete old file {old_file}: {e}")

    try:
        file.save(filepath)
        print(f"File saved successfully: {filename}")
        
        response = make_response(jsonify({"success": True, "filename": filename}), 200)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save file"}), 500

@app.route("/api/files", methods=["GET", "OPTIONS"])
def get_user_files():
    """Get list of files for the authenticated user"""
    origin = request.headers.get('Origin')
    
    if request.method == "OPTIONS":
        response = make_response('', 204)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    print(f"Files request - Session data: {dict(session)}")
    print(f"Cookies received: {dict(request.cookies)}")
    
    if "cin" not in session:
        print("Files request failed: No CIN in session")
        response = make_response(jsonify({"error": "Not authenticated"}), 401)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    cin = session["cin"]
    folder = current_app.config["UPLOAD_FOLDER"]
    
    if not os.path.exists(folder):
        response = make_response(jsonify({"files": [], "count": 0}), 200)
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    user_files = [f for f in os.listdir(folder) if f.startswith(str(cin))]
    user_files.sort()

    print(f"Found {len(user_files)} files for CIN {cin}")
    
    response = make_response(jsonify({"files": user_files, "count": len(user_files)}), 200)
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
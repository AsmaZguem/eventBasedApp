"""
app.py
Main Flask application entry point.
Run this file to start the server.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("Loan Management Backend Server")
    print("=" * 60)
    print("Starting server on http://localhost:5001")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5001)  
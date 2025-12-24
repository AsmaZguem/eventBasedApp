"""
ocr_service/app.py
Standalone OCR microservice
Runs independently and processes documents from the uploads folder
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    # Tesseract OCR executable path
    TESSERACT_CMD = r'C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    
    # Poppler path for PDF processing
    POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin'
    
    # Path to the main application's uploads folder
    UPLOADS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    @staticmethod
    def setup():
        """Setup and validate configuration"""
        # Add Poppler to PATH
        if os.path.exists(Config.POPPLER_PATH):
            if Config.POPPLER_PATH not in os.environ['PATH']:
                os.environ['PATH'] = Config.POPPLER_PATH + os.pathsep + os.environ['PATH']
                print(f"✓ Added Poppler to PATH")

# Set tesseract command
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_income_data(file_path):
    """Extract income and expense data from document"""
    monthly_income = 0
    expenses = 0

    try:
        normalized_path = os.path.normpath(file_path)
        
        if not os.path.exists(normalized_path):
            print(f"[OCR COMMERCIAL] File not found: {normalized_path}")
            return {"monthly_income": 3000, "expenses": 800}
        
        # Convert PDF to images or open image directly
        if normalized_path.lower().endswith('.pdf'):
            print(f"[OCR COMMERCIAL] Processing PDF: {normalized_path}")
            try:
                # Try with explicit poppler_path first
                images = convert_from_path(
                    normalized_path, 
                    poppler_path=Config.POPPLER_PATH
                )
            except Exception as e:
                print(f"[OCR COMMERCIAL] Error with explicit poppler_path: {e}")
                # Try without poppler_path (relies on PATH)
                try:
                    images = convert_from_path(normalized_path)
                except Exception as e2:
                    print(f"[OCR COMMERCIAL] Error without poppler_path: {e2}")
                    raise
        else:
            print(f"[OCR COMMERCIAL] Processing image: {normalized_path}")
            images = [Image.open(normalized_path)]

        # Process each page/image
        for idx, img in enumerate(images):
            print(f"[OCR COMMERCIAL] Processing page/image {idx + 1}")
            text = pytesseract.image_to_string(img)
            
            print(f"[OCR COMMERCIAL] Extracted text length: {len(text)} chars")

            # Extract numbers from lines containing keywords
            lines = text.split('\n')
            for line in lines:
                lower = line.lower()
                numbers = [int(n) for n in re.findall(r'\d+', line)]

                # Look for income-related keywords
                if any(k in lower for k in ['income', 'salary', 'earnings', 'revenue', 'salaire', 'revenu']) and numbers:
                    potential_income = max(numbers)
                    if potential_income > monthly_income:
                        monthly_income = potential_income
                        print(f"[OCR COMMERCIAL] Found income: {monthly_income}")
                
                # Look for expense-related keywords
                if any(k in lower for k in ['expense', 'rent', 'cost', 'bill', 'dépense', 'loyer']) and numbers:
                    potential_expense = max(numbers)
                    if potential_expense > expenses:
                        expenses = potential_expense
                        print(f"[OCR COMMERCIAL] Found expense: {expenses}")
                        
    except Exception as e:
        print(f"[OCR COMMERCIAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    # Fallback values
    if monthly_income == 0:
        monthly_income = 3000
    if expenses == 0:
        expenses = 800

    return {"monthly_income": monthly_income, "expenses": expenses}

def extract_debt_data(file_path):
    """Extract debt/liability data from document"""
    existing_debt = 0

    try:
        normalized_path = os.path.normpath(file_path)
        
        if not os.path.exists(normalized_path):
            print(f"[OCR RISK] File not found: {normalized_path}")
            return {"existing_debt": 500}
        
        # Convert PDF to images or open image directly
        if normalized_path.lower().endswith('.pdf'):
            print(f"[OCR RISK] Processing PDF: {normalized_path}")
            try:
                images = convert_from_path(
                    normalized_path, 
                    poppler_path=Config.POPPLER_PATH
                )
            except Exception as e:
                print(f"[OCR RISK] Error with explicit poppler_path: {e}")
                try:
                    images = convert_from_path(normalized_path)
                except Exception as e2:
                    print(f"[OCR RISK] Error without poppler_path: {e2}")
                    raise
        else:
            print(f"[OCR RISK] Processing image: {normalized_path}")
            images = [Image.open(normalized_path)]

        # Process each page/image
        for idx, img in enumerate(images):
            print(f"[OCR RISK] Processing page/image {idx + 1}")
            text = pytesseract.image_to_string(img)
            
            print(f"[OCR RISK] Extracted text length: {len(text)} chars")
            
            lines = text.split('\n')
            for line in lines:
                lower = line.lower()
                numbers = [int(n) for n in re.findall(r'\d+', line)]
                
                # Look for debt-related keywords
                if any(k in lower for k in ['debt', 'loan', 'outstanding', 'liability', 'credit', 
                                            'dette', 'prêt', 'crédit', 'emprunt']) and numbers:
                    potential_debt = max(numbers)
                    if potential_debt > existing_debt:
                        existing_debt = potential_debt
                        print(f"[OCR RISK] Found debt: {existing_debt}")
                        
    except Exception as e:
        print(f"[OCR RISK ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

    # Fallback value
    if existing_debt == 0:
        existing_debt = 500

    return {"existing_debt": existing_debt}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "OCR Service",
        "version": "1.0"
    }), 200

@app.route('/commercial/<cin>', methods=['GET'])
def analyze_commercial(cin):
    """
    Analyze commercial/financial documents for a client by CIN
    GET /commercial/{cin}
    """
    print(f"\n{'='*60}")
    print(f"[COMMERCIAL] New request for CIN: {cin}")
    print(f"{'='*60}")
    
    # Find the file for this CIN in uploads folder
    uploads_folder = os.path.abspath(Config.UPLOADS_FOLDER)
    print(f"[COMMERCIAL] Looking in: {uploads_folder}")
    
    if not os.path.exists(uploads_folder):
        print(f"[COMMERCIAL] Uploads folder not found!")
        return jsonify({
            "error": "Uploads folder not found",
            "path": uploads_folder
        }), 500
    
    # Find file starting with CIN
    try:
        all_files = os.listdir(uploads_folder)
        user_files = [f for f in all_files if f.startswith(str(cin))]
        
        print(f"[COMMERCIAL] All files: {all_files}")
        print(f"[COMMERCIAL] User files: {user_files}")
    except Exception as e:
        print(f"[COMMERCIAL] Error listing files: {e}")
        return jsonify({"error": str(e)}), 500
    
    if not user_files:
        print(f"[COMMERCIAL] No file found for CIN: {cin}")
        return jsonify({
            "error": "No document found for this client",
            "cin": cin,
            "uploads_folder": uploads_folder
        }), 404
    
    # Use the first file
    file_path = os.path.join(uploads_folder, user_files[0])
    print(f"[COMMERCIAL] Processing file: {file_path}")
    
    try:
        # Extract income data
        result = extract_income_data(file_path)
        result['cin'] = cin
        result['file_processed'] = user_files[0]
        
        print(f"[COMMERCIAL] Analysis complete: {result}")
        print(f"{'='*60}\n")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[COMMERCIAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": "Failed to process document",
            "details": str(e)
        }), 500

@app.route('/risk/<cin>', methods=['GET'])
def analyze_risk(cin):
    """
    Analyze risk assessment documents for a client by CIN
    GET /risk/{cin}
    """
    print(f"\n{'='*60}")
    print(f"[RISK] New request for CIN: {cin}")
    print(f"{'='*60}")
    
    # Find the file for this CIN in uploads folder
    uploads_folder = os.path.abspath(Config.UPLOADS_FOLDER)
    print(f"[RISK] Looking in: {uploads_folder}")
    
    if not os.path.exists(uploads_folder):
        print(f"[RISK] Uploads folder not found!")
        return jsonify({
            "error": "Uploads folder not found",
            "path": uploads_folder
        }), 500
    
    # Find file starting with CIN
    try:
        all_files = os.listdir(uploads_folder)
        user_files = [f for f in all_files if f.startswith(str(cin))]
        
        print(f"[RISK] All files: {all_files}")
        print(f"[RISK] User files: {user_files}")
    except Exception as e:
        print(f"[RISK] Error listing files: {e}")
        return jsonify({"error": str(e)}), 500
    
    if not user_files:
        print(f"[RISK] No file found for CIN: {cin}")
        return jsonify({
            "error": "No document found for this client",
            "cin": cin,
            "uploads_folder": uploads_folder
        }), 404
    
    # Use the first file
    file_path = os.path.join(uploads_folder, user_files[0])
    print(f"[RISK] Processing file: {file_path}")
    
    try:
        # Extract debt data
        result = extract_debt_data(file_path)
        result['cin'] = cin
        result['file_processed'] = user_files[0]
        
        print(f"[RISK] Analysis complete: {result}")
        print(f"{'='*60}\n")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[RISK ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": "Failed to process document",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("OCR Microservice")
    print("=" * 60)
    
    # Setup configuration
    Config.setup()
    
    print(f"Uploads folder: {os.path.abspath(Config.UPLOADS_FOLDER)}")
    print(f"Tesseract: {Config.TESSERACT_CMD}")
    print(f"Poppler: {Config.POPPLER_PATH}")
    
    # Verify Poppler installation
    if os.path.exists(Config.POPPLER_PATH):
        pdftoppm = os.path.join(Config.POPPLER_PATH, 'pdftoppm.exe')
        pdfinfo = os.path.join(Config.POPPLER_PATH, 'pdfinfo.exe')
        print(f"pdftoppm.exe exists: {os.path.exists(pdftoppm)}")
        print(f"pdfinfo.exe exists: {os.path.exists(pdfinfo)}")
    else:
        print(f"⚠️  WARNING: Poppler folder not found!")
    
    print("=" * 60)
    print("Starting OCR service on http://localhost:5002")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health")
    print("  GET  /commercial/<cin>")
    print("  GET  /risk/<cin>")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host="0.0.0.0", port=5002)
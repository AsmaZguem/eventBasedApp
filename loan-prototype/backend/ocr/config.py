"""
config.py
Configuration settings for OCR processing
"""
import os
import sys

class Config:
    # Tesseract OCR executable path
    # Windows default installation path
    TESSERACT_CMD = r'C:\Users\LENOVO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    
    # Poppler path for PDF processing
    # Download from: https://github.com/oschwartz10612/poppler-windows/releases/
    # IMPORTANT: This should point to the bin folder containing pdftoppm.exe and pdfinfo.exe
    POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin'
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    
    @staticmethod
    def validate():
        """Validate that required tools are installed"""
        tesseract_ok = os.path.exists(Config.TESSERACT_CMD)
        poppler_ok = False
        
        if not tesseract_ok:
            print(f"⚠️  WARNING: Tesseract not found at {Config.TESSERACT_CMD}")
            print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        
        # Check if poppler bin folder exists and contains required executables
        if os.path.exists(Config.POPPLER_PATH):
            pdftoppm_path = os.path.join(Config.POPPLER_PATH, 'pdftoppm.exe')
            pdfinfo_path = os.path.join(Config.POPPLER_PATH, 'pdfinfo.exe')
            
            if os.path.exists(pdftoppm_path) and os.path.exists(pdfinfo_path):
                poppler_ok = True
                print(f"✓ Poppler found at {Config.POPPLER_PATH}")
            else:
                print(f"⚠️  WARNING: Poppler bin folder exists but executables not found")
                print(f"   Looking for: pdftoppm.exe and pdfinfo.exe")
                print(f"   In: {Config.POPPLER_PATH}")
        else:
            print(f"⚠️  WARNING: Poppler not found at {Config.POPPLER_PATH}")
            print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
            print("   Extract and update POPPLER_PATH to point to the bin folder")
        
        return tesseract_ok and poppler_ok
    
    @staticmethod
    def setup_poppler_path():
        """Add Poppler to system PATH if not already there"""
        if os.path.exists(Config.POPPLER_PATH):
            if Config.POPPLER_PATH not in os.environ['PATH']:
                os.environ['PATH'] = Config.POPPLER_PATH + os.pathsep + os.environ['PATH']
                print(f"✓ Added Poppler to PATH: {Config.POPPLER_PATH}")
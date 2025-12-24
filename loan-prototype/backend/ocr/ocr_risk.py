"""
ocr/ocr_risk.py
OCR processing for risk assessment document analysis
"""
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from config import Config
import re
import os

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_debt_data(file_path):
    """
    Extract debt/liability data from a document
    
    Args:
        file_path: Path to the document (PDF or image)
        
    Returns:
        dict: {"existing_debt": int}
    """
    existing_debt = 0

    try:
        normalized_path = os.path.normpath(file_path).replace('\\', '/')
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            print(f"[OCR RISK] File not found: {normalized_path}")
            return {"existing_debt": 500}
        
        # Convert PDF to images or open image directly
        if normalized_path.lower().endswith('.pdf'):
            print(f"[OCR RISK] Processing PDF: {normalized_path}")
            images = convert_from_path(normalized_path, poppler_path=Config.POPPLER_PATH.replace('\\', '/'))
        else:
            print(f"[OCR RISK] Processing image: {normalized_path}")
            images = [Image.open(normalized_path)]

        # Process each page/image
        for idx, img in enumerate(images):
            print(f"[OCR RISK] Processing page/image {idx + 1}")
            text = pytesseract.image_to_string(img)
            
            # Debug: print extracted text
            print(f"[OCR RISK] Extracted text length: {len(text)} chars")
            
            # Extract numbers from lines containing keywords
            lines = text.split('\n')
            for line in lines:
                lower = line.lower()
                # Find all numbers in the line
                numbers = [int(n) for n in re.findall(r'\d+', line)]
                
                # Look for debt-related keywords
                if any(k in lower for k in ['debt', 'loan', 'outstanding', 'liability', 'credit', 
                                            'dette', 'prêt', 'crédit', 'emprunt', 'passif']) and numbers:
                    potential_debt = max(numbers)
                    if potential_debt > existing_debt:
                        existing_debt = potential_debt
                        print(f"[OCR RISK] Found debt: {existing_debt} in line: {line.strip()}")
                        
    except Exception as e:
        print(f"[OCR RISK ERROR] {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()

    # Fallback value if nothing found
    if existing_debt == 0:
        print("[OCR RISK] No debt found, using fallback: 500")
        existing_debt = 500

    result = {"existing_debt": existing_debt}
    print(f"[OCR RISK] Final result: {result}")
    return result
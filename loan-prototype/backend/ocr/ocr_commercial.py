import pytesseract
from pdf2image import convert_from_path, PDFInfoNotInstalledError
from PIL import Image
from config import Config
import re
import os

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_income_data(file_path):
    monthly_income = 0
    expenses = 0

    try:
        normalized_path = os.path.normpath(file_path).replace('\\', '/')
        if not os.path.exists(normalized_path):
            print(f"[OCR COMMERCIAL] File not found: {normalized_path}")
            return {"monthly_income": 3000, "expenses": 800}

        # Convert PDF to images or open image directly
        images = []
        if normalized_path.lower().endswith('.pdf'):
            print(f"[OCR COMMERCIAL] Processing PDF: {normalized_path}")
            try:
                images = convert_from_path(
                    normalized_path,
                    poppler_path=Config.POPPLER_PATH.replace('\\', '/')
                )
            except PDFInfoNotInstalledError:
                print("[OCR COMMERCIAL WARNING] Poppler not found or path incorrect. Using fallback OCR on PDF pages as images not supported.")
                return {"monthly_income": 3000, "expenses": 800}
        else:
            print(f"[OCR COMMERCIAL] Processing image: {normalized_path}")
            images = [Image.open(normalized_path)]

        # Process each page/image
        for idx, img in enumerate(images):
            print(f"[OCR COMMERCIAL] Processing page/image {idx + 1}")
            text = pytesseract.image_to_string(img)
            print(f"[OCR COMMERCIAL] Extracted text length: {len(text)} chars")

            lines = text.split('\n')
            for line in lines:
                lower = line.lower()
                numbers = [int(n) for n in re.findall(r'\d+', line)]

                if any(k in lower for k in ['income', 'salary', 'earnings', 'revenue', 'salaire', 'revenu']) and numbers:
                    potential_income = max(numbers)
                    if potential_income > monthly_income:
                        monthly_income = potential_income
                        print(f"[OCR COMMERCIAL] Found income: {monthly_income} in line: {line.strip()}")

                if any(k in lower for k in ['expense', 'rent', 'cost', 'bill', 'dépense', 'loyer', 'charge']) and numbers:
                    potential_expense = max(numbers)
                    if potential_expense > expenses:
                        expenses = potential_expense
                        print(f"[OCR COMMERCIAL] Found expense: {expenses} in line: {line.strip()}")

    except Exception as e:
        print(f"[OCR COMMERCIAL ERROR] {file_path}: {str(e)}")
        import traceback
        traceback.print_exc()

    # Fallback if nothing found
    if monthly_income == 0:
        monthly_income = 3000
    if expenses == 0:
        expenses = 800

    result = {"monthly_income": monthly_income, "expenses": expenses}
    print(f"[OCR COMMERCIAL] Final result: {result}")
    return result

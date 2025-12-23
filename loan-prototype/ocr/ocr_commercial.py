import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from config import Config
import re
import os

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_income_data(file_paths):
    monthly_income = 0
    expenses = 0

    for path in file_paths:
        try:
            normalized_path = os.path.normpath(path).replace('\\', '/')
            if normalized_path.lower().endswith('.pdf'):
                images = convert_from_path(normalized_path, poppler_path=Config.POPPLER_PATH.replace('\\', '/'))
            else:
                images = [Image.open(normalized_path)]

            for img in images:
                text = pytesseract.image_to_string(img)

                # Simple number extraction near keywords
                lines = text.split('\n')
                for line in lines:
                    lower = line.lower()
                    numbers = [int(n) for n in re.findall(r'\d+', line) if n.isdigit()]

                    if any(k in lower for k in ['income', 'salary', 'earnings', 'revenue']) and numbers:
                        monthly_income = max(monthly_income, max(numbers))
                    if any(k in lower for k in ['expense', 'rent', 'cost', 'bill']) and numbers:
                        expenses = max(expenses, max(numbers))
        except Exception as e:
            print(f"[OCR COMMERCIAL ERROR] {path}: {e}")

    # Fallback if nothing found
    if monthly_income == 0:
        monthly_income = 3000
    if expenses == 0:
        expenses = 800

    return {"monthly_income": monthly_income, "expenses": expenses}
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from config import Config
import re

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

def extract_debt_data(file_paths):
    existing_debt = 0

    for path in file_paths:
        try:
            if path.lower().endswith('.pdf'):
                images = convert_from_path(path, poppler_path=Config.POPPLER_PATH)
            else:
                images = [Image.open(path)]

            for img in images:
                text = pytesseract.image_to_string(img)
                lines = text.split('\n')
                for line in lines:
                    lower = line.lower()
                    numbers = [int(n) for n in re.findall(r'\d+', line) if n.isdigit()]
                    if any(k in lower for k in ['debt', 'loan', 'outstanding', 'liability', 'credit']) and numbers:
                        existing_debt = max(existing_debt, max(numbers))
        except Exception as e:
            print(f"[OCR RISK ERROR] {path}: {e}")

    # Fallback
    if existing_debt == 0:
        existing_debt = 500

    return {"existing_debt": existing_debt}
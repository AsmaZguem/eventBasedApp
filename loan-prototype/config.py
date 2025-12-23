import os

class Config:
    # PostgreSQL
    DATABASE_URL = "postgresql://postgres:asma@localhost:5432/loan_app"  # Change password!

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'

    # Topics
    TOPICS = {
        "submitted": "LoanApplicationSubmitted",
        "commercial": "CommercialScoringCompleted",
        "risk": "RiskScoringCompleted",
        "credit": "CreditContractGenerated"
    }

    # Uploads
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Tesseract (usually auto-detected if in PATH)
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Optional if PATH set

    # Poppler (for pdf2image)
    POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin'  
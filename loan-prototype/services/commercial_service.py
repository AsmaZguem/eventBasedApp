from event_bus.kafka_client import subscribe, publish
from ocr.ocr_commercial import extract_income_data
from database.db import update_application
from config import Config

def process_application(data):
    print(f"[COMMERCIAL] Processing {data['app_id']}")
    income_data = extract_income_data(data["documents"])
    score = income_data["monthly_income"] - income_data["expenses"]

    update_application(data["app_id"], {
        "commercial_score": score,
        "status": "COMMERCIAL_COMPLETED"
    })

    result = {
        "app_id": data["app_id"],
        "commercial_score": score
    }
    publish(Config.TOPICS["commercial"], result)

def init():
    subscribe(Config.TOPICS["submitted"], process_application)
    print("[COMMERCIAL] Service initialized")
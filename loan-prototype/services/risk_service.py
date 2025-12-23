from event_bus.kafka_client import subscribe, publish
from ocr.ocr_risk import extract_debt_data
from database.db import update_application
from config import Config

def process_risk(data):
    print(f"[RISK] Processing {data['app_id']}")
    debt_data = extract_debt_data([])  # No extra files needed, using fallback or logic

    final_score = data["commercial_score"] - debt_data["existing_debt"]
    decision = "APPROVED" if final_score > 1000 else "REJECTED"

    update_application(data["app_id"], {
        "risk_decision": decision,
        "status": f"RISK_{decision}"
    })

    publish(Config.TOPICS["risk"], {
        "app_id": data["app_id"],
        "decision": decision
    })

def init():
    subscribe(Config.TOPICS["commercial"], process_risk)
    print("[RISK] Service initialized")
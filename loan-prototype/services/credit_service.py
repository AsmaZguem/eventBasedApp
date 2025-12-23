from event_bus.kafka_client import subscribe, publish
from database.db import update_application
from config import Config

def generate_contract(data):
    if data["decision"] == "APPROVED":
        print(f"[CREDIT] Generating contract for {data['app_id']}")
        contract = "Simulated Loan Contract PDF - Approved"

        update_application(data["app_id"], {
            "credit_contract": contract,
            "status": "CONTRACT_GENERATED"
        })

        publish(Config.TOPICS["credit"], {
            "app_id": data["app_id"],
            "contract": contract
        })

def init():
    subscribe(Config.TOPICS["risk"], generate_contract)
    print("[CREDIT] Service initialized")
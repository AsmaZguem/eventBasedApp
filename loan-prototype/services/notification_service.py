from event_bus.kafka_client import subscribe
from database.db import update_application
from config import Config

def notify_risk(data):
    print(f"[NOTIFICATION] Risk decision: {data['decision']} for {data['app_id']}")
    update_application(data["app_id"], {"status": f"NOTIFIED_{data['decision']}"})

def notify_contract(data):
    print(f"[NOTIFICATION] Contract ready for {data['app_id']}")

def init():
    subscribe(Config.TOPICS["risk"], notify_risk)
    subscribe(Config.TOPICS["credit"], notify_contract)
    print("[NOTIFICATION] Service initialized")
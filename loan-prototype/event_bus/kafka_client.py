from confluent_kafka import Producer, Consumer
import json
import threading
from config import Config

producer = Producer({'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS})

def publish(topic, data):
    try:
        producer.produce(topic, json.dumps(data).encode('utf-8'))
        producer.flush()
        print(f"[KAFKA] Published to {topic}")
    except Exception as e:
        print(f"[KAFKA ERROR] {e}")

def subscribe(topic, handler):
    def run():
        consumer = Consumer({
            'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'loan-group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe([topic])
        print(f"[KAFKA] Subscribed to {topic}")
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"[KAFKA ERROR] {msg.error()}")
                continue
            try:
                data = json.loads(msg.value().decode('utf-8'))
                handler(data)
            except Exception as e:
                print(f"[KAFKA HANDLER ERROR] {e}")
    threading.Thread(target=run, daemon=True).start()
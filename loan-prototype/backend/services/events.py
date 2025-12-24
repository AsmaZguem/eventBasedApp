"""
services/events.py
Kafka event producer and consumer utilities
"""

from confluent_kafka import Producer, Consumer, KafkaError
import json
import socket

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'

# Topics - matching your existing Kafka topics
TOPIC_LOAN_SUBMITTED = 'LoanApplicationSubmitted'
TOPIC_COMMERCIAL_COMPLETED = 'CommercialScoringCompleted'
TOPIC_RISK_COMPLETED = 'RiskScoringCompleted'
TOPIC_CONTRACT_GENERATED = 'CreditContractGenerated'
TOPIC_NOTIFICATION = 'NotificationCompleted'

def get_kafka_producer():
    """Get Kafka producer instance"""
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': socket.gethostname()
    }
    return Producer(conf)

def get_kafka_consumer(group_id, topics):
    """Get Kafka consumer instance"""
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    consumer = Consumer(conf)
    consumer.subscribe(topics)
    return consumer

def delivery_report(err, msg):
    """Callback for message delivery reports"""
    if err is not None:
        print(f'❌ Message delivery failed: {err}')
    else:
        print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}]')

def publish_event(producer, topic, event_data):
    """Publish an event to Kafka"""
    try:
        producer.produce(
            topic,
            key=str(event_data.get('cin', '')),
            value=json.dumps(event_data),
            callback=delivery_report
        )
        producer.flush()
        return True
    except Exception as e:
        print(f'❌ Error publishing event: {e}')
        return False

def publish_loan_submitted(cin, loan_amount, duration):
    """Publish loan submitted event to LoanApplicationSubmitted"""
    producer = get_kafka_producer()
    event = {
        'event_type': 'LOAN_SUBMITTED',
        'cin': cin,
        'loan_amount': loan_amount,
        'loan_duration_months': duration,
        'status': 'PENDING',
        'timestamp': str(int(__import__('time').time()))
    }
    return publish_event(producer, TOPIC_LOAN_SUBMITTED, event)

def publish_commercial_completed(cin, commercial_score, monthly_income, expenses, loan_amount, duration):
    """Publish commercial analysis completed event to CommercialScoringCompleted"""
    producer = get_kafka_producer()
    event = {
        'event_type': 'COMMERCIAL_COMPLETED',
        'cin': cin,
        'commercial_score': commercial_score,
        'monthly_income': monthly_income,
        'expenses': expenses,
        'loan_amount': loan_amount,
        'loan_duration_months': duration,
        'timestamp': str(int(__import__('time').time()))
    }
    return publish_event(producer, TOPIC_COMMERCIAL_COMPLETED, event)

def publish_risk_completed(cin, risk_score, existing_debt, has_unpaid_commitments, commercial_score, monthly_income, expenses, loan_amount, duration):
    """Publish risk analysis completed event to RiskScoringCompleted"""
    producer = get_kafka_producer()
    event = {
        'event_type': 'RISK_COMPLETED',
        'cin': cin,
        'risk_score': risk_score,
        'existing_debt': existing_debt,
        'has_unpaid_commitments': has_unpaid_commitments,
        'commercial_score': commercial_score,
        'monthly_income': monthly_income,
        'expenses': expenses,
        'loan_amount': loan_amount,
        'loan_duration_months': duration,
        'timestamp': str(int(__import__('time').time()))
    }
    return publish_event(producer, TOPIC_RISK_COMPLETED, event)

def publish_contract_generated(cin, is_approved, final_score, reason, contract_path=None, amortization_path=None):
    """Publish contract generated event to CreditContractGenerated"""
    producer = get_kafka_producer()
    event = {
        'event_type': 'CONTRACT_GENERATED',
        'cin': cin,
        'is_approved': is_approved,
        'final_score': final_score,
        'reason': reason,
        'contract_path': contract_path,
        'amortization_path': amortization_path,
        'timestamp': str(int(__import__('time').time()))
    }
    return publish_event(producer, TOPIC_CONTRACT_GENERATED, event)

def publish_notification(cin, is_approved, message):
    """Publish notification event to NotificationCompleted"""
    producer = get_kafka_producer()
    event = {
        'event_type': 'NOTIFICATION_SENT',
        'cin': cin,
        'is_approved': is_approved,
        'message': message,
        'timestamp': str(int(__import__('time').time()))
    }
    return publish_event(producer, TOPIC_NOTIFICATION, event)
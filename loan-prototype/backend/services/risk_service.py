"""
services/risk_service.py
Risk Management Service - Analyzes debt and repayment capability
Listens to: CommercialScoringCompleted
Publishes to: RiskScoringCompleted
"""

import requests
import json
from events import get_kafka_consumer, publish_risk_completed
from confluent_kafka import KafkaError

# Service URLs
OCR_SERVICE_URL = 'http://localhost:5002'
CENTRAL_BANK_URL = 'http://localhost:5000'

def calculate_risk_score(existing_debt, monthly_income, expenses, has_unpaid_commitments):
    """
    Calculate risk score based on debt and commitments
    Score range: 0-100
    
    Simple formula:
    - Total monthly obligations = expenses + existing_debt
    - Debt ratio = total obligations / monthly_income
    - Lower score if has unpaid commitments
    """
    total_obligations = expenses + existing_debt
    debt_ratio = (total_obligations / monthly_income) * 100 if monthly_income > 0 else 100
    
    # Base score starts at 100
    score = 100
    
    # Penalize based on debt ratio
    if debt_ratio > 70:
        score -= 60  # Very high risk
    elif debt_ratio > 60:
        score -= 45
    elif debt_ratio > 50:
        score -= 30
    elif debt_ratio > 40:
        score -= 15
    
    # Heavy penalty for unpaid commitments
    if has_unpaid_commitments:
        score -= 40
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    print(f"📊 Risk Analysis:")
    print(f"   Monthly Income: {monthly_income}")
    print(f"   Expenses: {expenses}")
    print(f"   Existing Debt: {existing_debt}")
    print(f"   Total Obligations: {total_obligations}")
    print(f"   Debt Ratio: {debt_ratio:.2f}%")
    print(f"   Unpaid Commitments: {'Yes' if has_unpaid_commitments else 'No'}")
    print(f"   Risk Score: {score}")
    
    return score

def check_central_bank(cin):
    """Check central bank for unpaid commitments"""
    try:
        print(f"📞 Calling Central Bank API: {CENTRAL_BANK_URL}/api/credit-check/{cin}")
        response = requests.get(f"{CENTRAL_BANK_URL}/api/credit-check/{cin}", timeout=5)
        
        if response.status_code == 200:
            result = response.text.strip().lower()
            has_unpaid = result == 'true'
            print(f"✅ Central Bank response: {result} (has unpaid: {has_unpaid})")
            return has_unpaid
        else:
            print(f"⚠️ Central Bank returned {response.status_code}, assuming no unpaid commitments")
            return False
            
    except Exception as e:
        print(f"❌ Central Bank check error: {e}")
        return False

def analyze_risk(cin, monthly_income, expenses, commercial_score, loan_amount, duration):
    """
    Analyze risk by:
    1. Calling OCR service to extract debt data
    2. Checking central bank for unpaid commitments
    3. Calculating risk score
    4. Publishing result to RiskScoringCompleted
    """
    print(f"\n{'='*60}")
    print(f"⚠️ RISK SERVICE - Analyzing CIN: {cin}")
    print(f"{'='*60}")
    
    try:
        # Call OCR service to extract debt data
        print(f"📞 Calling OCR service: {OCR_SERVICE_URL}/risk/{cin}")
        response = requests.get(f"{OCR_SERVICE_URL}/risk/{cin}", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ OCR service error: {response.status_code}")
            existing_debt = 500
            print(f"⚠️ Using fallback debt value: {existing_debt}")
        else:
            ocr_data = response.json()
            print(f"✅ OCR data received: {ocr_data}")
            existing_debt = ocr_data.get('existing_debt', 500)
        
        # Check central bank
        has_unpaid_commitments = check_central_bank(cin)
        
        # Calculate risk score
        risk_score = calculate_risk_score(
            existing_debt, 
            monthly_income, 
            expenses, 
            has_unpaid_commitments
        )
        
        # Publish risk completed event to RiskScoringCompleted
        print(f"📤 Publishing to RiskScoringCompleted...")
        success = publish_risk_completed(
            cin, 
            risk_score, 
            existing_debt, 
            has_unpaid_commitments,
            commercial_score,
            monthly_income,
            expenses,
            loan_amount,
            duration
        )
        
        if success:
            print(f"✅ Risk analysis completed - Score: {risk_score}")
        else:
            print(f"❌ Failed to publish risk event")
        
        print(f"{'='*60}\n")
        return success
        
    except Exception as e:
        print(f"❌ Risk service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_risk_service():
    """Run the risk management service consumer"""
    print("=" * 60)
    print("⚠️ RISK MANAGEMENT SERVICE STARTING")
    print("=" * 60)
    print("Listening to: CommercialScoringCompleted")
    print("Publishing to: RiskScoringCompleted")
    print("=" * 60 + "\n")
    
    consumer = get_kafka_consumer('risk-service-group', ['CommercialScoringCompleted'])
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"❌ Consumer error: {msg.error()}")
                    break
            
            # Process message
            try:
                event_data = json.loads(msg.value().decode('utf-8'))
                print(f"\n📨 Received event from CommercialScoringCompleted")
                print(f"   Event type: {event_data.get('event_type', 'UNKNOWN')}")
                
                cin = event_data.get('cin')
                monthly_income = event_data.get('monthly_income')
                expenses = event_data.get('expenses')
                commercial_score = event_data.get('commercial_score')
                loan_amount = event_data.get('loan_amount')
                duration = event_data.get('loan_duration_months')
                
                if cin and monthly_income and expenses and commercial_score is not None:
                    analyze_risk(cin, float(monthly_income), float(expenses), 
                               float(commercial_score), float(loan_amount), int(duration))
                else:
                    print(f"❌ Invalid event data: missing required fields")
                    print(f"   Received: {event_data}")
                    
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\n🛑 Risk service shutting down...")
    finally:
        consumer.close()

if __name__ == '__main__':
    run_risk_service()
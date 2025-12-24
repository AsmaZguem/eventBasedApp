"""
services/commercial_service.py
Commercial Service - Analyzes borrower eligibility and income
Listens to: LoanApplicationSubmitted
Publishes to: CommercialScoringCompleted
"""

import requests
import json
from events import get_kafka_consumer, publish_commercial_completed
from confluent_kafka import KafkaError

# OCR Service URL
OCR_SERVICE_URL = 'http://localhost:5002'

def calculate_commercial_score(monthly_income, expenses, loan_amount, duration):
    """
    Calculate commercial score based on income and expenses
    Score range: 0-100
    
    Simple formula:
    - Disposable income = monthly_income - expenses
    - Monthly payment = loan_amount / duration
    - Debt-to-income ratio = monthly_payment / monthly_income
    - Score decreases as debt-to-income increases
    """
    disposable_income = monthly_income - expenses
    monthly_payment = loan_amount / duration
    
    # Calculate debt-to-income ratio
    debt_to_income = (monthly_payment / monthly_income) * 100 if monthly_income > 0 else 100
    
    # Base score starts at 100
    score = 100
    
    # Penalize based on debt-to-income ratio
    if debt_to_income > 50:
        score -= 50  # Very high ratio
    elif debt_to_income > 40:
        score -= 40
    elif debt_to_income > 30:
        score -= 25
    elif debt_to_income > 20:
        score -= 10
    
    # Bonus if disposable income is high
    if disposable_income > monthly_payment * 2:
        score += 10
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    print(f"📊 Commercial Analysis:")
    print(f"   Monthly Income: {monthly_income}")
    print(f"   Expenses: {expenses}")
    print(f"   Disposable Income: {disposable_income}")
    print(f"   Monthly Payment: {monthly_payment:.2f}")
    print(f"   Debt-to-Income Ratio: {debt_to_income:.2f}%")
    print(f"   Commercial Score: {score}")
    
    return score

def analyze_commercial(cin, loan_amount, duration):
    """
    Analyze commercial eligibility by:
    1. Calling OCR service to extract income data
    2. Calculating commercial score
    3. Publishing result to CommercialScoringCompleted
    """
    print(f"\n{'='*60}")
    print(f"🏦 COMMERCIAL SERVICE - Analyzing CIN: {cin}")
    print(f"{'='*60}")
    
    try:
        # Call OCR service to extract income data
        print(f"📞 Calling OCR service: {OCR_SERVICE_URL}/commercial/{cin}")
        response = requests.get(f"{OCR_SERVICE_URL}/commercial/{cin}", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ OCR service error: {response.status_code}")
            # Use fallback values
            monthly_income = 3000
            expenses = 800
            print(f"⚠️  Using fallback values: income={monthly_income}, expenses={expenses}")
        else:
            ocr_data = response.json()
            print(f"✅ OCR data received: {ocr_data}")
            monthly_income = ocr_data.get('monthly_income', 3000)
            expenses = ocr_data.get('expenses', 800)
        
        # Calculate commercial score
        commercial_score = calculate_commercial_score(
            monthly_income, 
            expenses, 
            loan_amount, 
            duration
        )
        
        # Publish commercial completed event to CommercialScoringCompleted
        print(f"📤 Publishing to CommercialScoringCompleted...")
        success = publish_commercial_completed(
            cin, 
            commercial_score, 
            monthly_income, 
            expenses,
            loan_amount,
            duration
        )
        
        if success:
            print(f"✅ Commercial analysis completed - Score: {commercial_score}")
        else:
            print(f"❌ Failed to publish commercial event")
        
        print(f"{'='*60}\n")
        return success
        
    except Exception as e:
        print(f"❌ Commercial service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_commercial_service():
    """Run the commercial service consumer"""
    print("=" * 60)
    print("🏦 COMMERCIAL SERVICE STARTING")
    print("=" * 60)
    print("Listening to: LoanApplicationSubmitted")
    print("Publishing to: CommercialScoringCompleted")
    print("=" * 60 + "\n")
    
    consumer = get_kafka_consumer('commercial-service-group', ['LoanApplicationSubmitted'])
    
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
                print(f"\n📨 Received event from LoanApplicationSubmitted")
                print(f"   Event type: {event_data.get('event_type', 'UNKNOWN')}")
                
                cin = event_data.get('cin')
                loan_amount = event_data.get('loan_amount')
                duration = event_data.get('loan_duration_months')
                
                if cin and loan_amount and duration:
                    analyze_commercial(cin, float(loan_amount), int(duration))
                else:
                    print(f"❌ Invalid event data: missing required fields")
                    print(f"   Received: {event_data}")
                    
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\n🛑 Commercial service shutting down...")
    finally:
        consumer.close()

if __name__ == '__main__':
    run_commercial_service()
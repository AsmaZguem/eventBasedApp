"""
credit_service.py
Credit Service - Makes final decision and generates documents
Listens to: RiskScoringCompleted
Publishes to: CreditContractGenerated
"""

import json
import os
import sys
from datetime import datetime

# Add database directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.loan_db import save_loan_application
from events import get_kafka_consumer, publish_contract_generated
from confluent_kafka import KafkaError

# --------------------------
# Helper Functions
# --------------------------

# In credit_service.py
def sanitize_for_db(s):
    if s is None:
        return None
    # Change 'ignore' to 'replace' or just use this:
    return s.encode('ascii', 'ignore').decode('ascii')


def calculate_monthly_payment(loan_amount, duration, annual_interest_rate=5.0):
    """Calculate monthly payment using amortization formula"""
    if annual_interest_rate == 0:
        return loan_amount / duration
    monthly_rate = annual_interest_rate / 12 / 100
    n = duration
    payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    return round(payment, 2)


def calculate_final_score(commercial_score, risk_score):
    """Weighted average: 60% commercial, 40% risk"""
    final_score = (commercial_score * 0.6) + (risk_score * 0.4)
    return round(final_score, 2)


def make_loan_decision(final_score):
    """Decide if loan should be approved"""
    is_approved = final_score >= 60
    if final_score >= 80:
        reason = "Excellent financial profile"
    elif final_score >= 70:
        reason = "Good financial standing"
    elif final_score >= 60:
        reason = "Acceptable financial conditions"
    elif final_score >= 40:
        reason = "Insufficient income or high debt ratio"
    else:
        reason = "High risk - unpaid commitments or excessive debt"
    return is_approved, reason


def generate_contract(cin, loan_amount, duration, monthly_payment, annual_interest_rate=5.0):
    """Generate loan contract document"""
    total_repayment = monthly_payment * duration
    total_interest = total_repayment - loan_amount
    contract = f"""
{'='*70}
                    LOAN AGREEMENT CONTRACT
{'='*70}

Contract Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Contract Number: LOAN-{cin}-{datetime.now().strftime('%Y%m%d%H%M%S')}

BORROWER INFORMATION:
  National ID (CIN): {cin}

LOAN DETAILS:
  Principal Amount: {loan_amount:,.2f} TND
  Annual Interest Rate: {annual_interest_rate}%
  Loan Duration: {duration} months
  Monthly Payment: {monthly_payment:,.2f} TND
  Total Interest: {total_interest:,.2f} TND
  Total Repayment: {total_repayment:,.2f} TND

TERMS AND CONDITIONS:
1. LOAN DISBURSEMENT
   The Bank agrees to provide the Borrower with a loan amount of 
   {loan_amount:,.2f} TND to be disbursed upon signing this agreement.

2. REPAYMENT SCHEDULE
   The Borrower agrees to repay the loan in {duration} equal monthly 
   installments of {monthly_payment:,.2f} TND each, starting from the 
   month following the loan disbursement.

3. INTEREST RATE
   The loan carries an annual interest rate of {annual_interest_rate}%, 
   calculated on the outstanding balance.

4. PAYMENT DUE DATE
   Each monthly installment is due on the same day of each month as 
   specified in the amortization schedule.

5. LATE PAYMENT
   Late payments may incur additional fees and penalties as per the 
   Bank's policies.

6. EARLY REPAYMENT
   The Borrower may repay the loan in full or in part before the 
   scheduled end date without incurring early repayment penalties.

7. DEFAULT
   Failure to make payments as scheduled may result in legal action 
   and damage to the Borrower's credit rating.

8. GOVERNING LAW
   This agreement is governed by the laws of Tunisia.

ACKNOWLEDGMENT:
By signing below, both parties acknowledge that they have read, 
understood, and agree to the terms and conditions outlined in this 
loan agreement.

SIGNATURES:
Bank Representative: _________________________  Date: __________
Name: INSATx Bank Officer
Title: Credit Manager

Borrower: ___________________________________  Date: __________
Name: [To be filled]
CIN: {cin}

{'='*70}
                    END OF CONTRACT
{'='*70}
"""
    return contract


def generate_amortization_table(loan_amount, duration, annual_interest_rate=5.0):
    """Generate detailed amortization table"""
    monthly_payment = calculate_monthly_payment(loan_amount, duration, annual_interest_rate)
    monthly_rate = annual_interest_rate / 12 / 100
    balance = loan_amount
    table = f"{'='*80}\nAMORTIZATION TABLE\n{'='*80}\n"
    table += f"{'Month':<8} {'Payment':>12} {'Interest':>12} {'Principal':>12} {'Balance':>12}\n"
    table += '-'*80 + '\n'
    for month in range(1, duration + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        if month == duration:
            principal_payment = balance
            interest_payment = monthly_payment - principal_payment
        balance -= principal_payment
        table += f"{month:<8} {monthly_payment:>12,.2f} {interest_payment:>12,.2f} {principal_payment:>12,.2f} {max(0, balance):>12,.2f}\n"
    table += '-'*80 + '\n'
    table += f"{'TOTALS':<8} {monthly_payment * duration:>12,.2f} {monthly_payment * duration - loan_amount:>12,.2f} {loan_amount:>12,.2f}\n"
    table += '='*80 + '\n'
    return table


def save_documents(cin, contract, amortization):
    """Save contract and amortization table to files"""
    docs_folder = os.path.join(os.path.dirname(__file__), '..', 'loan_documents')
    os.makedirs(docs_folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    contract_path = os.path.join(docs_folder, f'{cin}_contract_{timestamp}.txt')
    amortization_path = os.path.join(docs_folder, f'{cin}_amortization_{timestamp}.txt')
    with open(contract_path, 'w', encoding='utf-8') as f:
        f.write(contract)
    with open(amortization_path, 'w', encoding='utf-8') as f:
        f.write(amortization)
    return contract_path, amortization_path


# --------------------------
# Loan Processing
# --------------------------

def process_loan_decision(cin, commercial_score, risk_score, loan_amount, duration,
                          monthly_income, expenses):
    """Make final loan decision and save to DB with sanitized data"""
    print("\n" + "="*60)
    print(f"💰 CREDIT SERVICE - Processing loan for CIN: {cin}")
    print("="*60)

    final_score = calculate_final_score(commercial_score, risk_score)
    is_approved, reason = make_loan_decision(final_score)
    monthly_payment = 0
    annual_interest_rate = 5.0
    contract_path = None
    amortization_path = None

    if is_approved:
        monthly_payment = calculate_monthly_payment(loan_amount, duration, annual_interest_rate)
        contract = generate_contract(cin, loan_amount, duration, monthly_payment, annual_interest_rate)
        amortization = generate_amortization_table(loan_amount, duration, annual_interest_rate)
        contract_path, amortization_path = save_documents(cin, contract, amortization)

    # --------------------------
    # SANITIZE STRING FIELDS BEFORE DB
    # --------------------------
    cin_safe = sanitize_for_db(cin)
    contract_path_safe = sanitize_for_db(contract_path)
    amortization_path_safe = sanitize_for_db(amortization_path)
    reason_safe = sanitize_for_db(reason)

    # Save to DB
    print("\n💾 Saving loan to database...")
    try:
        saved = save_loan_application(
            cin=cin_safe,
            loan_amount=loan_amount,
            duration=duration,
            monthly_payment=monthly_payment,
            interest_rate=annual_interest_rate,
            status='APPROVED' if is_approved else 'REJECTED',
            commercial_score=commercial_score,
            risk_score=risk_score,
            final_score=final_score,
            monthly_income=monthly_income,
            expenses=expenses,
            contract_path=contract_path_safe,
            amortization_path=amortization_path_safe,
            rejection_reason=None if is_approved else reason_safe
        )
        if saved:
            print("✅ Loan saved successfully")
        else:
            print("⚠️ Failed to save loan")
    except Exception as e:
        print(f"[DB] ❌ Error saving loan: {e}")

    # Publish Kafka event
    print("\n📤 Publishing to CreditContractGenerated...")
    publish_contract_generated(cin_safe, is_approved, final_score, reason_safe, contract_path_safe, amortization_path_safe)
    print("✅ Contract event published")
    print("="*60 + "\n")
    return True


# --------------------------
# Kafka Consumer
# --------------------------

def run_credit_service():
    print("="*60)
    print("💰 CREDIT SERVICE STARTING")
    print("="*60)
    print("Listening to: RiskScoringCompleted")
    print("Publishing to: CreditContractGenerated")
    print("="*60 + "\n")

    consumer = get_kafka_consumer('credit-service-group', ['RiskScoringCompleted'])

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
            try:
                event_data = json.loads(msg.value().decode('utf-8'))
                cin = event_data.get('cin')
                commercial_score = float(event_data.get('commercial_score', 0))
                risk_score = float(event_data.get('risk_score', 0))
                loan_amount = float(event_data.get('loan_amount', 0))
                duration = int(event_data.get('loan_duration_months', 0))
                monthly_income = float(event_data.get('monthly_income', 0))
                expenses = float(event_data.get('expenses', 0))
                process_loan_decision(cin, commercial_score, risk_score, loan_amount, duration, monthly_income, expenses)
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
    except KeyboardInterrupt:
        print("\n🛑 Credit service shutting down...")
    finally:
        consumer.close()


# --------------------------
# Main
# --------------------------
if __name__ == '__main__':
    run_credit_service()

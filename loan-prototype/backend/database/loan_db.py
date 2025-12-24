import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import sys

if sys.platform == "win32":
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ["PGCLIENTENCODING"] = "UTF8"

DB_CONFIG = {
    "host": "localhost",
    "database": "loandb",
    "user": "postgres",
    "password": "admin",
    "port": 5432,
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def save_loan_application(
    cin, loan_amount, duration, monthly_payment, interest_rate,
    status, commercial_score, risk_score, final_score,
    monthly_income, expenses,
    contract_path=None, amortization_path=None, rejection_reason=None
):

    is_approved = (status.upper() == 'APPROVED')

    data_to_save = (
        str(cin),
        float(loan_amount),
        int(duration),
        str(status),
        float(commercial_score) if commercial_score is not None else None,
        float(risk_score) if risk_score is not None else None,
        float(final_score) if final_score is not None else None,
        is_approved,
        str(contract_path) if contract_path else None,
        str(amortization_path) if amortization_path else None
    )

    query = """
        INSERT INTO loans (
            cin, 
            loan_amount, 
            loan_duration_months, 
            status,
            commercial_score, 
            risk_score, 
            final_score, 
            is_approved,
            contract_path, 
            amortization_path
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()
        cursor.execute(query, data_to_save)
        conn.commit()
        print("[DB] SUCCESS: Loan saved successfully")
        return True
    except Exception as e:
        print(f"[DB] ERROR saving loan: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def get_loans_by_cin(cin):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT *
            FROM loans
            WHERE cin = %s
            ORDER BY created_at DESC
        """, (str(cin),))
        return cur.fetchall()
    except Exception as e:
        print("[DB] ERROR fetching loans:", e)
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_loan_by_id(loan_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT *
            FROM loans
            WHERE loan_id = %s
        """, (int(loan_id),))
        row = cur.fetchone()
        return row
    except Exception as e:
        print("[DB] ERROR fetching loan by id:", e)
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_approved_loans_by_cin(cin):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT *
            FROM loans
            WHERE cin = %s AND status = 'APPROVED'
            ORDER BY created_at DESC
        """, (str(cin),))
        return cur.fetchall()
    except Exception as e:
        print("[DB] ERROR fetching approved loans:", e)
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_loan_status(loan_id, new_status):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE loans
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE loan_id = %s
        """, (str(new_status), int(loan_id)))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("[DB] ERROR updating loan status:", e)
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
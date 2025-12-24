import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Database configuration - use environment variables in production
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'bank_db'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'admin'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

def get_db_connection():
    """Get database connection"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def get_client_by_cin(cin):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT cin, name, email FROM clients WHERE cin = %s",
            (cin,)
        )
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    except psycopg2.Error as e:
        print(f"Database error in get_client_by_cin: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_client_by_email(email):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT cin, name, email, password FROM clients WHERE email = %s",
            (email,)
        )
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    except psycopg2.Error as e:
        print(f"Database error in get_client_by_email: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verify_login(email, password):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT cin, name, email FROM clients WHERE email = %s AND password = %s",
            (email, password)
        )
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    except psycopg2.Error as e:
        print(f"Database error in verify_login: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_accounts_by_cin(cin):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT account_number, cin, amount, account_type FROM accounts WHERE cin = %s",
            (cin,)
        )
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    except psycopg2.Error as e:
        print(f"Database error in get_accounts_by_cin: {e}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_account_by_number(account_number):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT account_number, cin, amount, account_type FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    except psycopg2.Error as e:
        print(f"Database error in get_account_by_number: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_account_balance(account_number, new_amount):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE accounts SET amount = %s WHERE account_number = %s",
            (new_amount, account_number)
        )
        
        conn.commit()
        success = cursor.rowcount > 0
        
        return success
    
    except psycopg2.Error as e:
        print(f"Database error in update_account_balance: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_all_clients():

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT cin, name, email FROM clients ORDER BY cin")
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    except psycopg2.Error as e:
        print(f"Database error in get_all_clients: {e}")
        return []
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'database': 'central_bank',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def get_customer_by_cin(cin):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT cin, has_unpaid_commitments FROM customers WHERE cin = %s",
            (cin,)
        )
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return {
                'cin': row['cin'],
                'has_unpaid_commitments': bool(row['has_unpaid_commitments'])
            }
        return None
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'host': 'localhost',
    'database': 'central_bank',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}

def create_database():
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                cin TEXT PRIMARY KEY,
                has_unpaid_commitments INTEGER NOT NULL
            )
        """)
        
        cursor.execute("DELETE FROM customers")
        
        users = [
            ('11111111', 0), 
            ('11111112', 1), 
            ('11111113', 1), 
            ('11111114', 0)   
        ]
        
        cursor.executemany(
            "INSERT INTO customers (cin, has_unpaid_commitments) VALUES (%s, %s)",
            users
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully!")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"Added {len(users)} customers")
        print("\nCustomers:")
        for cin, status in users:
            print(f"  CIN: {cin} - Unpaid Commitments: {'Yes' if status else 'No'}")
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        print("\nMake sure PostgreSQL is running and database 'central_bank' exists.")
        print("Create it with: CREATE DATABASE central_bank;")

if __name__ == '__main__':
    create_database()
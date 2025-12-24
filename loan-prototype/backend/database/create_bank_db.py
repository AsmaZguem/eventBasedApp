

import psycopg2
from psycopg2 import sql
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'bank_db',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}

def create_database():
    """Create bank database and populate with users and accounts"""
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                cin TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                cin TEXT NOT NULL,
                amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
                account_type TEXT NOT NULL,
                FOREIGN KEY (cin) REFERENCES clients(cin) ON DELETE CASCADE
            )
        """)
        
        # Clear existing data (optional)
        cursor.execute("DELETE FROM accounts")
        cursor.execute("DELETE FROM clients")
        
        # Insert 4 clients
        clients = [
            ('11111111', 'Ali Kallel', 'ali.kallel@insat.ucar.tn', 'password1'),
            ('11111112', 'Asma Zguem', 'asma.zguem@insat.ucar.tn', 'password2'),
            ('11111113', 'Mohamed Malek Gharbi', 'malek.gharbi@insat.ucar.tn', 'password3'),
            ('11111114', 'Mohamed Karrab', 'mohamed.karrab@insat.ucar.tn', 'password4')
        ]
        
        cursor.executemany(
            "INSERT INTO clients (cin, name, email, password) VALUES (%s, %s, %s, %s)",
            clients
        )
        
        # Insert accounts for each client
        accounts = [
            ('TN5901000000111111111111', '11111111', 5000.00, 'courant'),
            ('TN5901000000111111121112', '11111112', 3500.50, 'courant'),
            ('TN5901000000111111131113', '11111113', 1200.75, 'courant'),
            ('TN5901000000111111141114', '11111114', 8750.00, 'courant')
        ]
        
        cursor.executemany(
            "INSERT INTO accounts (account_number, cin, amount, account_type) VALUES (%s, %s, %s, %s)",
            accounts
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Bank database setup completed successfully!")
        print(f"✓ Database: {DB_CONFIG['database']}")
        print(f"✓ Added {len(clients)} clients")
        print(f"✓ Added {len(accounts)} accounts")
        
        print("\n" + "=" * 70)
        print("CLIENTS:")
        print("=" * 70)
        for cin, name, email, password in clients:
            print(f"CIN: {cin}")
            print(f"  Name: {name}")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print()
        
        print("=" * 70)
        print("ACCOUNTS:")
        print("=" * 70)
        for acc_num, cin, amount, acc_type in accounts:
            client_name = next(c[1] for c in clients if c[0] == cin)
            print(f"Account: {acc_num}")
            print(f"  Client: {client_name} (CIN: {cin})")
            print(f"  Type: {acc_type}")
            print(f"  Balance: {amount:,.2f} TND")
            print()
    
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        print("\nMake sure PostgreSQL is running and database 'bank_db' exists.")
        print("Create it with: CREATE DATABASE bank_db;")

if __name__ == '__main__':
    create_database()
"""
recreate_loan_database.py
Run this script to DROP and recreate the loan database with correct schema
WARNING: This will DELETE all existing loan data!
"""
import psycopg2
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}

def recreate_database():
    """Drop and recreate the loan database"""
    
    print("="*70)
    print("LOAN DATABASE RECREATION SCRIPT")
    print("="*70)
    print("WARNING: This will DELETE the existing 'loandb' database!")
    print("="*70)
    
    # Ask for confirmation
    response = input("\nType 'YES' to continue: ")
    if response != 'YES':
        print("Operation cancelled.")
        return
    
    conn = None
    cursor = None
    
    try:
        # Connect to PostgreSQL (default database)
        print("\n[1/4] Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            database='postgres'  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("SUCCESS: Connected to PostgreSQL")
        
        # Terminate existing connections to loandb
        print("\n[2/4] Terminating existing connections to 'loandb'...")
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'loandb'
              AND pid <> pg_backend_pid();
        """)
        print("SUCCESS: Connections terminated")
        
        # Drop the database if it exists
        print("\n[3/4] Dropping database 'loandb' if exists...")
        cursor.execute("DROP DATABASE IF EXISTS loandb;")
        print("SUCCESS: Database dropped")
        
        # Create the database
        print("\n[4/4] Creating new database 'loandb'...")
        cursor.execute("CREATE DATABASE loandb WITH ENCODING 'UTF8';")
        print("SUCCESS: Database created")
        
        # Close connection to postgres database
        cursor.close()
        conn.close()
        
        # Connect to the new loandb database
        print("\n[5/6] Connecting to 'loandb'...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port'],
            database='loandb'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        print("SUCCESS: Connected to loandb")
        
        # Create the loans table with correct schema
        print("\n[6/6] Creating 'loans' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id SERIAL PRIMARY KEY,
                cin TEXT NOT NULL,
                loan_amount NUMERIC(15, 2) NOT NULL,
                loan_duration_months INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                commercial_score NUMERIC(5, 2),
                risk_score NUMERIC(5, 2),
                final_score NUMERIC(5, 2),
                is_approved BOOLEAN,
                contract_path TEXT,
                amortization_path TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("SUCCESS: Table 'loans' created")
        
        # Create index
        print("\n[7/7] Creating index on cin...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loans_cin ON loans(cin);")
        print("SUCCESS: Index created")
        
        # Display table structure
        print("\n" + "="*70)
        print("DATABASE RECREATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nTABLE STRUCTURE:")
        print("-"*70)
        
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'loans'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"{'Column':<25} {'Type':<20} {'Nullable':<10}")
        print("-"*70)
        for col in columns:
            col_name, data_type, max_length, nullable = col
            type_str = f"{data_type}({max_length})" if max_length else data_type
            print(f"{col_name:<25} {type_str:<20} {nullable:<10}")
        
        print("="*70)
        print("\nNOTES:")
        print("- Database: loandb")
        print("- Encoding: UTF8")
        print("- Table: loans")
        print("- Index: idx_loans_cin")
        print("\nYou can now run your services!")
        print("="*70)
        
    except psycopg2.Error as e:
        print(f"\nERROR: Database operation failed")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check username/password in DB_CONFIG")
        print("3. Ensure you have permission to create/drop databases")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    recreate_database()
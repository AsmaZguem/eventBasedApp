import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'loandb',
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
            CREATE TABLE IF NOT EXISTS loans (
                loan_id SERIAL PRIMARY KEY,
                cin TEXT NOT NULL,
                loan_amount DECIMAL(15, 2) NOT NULL,
                loan_duration_months INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                commercial_score DECIMAL(5, 2),
                risk_score DECIMAL(5, 2),
                final_score DECIMAL(5, 2),
                is_approved BOOLEAN,
                contract_path TEXT,
                amortization_path TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loans_cin ON loans(cin)")
        
        print("Loan database setup completed!")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"Created table: loans")

        print("\n" + "=" * 70)
        print("TABLE STRUCTURE:")
        print("=" * 70)
        print("loan_id              - Auto-increment ID")
        print("cin                  - Client ID (references bank_db.clients)")
        print("loan_amount          - Requested amount")
        print("loan_duration_months - Loan duration")
        print("status               - PENDING, APPROVED, REJECTED")
        print("commercial_score     - Score from commercial service")
        print("risk_score           - Score from risk service")
        print("final_score          - Final decision score")
        print("is_approved          - Final approval decision")
        print("contract_path        - Path to generated contract")
        print("amortization_path    - Path to amortization table")
        print("created_at           - When loan was requested")
        print("updated_at           - Last update time")
        print("=" * 70)
        
        cursor.close()
        conn.close()
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        print("\nMake sure PostgreSQL is running and database 'loan_db' exists.")
        print("Create it with: CREATE DATABASE loan_db;")

if __name__ == '__main__':
    create_database()
### 1. Create Databases
```bash
psql -U postgres
```

```sql
CREATE DATABASE bank_db;
CREATE DATABASE central_bank;
CREATE DATABASE loandb;
\q
```

### 2. Initialize Databases

**Bank Database (Client Accounts):**
```bash
python database/create_bank_db.py
```

**Central Bank Database (Credit History):**
```bash
python central_bank_api/create_db.py
```

**Loan Database:**
```bash
python database/create_loan_db.py
```



## Configuration

### 1. Update OCR Service Paths
Edit `ocr_service/ocr.py` and update these paths according to your installation:
```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# TESSERACT_CMD = '/usr/bin/tesseract'  # Linux/macOS

POPPLER_PATH = r'C:\poppler-25.12.0\Library\bin'  # Windows
# POPPLER_PATH = '/usr/bin'  # Linux/macOS
```

### 2. Email Configuration
Create a `.env` file in the `services` directory:
```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### 3. Database Configuration
Update database credentials in:
- `database/bank_db.py`
- `database/loan_db.py`
- `central_bank_api/db.py`

Default credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'admin',
    'port': 5432
}
```

## Running the System

### Start Services in Order:

#### 1. Start Central Bank API
```bash
cd central_bank_api
python app.py
```
Access at: http://localhost:5000

#### 2. Start OCR Service
```bash
cd ocr_service
python ocr.py
```
Access at: http://localhost:5002

#### 3. Start Main Bank API
```bash
python app.py
```
Access at: http://localhost:5001

#### 4. Start Microservices (in separate terminals)

**Commercial Service:**
```bash
cd services
python commercial_service.py
```

**Risk Service:**
```bash
cd services
python risk_service.py
```

**Credit Service:**
```bash
cd services
python credit_service.py
```

**Notification Service:**
```bash
cd services
python notification_service.py
```

```
User submits loan
     ↓
LoanApplicationSubmitted (Kafka)
     ↓
Commercial Service (analyzes income via OCR)
     ↓
CommercialScoringCompleted (Kafka)
     ↓
Risk Service (checks debt + central bank)
     ↓
RiskScoringCompleted (Kafka)
     ↓
Credit Service (final decision + contract generation)
     ↓
CreditContractGenerated (Kafka)
     ↓
Notification Service (sends email)
     ↓
NotificationCompleted (Kafka)
```


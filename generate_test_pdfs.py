"""
generate_test_pdfs.py
Generate test PDF documents for testing the loan system
Creates PDFs with financial information that OCR can extract
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

def create_approved_candidate_pdf(output_path, cin, name):
    """
    Create PDF for a candidate that SHOULD BE APPROVED
    - High income: 5000 TND
    - Low expenses: 1000 TND
    - Low existing debt: 300 TND
    - No unpaid commitments (checked via Central Bank)
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "FINANCIAL STATEMENT")
    
    # Personal Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, "Personal Information:")
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.8*inch, f"Name: {name}")
    c.drawString(1*inch, height - 2.0*inch, f"CIN: {cin}")
    c.drawString(1*inch, height - 2.2*inch, f"Date: 2024-12-24")
    
    # Income Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2.8*inch, "Monthly Income:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 3.1*inch, "Salary Income: 5000 TND")
    c.drawString(1.5*inch, height - 3.3*inch, "Total Monthly Income: 5000 TND")
    
    # Expenses Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 3.9*inch, "Monthly Expenses:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 4.2*inch, "Rent: 600 TND")
    c.drawString(1.5*inch, height - 4.4*inch, "Utilities: 200 TND")
    c.drawString(1.5*inch, height - 4.6*inch, "Food: 200 TND")
    c.drawString(1.5*inch, height - 4.8*inch, "Total Monthly Expenses: 1000 TND")
    
    # Existing Debt Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 5.4*inch, "Existing Debts:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 5.7*inch, "Credit Card Outstanding: 300 TND")
    c.drawString(1.5*inch, height - 5.9*inch, "Total Existing Debt: 300 TND")
    
    # Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 6.5*inch, "Financial Summary:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 6.8*inch, f"Net Monthly Income: 4000 TND")
    c.drawString(1.5*inch, height - 7.0*inch, f"Debt-to-Income Ratio: 6%")
    c.drawString(1.5*inch, height - 7.2*inch, f"Financial Status: EXCELLENT")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1*inch, 1*inch, "This is a test document for loan application verification")
    
    c.save()
    print(f"✅ Created: {output_path}")
    print(f"   Income: 5000 TND, Expenses: 1000 TND, Debt: 300 TND")
    print(f"   Expected: APPROVED ✅")

def create_rejected_candidate_pdf(output_path, cin, name):
    """
    Create PDF for a candidate that SHOULD BE REJECTED
    - Low income: 2000 TND
    - High expenses: 1500 TND
    - High existing debt: 2000 TND
    - Has unpaid commitments (checked via Central Bank)
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "FINANCIAL STATEMENT")
    
    # Personal Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, "Personal Information:")
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.8*inch, f"Name: {name}")
    c.drawString(1*inch, height - 2.0*inch, f"CIN: {cin}")
    c.drawString(1*inch, height - 2.2*inch, f"Date: 2024-12-24")
    
    # Income Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2.8*inch, "Monthly Income:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 3.1*inch, "Salary Income: 2000 TND")
    c.drawString(1.5*inch, height - 3.3*inch, "Total Monthly Income: 2000 TND")
    
    # Expenses Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 3.9*inch, "Monthly Expenses:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 4.2*inch, "Rent: 800 TND")
    c.drawString(1.5*inch, height - 4.4*inch, "Utilities: 300 TND")
    c.drawString(1.5*inch, height - 4.6*inch, "Food: 400 TND")
    c.drawString(1.5*inch, height - 4.8*inch, "Total Monthly Expenses: 1500 TND")
    
    # Existing Debt Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 5.4*inch, "Existing Debts:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 5.7*inch, "Personal Loan Outstanding: 1500 TND")
    c.drawString(1.5*inch, height - 5.9*inch, "Credit Card Debt: 500 TND")
    c.drawString(1.5*inch, height - 6.1*inch, "Total Existing Debt: 2000 TND")
    
    # Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 6.7*inch, "Financial Summary:")
    c.setFont("Helvetica", 12)
    c.drawString(1.5*inch, height - 7.0*inch, f"Net Monthly Income: 500 TND")
    c.drawString(1.5*inch, height - 7.2*inch, f"Debt-to-Income Ratio: 100%")
    c.drawString(1.5*inch, height - 7.4*inch, f"Financial Status: HIGH RISK")
    
    # Warning
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(1, 0, 0)  # Red
    c.drawString(1.5*inch, height - 7.8*inch, "⚠ WARNING: High debt-to-income ratio")
    
    # Footer
    c.setFillColorRGB(0, 0, 0)  # Black
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1*inch, 1*inch, "This is a test document for loan application verification")
    
    c.save()
    print(f"✅ Created: {output_path}")
    print(f"   Income: 2000 TND, Expenses: 1500 TND, Debt: 2000 TND")
    print(f"   Expected: REJECTED ❌")

def main():
    print("=" * 70)
    print("GENERATING TEST PDF DOCUMENTS")
    print("=" * 70)
    print()
    
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("❌ ReportLab is not installed!")
        print("Install it with: pip install reportlab")
        return
    
    # Create uploads folder if it doesn't exist
    uploads_folder = os.path.join(os.path.dirname(__file__), 'uploads')
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)
        print(f"✅ Created uploads folder: {uploads_folder}\n")
    
    # Test User 1: Ali Kallel - SHOULD BE APPROVED
    # CIN: 11111111 - No unpaid commitments in Central Bank
    print("Creating PDF for User 1 (Should be APPROVED):")
    print("-" * 70)
    pdf1_path = os.path.join(uploads_folder, '11111111.pdf')
    create_approved_candidate_pdf(pdf1_path, '11111111', 'Ali Kallel')
    print()
    
    # Test User 2: Asma Zguem - SHOULD BE REJECTED
    # CIN: 11111112 - Has unpaid commitments in Central Bank
    print("Creating PDF for User 2 (Should be REJECTED):")
    print("-" * 70)
    pdf2_path = os.path.join(uploads_folder, '11111112.pdf')
    create_rejected_candidate_pdf(pdf2_path, '11111112', 'Asma Zguem')
    print()
    
    print("=" * 70)
    print("TEST SCENARIOS:")
    print("=" * 70)
    print()
    print("Scenario 1: Ali Kallel (CIN: 11111111) - SHOULD BE APPROVED ✅")
    print("  • Login: ali.kallel@insat.ucar.tn / password1")
    print("  • Income: 5000 TND (HIGH)")
    print("  • Expenses: 1000 TND (LOW)")
    print("  • Existing Debt: 300 TND (LOW)")
    print("  • Central Bank: No unpaid commitments ✅")
    print("  • Expected Commercial Score: ~90")
    print("  • Expected Risk Score: ~95")
    print("  • Expected Final Score: ~92 (APPROVED)")
    print()
    print("Scenario 2: Asma Zguem (CIN: 11111112) - SHOULD BE REJECTED ❌")
    print("  • Login: asma.zguem@insat.ucar.tn / password2")
    print("  • Income: 2000 TND (LOW)")
    print("  • Expenses: 1500 TND (HIGH)")
    print("  • Existing Debt: 2000 TND (HIGH)")
    print("  • Central Bank: Has unpaid commitments ⚠️")
    print("  • Expected Commercial Score: ~50")
    print("  • Expected Risk Score: ~20")
    print("  • Expected Final Score: ~38 (REJECTED)")
    print()
    print("=" * 70)
    print("HOW TO TEST:")
    print("=" * 70)
    print()
    print("1. Start all services (see QUICK_START.md)")
    print("2. Open http://localhost:5500")
    print()
    print("Test 1 (APPROVED):")
    print("  - Login as Ali Kallel")
    print("  - The PDF is already uploaded (11111111.pdf)")
    print("  - Submit loan: Amount=10000, Duration=24 months")
    print("  - Watch terminals - should see APPROVED ✅")
    print()
    print("Test 2 (REJECTED):")
    print("  - Logout and login as Asma Zguem")
    print("  - The PDF is already uploaded (11111112.pdf)")
    print("  - Submit loan: Amount=10000, Duration=24 months")
    print("  - Watch terminals - should see REJECTED ❌")
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()
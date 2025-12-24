import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from events import get_kafka_consumer, publish_notification
from confluent_kafka import KafkaError
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.bank_db import get_client_by_cin

# Load environment variables
load_dotenv()

def send_email(recipient_email, subject, html_content, text_content):
 
    try:
        # Get credentials from environment variables
        sender_email = os.getenv('GMAIL_EMAIL')
        sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not sender_email or not sender_password:
            print(" Error: Gmail credentials not found in .env file")
            return False
        
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"INSATx Bank <{sender_email}>"
        message['To'] = recipient_email
        
        # Add plain text and HTML parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        message.attach(part1)
        message.attach(part2)
        
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
        
    except Exception as e:
        print(f" Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_approval_email_html(cin, customer_name, final_score, reason):
    """Create HTML email for approved loan"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .details {{ background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
            .steps {{ background-color: white; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; border-radius: 0 0 5px 5px; }}
            h1 {{ margin: 0; }}
            .success-icon {{ font-size: 48px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="success-icon">✅</div>
                <h1>Loan Application Approved!</h1>
            </div>
            <div class="content">
                <p>Dear {customer_name},</p>
                
                <p> <strong>Congratulations!</strong> We are pleased to inform you that your loan application has been <strong>APPROVED</strong>!</p>
                
                <div class="details">
                    <h3> Decision Details:</h3>
                    <ul>
                        <li><strong>Customer ID (CIN):</strong> {cin}</li>
                        <li><strong>Final Score:</strong> {final_score}/100</li>
                        <li><strong>Status:</strong> {reason}</li>
                    </ul>
                </div>
                
                <div class="steps">
                    <h3> Next Steps:</h3>
                    <ol>
                        <li>Your contract and amortization table are ready</li>
                        <li>You can view them in your account dashboard</li>
                        <li>Please review and sign the documents at your earliest convenience</li>
                        <li>Visit your bank branch to complete the process</li>
                    </ol>
                </div>
                
                <p>If you have any questions, please don't hesitate to contact us.</p>
                
                <p>Best regards,<br>
                <strong>INSATx Bank Team</strong></p>
            </div>
            <div class="footer">
                <p> INSATx Bank - Your trusted financial partner</p>
            </div>
        </div>
    </body>
    </html>
    """

def create_rejection_email_html(cin, customer_name, final_score, reason):
    """Create HTML email for rejected loan"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .details {{ background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #f44336; }}
            .suggestions {{ background-color: white; padding: 15px; margin: 20px 0; }}
            .footer {{ background-color: #333; color: white; padding: 15px; text-align: center; border-radius: 0 0 5px 5px; }}
            h1 {{ margin: 0; }}
            .info-icon {{ font-size: 48px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="info-icon"></div>
                <h1>Loan Application Update</h1>
            </div>
            <div class="content">
                <p>Dear {customer_name},</p>
                
                <p>Thank you for your interest in INSATx Bank. We regret to inform you that your loan application could not be approved at this time.</p>
                
                <div class="details">
                    <h3> Decision Details:</h3>
                    <ul>
                        <li><strong>Customer ID (CIN):</strong> {cin}</li>
                        <li><strong>Final Score:</strong> {final_score}/100</li>
                        <li><strong>Reason:</strong> {reason}</li>
                    </ul>
                </div>
                
                <div class="suggestions">
                    <h3> What You Can Do:</h3>
                    <ul>
                        <li>Review your financial situation</li>
                        <li>Consider improving your income-to-debt ratio</li>
                        <li>Ensure all existing commitments are paid on time</li>
                        <li>Reapply after 6 months with improved conditions</li>
                    </ul>
                </div>
                
                <p> Please feel free to contact us for more information or financial advice. We're here to help you achieve your financial goals.</p>
                
                <p>Best regards,<br>
                <strong>INSATx Bank Team</strong></p>
            </div>
            <div class="footer">
                <p>💼 INSATx Bank - Your trusted financial partner</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_notification(cin, is_approved, final_score, reason):
    """
    Send notification to client based on loan decision
    Fetches customer email from database
    
    Args:
        cin: Customer identification number
        is_approved: Boolean indicating if loan is approved
        final_score: Final credit score
        reason: Reason for decision
    """
    print(f"\n{'='*60}")
    print(f"NOTIFICATION SERVICE - Processing CIN: {cin}")
    print(f"{'='*60}")
    
    # Fetch customer details from database
    print(f"Fetching customer details from database...")
    customer = get_client_by_cin(cin)
    
    if not customer:
        print(f"Error: Customer with CIN {cin} not found in database")
        print(f"{'='*60}\n")
        return False
    
    customer_email = customer.get('email')
    customer_name = customer.get('name', 'Valued Customer')
    
    if not customer_email:
        print(f"Error: No email found for customer {cin}")
        print(f"{'='*60}\n")
        return False
    
    print(f"Customer found: {customer_name} ({customer_email})")
    
    # Prepare email content
    if is_approved:
        subject = "Loan Application Approved - INSATx Bank"
        html_content = create_approval_email_html(cin, customer_name, final_score, reason)
        text_content = f"""
LOAN APPLICATION APPROVED

Dear {customer_name},

Congratulations! Your loan application has been APPROVED!

Decision Details:
- Customer ID (CIN): {cin}
- Final Score: {final_score}/100
- Status: {reason}

Next Steps:
1. Your contract and amortization table are ready
2. You can view them in your account dashboard
3. Please review and sign the documents at your earliest convenience
4. Visit your bank branch to complete the process

Best regards,
INSATx Bank - Your trusted financial partner
"""
    else:
        subject = "Loan Application Update - INSATx Bank"
        html_content = create_rejection_email_html(cin, customer_name, final_score, reason)
        text_content = f"""
LOAN APPLICATION UPDATE

Dear {customer_name},

We regret to inform you that your loan application could not be approved at this time.

Decision Details:
- Customer ID (CIN): {cin}
- Final Score: {final_score}/100
- Reason: {reason}

What You Can Do:
• Review your financial situation
• Consider improving your income-to-debt ratio
• Ensure all existing commitments are paid on time
• Reapply after 6 months with improved conditions

Contact us for more information or financial advice.

Best regards,
INSATx Bank - Your trusted financial partner
"""
    
    # Display notification in console
    print(f"Sending email to: {customer_email}")
    print(f"Subject: {subject}")
    
    # Send email
    email_success = send_email(customer_email, subject, html_content, text_content)
    
    if email_success:
        print(f"Email sent successfully to {customer_email}")
    else:
        print(f"Failed to send email to {customer_email}")
    
    # Publish to NotificationCompleted topic
    print(f"Publishing to NotificationCompleted...")
    kafka_success = publish_notification(cin, is_approved, text_content)
    
    if kafka_success:
        print(f"Kafka event published successfully")
    else:
        print(f"Failed to publish Kafka event")
    
    print(f"{'='*60}\n")
    return email_success and kafka_success

def run_notification_service():
    """Run the notification service consumer"""
    print("=" * 60)
    print("NOTIFICATION SERVICE STARTING")
    print("=" * 60)
    print("Listening to: CreditContractGenerated")
    print("Publishing to: NotificationCompleted")
    print("=" * 60 + "\n")
    
    consumer = get_kafka_consumer('notification-service-group', ['CreditContractGenerated'])
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    break
            
            try:
                event_data = json.loads(msg.value().decode('utf-8'))
                print(f"\n Received event from CreditContractGenerated")
                print(f"   Event type: {event_data.get('event_type', 'UNKNOWN')}")
                
                cin = event_data.get('cin')
                is_approved = event_data.get('is_approved')
                final_score = event_data.get('final_score')
                reason = event_data.get('reason')
                
                if cin and is_approved is not None and final_score is not None and reason:
                    send_notification(cin, is_approved, final_score, reason)
                else:
                    print(f"Invalid event data: missing required fields")
                    print(f"   Received: {event_data}")
                    
            except Exception as e:
                print(f"Error processing message: {e}")
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\nNotification service shutting down...")
    finally:
        consumer.close()

if __name__ == '__main__':
    run_notification_service()
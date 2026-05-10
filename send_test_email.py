#!/usr/bin/env python3
"""
Quick Test - Send Email with Current Report
Tests email configuration by sending a test report
Configure recipient via config/email_config.json or environment variables
"""

import os
import sys

# Check if SMTP_PASSWORD is set
smtp_password = os.getenv("SMTP_PASSWORD")

if not smtp_password:
    print("=" * 70)
    print("⚠️  SMTP_PASSWORD not set")
    print("=" * 70)
    print()
    print("To send email, you need to set your Gmail App Password:")
    print()
    print("STEP 1: Get Gmail App Password")
    print("  1. Go to: https://myaccount.google.com/apppasswords")
    print("  2. Generate App Password for 'Mail' on 'Mac'")
    print("  3. Copy the 16-character password")
    print()
    print("STEP 2: Set the password")
    print("  export SMTP_PASSWORD='your-16-char-password'")
    print()
    print("STEP 3: Run this script again")
    print("  python3 send_test_email.py")
    print()
    print("=" * 70)
    sys.exit(1)

print("=" * 70)
print("📧 SENDING TEST EMAIL")
print("=" * 70)
print()

# Import after checking password
try:
    from monthly_kernel_report import send_email_report, load_email_config
except ImportError as e:
    print(f"ERROR: Could not import monthly_kernel_report: {e}")
    sys.exit(1)

# Load config
config = load_email_config()

print("Loading configuration...")
print(f"  SMTP Server: {config['smtp_server']}:{config['smtp_port']}")
print(f"  From: {config['sender_email']}")
print(f"  To: {config['recipient_email']}")
print()

# Send email
print("Sending email...")
result = send_email_report(config)

print()
print("=" * 70)
if result:
    print("✅ SUCCESS!")
    print("=" * 70)
    print()
    print(f"Email sent successfully to: {config['recipient_email']}")
    print()
    print("Check your inbox for:")
    print("  Subject: Linux Kernel Storage & Filesystem Update - May 2026")
    print()
    print("If you don't see it:")
    print("  • Check spam/junk folder")
    print("  • Verify email address is correct")
    print("  • Check logs/monthly_report_error.log")
    print()
else:
    print("❌ FAILED")
    print("=" * 70)
    print()
    print("Email sending failed. Common issues:")
    print("  • Wrong SMTP password")
    print("  • Gmail App Password not generated")
    print("  • 2-factor auth not enabled on Gmail")
    print()
    print("Check logs/monthly_report_error.log for details")
    print()

print("=" * 70)

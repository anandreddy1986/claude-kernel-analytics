#!/bin/bash
#
# Quick Test Script for Monthly Automation
# Tests the monthly report generation without sending email
#

echo "========================================"
echo "Testing Monthly Automation"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "monthly_kernel_report.py" ]; then
    echo "ERROR: Please run this script from the project root directory"
    exit 1
fi

# Check Python installation
echo "1. Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "   ✓ Python3 found: $(python3 --version)"
else
    echo "   ✗ Python3 not found"
    exit 1
fi

# Check required directories
echo ""
echo "2. Checking directories..."
mkdir -p logs
mkdir -p config
echo "   ✓ Directories created"

# Check if SMTP_PASSWORD is set (warn if not)
echo ""
echo "3. Checking SMTP configuration..."
if [ -z "$SMTP_PASSWORD" ]; then
    echo "   ⚠️  WARNING: SMTP_PASSWORD not set"
    echo "   Email sending will fail, but reports will be generated"
    echo ""
    echo "   To set SMTP password:"
    echo "   export SMTP_PASSWORD='your-app-password'"
else
    echo "   ✓ SMTP_PASSWORD is set"
fi

# Test run (dry run without email)
echo ""
echo "4. Would you like to test the full automation? (y/n)"
echo "   This will:"
echo "   - Collect latest kernel changes (~10-15 minutes)"
echo "   - Generate blog post (~2-3 minutes)"
echo "   - Generate PDF report"
echo "   - Attempt to send email (if SMTP configured)"
echo ""
read -p "   Proceed? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "========================================"
    echo "Running Full Automation Test"
    echo "========================================"
    echo ""

    python3 monthly_kernel_report.py

    exit_code=$?

    echo ""
    echo "========================================"
    if [ $exit_code -eq 0 ]; then
        echo "✓ Test completed successfully"
        echo "  Check logs/monthly_report.log for details"
    elif [ $exit_code -eq 2 ]; then
        echo "⚠️  Reports generated, but email failed"
        echo "  Check logs/monthly_report_error.log"
        echo "  Reports are in data/drafts/"
    else
        echo "✗ Test failed with exit code $exit_code"
        echo "  Check logs/monthly_report_error.log"
    fi
    echo "========================================"
else
    echo ""
    echo "Test cancelled. To run manually:"
    echo "  python3 monthly_kernel_report.py"
fi

echo ""
echo "Next steps:"
echo "  1. Set SMTP_PASSWORD: export SMTP_PASSWORD='your-app-password'"
echo "  2. Install LaunchAgent: cp com.redhat.kernel.monthly.plist ~/Library/LaunchAgents/"
echo "  3. Load agent: launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist"
echo ""
echo "See MONTHLY_AUTOMATION_SETUP.md for detailed instructions"
echo ""

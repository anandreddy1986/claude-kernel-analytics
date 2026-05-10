#!/bin/bash
#
# Quick Setup - No Email Required
# Sets up monthly automation to generate reports locally
#

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║       Monthly Kernel Report Setup - No Email Version                ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This setup will:"
echo "  ✓ Install monthly automation (runs 1st of each month)"
echo "  ✓ Generate professional reports automatically"
echo "  ✓ Save reports to data/drafts/ folder"
echo "  ✓ Skip email sending (you can add later)"
echo ""
echo "Reports will be generated at:"
echo "  data/drafts/Linux_Kernel_Storage_Update_[Month]_[Year].pdf"
echo "  data/drafts/Linux_Kernel_Storage_Update_[Month]_[Year].html"
echo ""
read -p "Continue with setup? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Installing Monthly Automation Scheduler"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Copy plist to LaunchAgents
cp com.redhat.kernel.monthly.plist ~/Library/LaunchAgents/

if [ $? -eq 0 ]; then
    echo "✓ LaunchAgent configuration copied"
else
    echo "✗ Failed to copy LaunchAgent configuration"
    exit 1
fi

# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

if [ $? -eq 0 ]; then
    echo "✓ LaunchAgent loaded successfully"
else
    echo "✗ Failed to load LaunchAgent"
    exit 1
fi

# Verify it's running
if launchctl list | grep -q "com.redhat.kernel.monthly"; then
    echo "✓ Monthly automation is active"
else
    echo "⚠  Warning: LaunchAgent may not be active"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Checking Current Reports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "data/drafts" ]; then
    echo "Report directory: data/drafts/"
    echo ""
    echo "Current reports:"
    ls -lh data/drafts/*.pdf data/drafts/*.html 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

    if [ -f "data/drafts/Linux_Kernel_Storage_Update_Apr_May_2026.pdf" ]; then
        echo ""
        echo "✓ May 2026 report is ready!"
        echo ""
        read -p "Would you like to open the report now? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open data/drafts/Linux_Kernel_Storage_Update_Apr_May_2026.pdf
            echo "✓ Report opened in default PDF viewer"
        fi
    fi
else
    echo "⚠  Reports directory not found (will be created on first run)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What happens next:"
echo ""
echo "  📅 June 1, 2026 at 9:00 AM"
echo "      ↓"
echo "  🤖 System wakes up automatically"
echo "      ↓"
echo "  📊 Collects latest kernel changes"
echo "      ↓"
echo "  ✍️  Generates new June 2026 report"
echo "      ↓"
echo "  💾 Saves to data/drafts/ folder"
echo "      ↓"
echo "  ✅ Done! (No email sent)"
echo ""
echo "To view reports:"
echo "  open data/drafts/"
echo ""
echo "To check automation status:"
echo "  launchctl list | grep com.redhat.kernel.monthly"
echo "  tail -f logs/monthly_report.log"
echo ""
echo "To add email later:"
echo "  See EMAIL_ALTERNATIVES.md for options"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Your AI Agent System is Active!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

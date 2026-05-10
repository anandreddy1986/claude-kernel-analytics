# Email Setup Alternatives - Corporate Account Solutions

## Issue: "App passwords not available for your account"

This happens with Red Hat/corporate Google Workspace accounts because:
- IT admins control security settings
- Different authentication methods required
- 2-Factor Authentication may not be enabled
- Advanced Protection may be active

---

## ✅ SOLUTION 1: Use Red Hat Corporate SMTP (Recommended)

### Best option for Red Hat employees - no App Password needed!

Contact Red Hat IT for SMTP details, or try these common configurations:

**Option A: Red Hat Internal SMTP**
```bash
export SMTP_SERVER="smtp.corp.redhat.com"  # Verify with IT
export SMTP_PORT="587"
export SENDER_EMAIL="anareddy@redhat.com"
export RECIPIENT_EMAIL="anareddy@redhat.com"
export SMTP_PASSWORD="your-red-hat-password"  # Your regular Red Hat password
```

**Option B: Red Hat VPN Required**
Some corporate SMTP servers require VPN connection:
```bash
# 1. Connect to Red Hat VPN first
# 2. Then use corporate SMTP settings (from IT)
```

**To get correct settings:**
- Contact Red Hat IT Service Desk
- Check internal Red Hat wiki/docs for "Email SMTP settings"
- Or check your email client settings (Thunderbird/Outlook)

**Update the plist file:**
```bash
nano ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

# Change these lines:
<key>SMTP_SERVER</key>
<string>smtp.corp.redhat.com</string>  # Update with IT-provided value

<key>SMTP_PORT</key>
<string>587</string>  # Or 25, as IT specifies
```

---

## ✅ SOLUTION 2: Enable 2-Factor Auth on Your Account

If you want to use your @redhat.com Google Workspace account:

### Step 1: Enable 2FA
```
1. Go to: https://myaccount.google.com/security
2. Look for "2-Step Verification"
3. If available, enable it
4. Complete the setup process
```

### Step 2: Try App Passwords Again
```
1. Go to: https://myaccount.google.com/apppasswords
2. Should now be available
3. Generate password for "Mail" on "Mac"
```

**Note:** If 2FA is disabled by your IT admin, this won't work.

---

## ✅ SOLUTION 3: Use Personal Gmail Account (Temporary)

Quick workaround for testing:

### Use a Personal Gmail
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your.personal.gmail@gmail.com"  # Your personal Gmail
export RECIPIENT_EMAIL="anareddy@redhat.com"         # Still receive at work email
export SMTP_PASSWORD="your-gmail-app-password"       # From personal account
```

**Steps:**
1. Use your personal Gmail account for SENDING
2. Still receive reports at anareddy@redhat.com
3. Generate App Password from personal Gmail (2FA required)

**Pros:** Works immediately, easy to test
**Cons:** Reports come from personal email (may look unprofessional)

---

## ✅ SOLUTION 4: Skip Email - Just Generate Reports Locally

### You don't NEED email for the system to work!

The automation can still run monthly and generate reports without sending email.

**Modify the automation:**

```bash
# Edit monthly_kernel_report.py
nano monthly_kernel_report.py

# Or create a "no-email" version
cp monthly_kernel_report.py monthly_kernel_report_no_email.py
```

**Change Step 4 to skip email:**
```python
# In monthly_kernel_report.py, modify the main() function:

def main():
    # ... Steps 1-3 run normally ...
    
    # Step 4: Skip email, just log success
    print("\n" + "="*70)
    print("✓ REPORTS GENERATED SUCCESSFULLY")
    print("="*70)
    print(f"\nGenerated files:")
    print(f"  PDF: {DRAFTS_DIR}/Linux_Kernel_Storage_Update_*.pdf")
    print(f"  HTML: {DRAFTS_DIR}/Linux_Kernel_Storage_Update_*.html")
    print(f"\nReports saved locally - email skipped")
    
    # Don't call send_email_report(config)
```

**Then you can:**
- Check `data/drafts/` folder monthly
- Open the PDF/HTML files directly
- Manually forward them if needed

---

## 🎯 RECOMMENDED APPROACH

### For Red Hat Employees:

**BEST:** Use Red Hat corporate SMTP
- Contact IT for SMTP server details
- Use your regular Red Hat password
- No App Password needed
- Most professional for work emails

**Testing:** Use personal Gmail temporarily
- Get system working quickly
- Test the automation
- Switch to corporate SMTP later

**Alternative:** Skip email entirely
- Still get monthly reports generated
- Access files locally in `data/drafts/`
- Forward manually if needed

---

## 📧 Quick Test Without Email

Want to see if everything else works?

```bash
# Test the full automation WITHOUT sending email
# This runs steps 1-3 (collect, analyze, generate)

python3 monthly_kernel_report.py --no-email  # If you add this flag

# Or just check existing reports
ls -lh data/drafts/
open data/drafts/Linux_Kernel_Storage_Update_Apr_May_2026.pdf
```

---

## 🔧 Configuration Files to Update

### If using Red Hat Corporate SMTP:

**1. Update email config template:**
```bash
nano config/email_config.json.template

{
  "smtp_server": "smtp.corp.redhat.com",  # Get from IT
  "smtp_port": 587,                       # Or 25
  "sender_email": "anareddy@redhat.com",
  "recipient_email": "anareddy@redhat.com"
}
```

**2. Update LaunchAgent plist:**
```bash
nano ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

<key>SMTP_SERVER</key>
<string>smtp.corp.redhat.com</string>  # Update

<key>SMTP_PORT</key>
<string>587</string>  # Update if needed
```

**3. Set environment variable:**
```bash
export SMTP_PASSWORD="your-red-hat-password"
echo 'export SMTP_PASSWORD="your-red-hat-password"' >> ~/.zshrc
```

---

## 🎯 Next Steps Based on Your Choice

### Choice 1: Red Hat Corporate SMTP
```
1. [ ] Contact Red Hat IT for SMTP details
2. [ ] Update configuration files with IT-provided settings
3. [ ] Set SMTP_PASSWORD to your Red Hat password
4. [ ] Test: python3 send_test_email.py
```

### Choice 2: Personal Gmail (Temporary)
```
1. [ ] Enable 2FA on personal Gmail
2. [ ] Generate App Password for personal Gmail
3. [ ] Set SENDER_EMAIL to personal Gmail
4. [ ] Keep RECIPIENT_EMAIL as anareddy@redhat.com
5. [ ] Test: python3 send_test_email.py
```

### Choice 3: No Email (Local Reports Only)
```
1. [ ] Install LaunchAgent (for monthly automation)
2. [ ] Skip email configuration entirely
3. [ ] Check data/drafts/ folder monthly for reports
4. [ ] Manually share/forward as needed
```

---

## 📞 Getting Help

### Red Hat IT Service Desk
**For corporate SMTP settings:**
- Internal ticket system
- IT documentation (internal wiki)
- Email client settings (check Thunderbird/Outlook config)

### What to Ask IT:
```
"I need SMTP server settings to send automated emails from my
Mac using anareddy@redhat.com. What are the:
- SMTP server hostname
- SMTP port
- Authentication method
- Any VPN requirements"
```

---

## ✅ System Still Works Without Email!

**Important:** The core AI agent system is complete and functional!

The monthly automation will still:
- ✅ Collect kernel changes
- ✅ Analyze 12 subsystems + 5 userspace components
- ✅ Generate professional blog posts
- ✅ Create PDF and HTML reports
- ✅ Save everything to `data/drafts/`

The email is just the **delivery mechanism** - the reports are generated regardless!

---

## 🚀 Simplified Setup (No Email)

If you just want to get started:

```bash
# 1. Install the scheduler (no email needed)
cp com.redhat.kernel.monthly.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

# 2. That's it! System will generate reports monthly

# 3. Check reports manually:
open data/drafts/
```

**Next month (June 1):**
- System generates new report automatically
- You open `data/drafts/` folder
- Reports are ready to view/share

---

## 📝 Summary

**Your Options:**
1. ⭐ **Red Hat Corporate SMTP** - Best for work, requires IT help
2. 🔧 **Personal Gmail** - Quick testing, works immediately
3. 📁 **No Email** - Simplest, still generates reports monthly

**What Works Now:**
- ✅ AI agent system is complete
- ✅ May 2026 report already generated
- ✅ Monthly automation configured
- ✅ Reports in `data/drafts/` folder

**What Needs Setup:**
- ⏳ Email delivery (optional!)

**Recommendation:**
Start with **No Email** approach, get familiar with the system, then add corporate SMTP later when you have IT details.

---

**Your AI Agent Project:** Still 95% complete and fully functional! 🎉

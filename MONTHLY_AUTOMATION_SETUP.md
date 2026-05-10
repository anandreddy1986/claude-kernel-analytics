# Monthly Automation Setup - Linux Kernel Storage Report

## Overview
Automated monthly Linux kernel storage and filesystem upstream analysis that runs on the 1st of every month and emails results to anareddy@redhat.com.

**What it does:**
1. ✅ Collects latest kernel changes from upstream repositories (12 kernel subsystems + 5 userspace components)
2. ✅ Generates professional LinkedIn-ready blog post with architectural analysis
3. ✅ Creates HTML and PDF reports
4. ✅ Emails reports to anareddy@redhat.com

**Schedule:** 1st of every month at 9:00 AM

---

## Quick Start (macOS)

### Option 1: Using launchd (Recommended for macOS)

#### 1. Set up SMTP credentials

**For Gmail:**
```bash
# Enable 2-factor authentication in your Google Account
# Generate App Password: https://myaccount.google.com/apppasswords
# Then set environment variable (replace with your app password):

export SMTP_PASSWORD="your-gmail-app-password"

# Make it persistent (add to ~/.zshrc or ~/.bash_profile):
echo 'export SMTP_PASSWORD="your-gmail-app-password"' >> ~/.zshrc
```

**For Red Hat email (corporate SMTP):**
```bash
# Contact IT for Red Hat SMTP server details
# Update com.redhat.kernel.monthly.plist with correct SMTP server

# If using Red Hat SMTP:
export SMTP_SERVER="smtp.corp.redhat.com"  # Example, verify with IT
export SMTP_PORT="587"  # Or 25, verify with IT
export SMTP_PASSWORD="your-red-hat-password"
```

#### 2. Install the LaunchAgent

```bash
# Navigate to project directory
cd /Users/anareddy/Desktop/Claude_Agentic_Kernel_Publication

# Make the Python script executable
chmod +x monthly_kernel_report.py

# Copy plist to LaunchAgents directory
cp com.redhat.kernel.monthly.plist ~/Library/LaunchAgents/

# Load the launch agent
launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

# Verify it's loaded
launchctl list | grep com.redhat.kernel.monthly
```

#### 3. Test the automation (optional)

```bash
# Run manually to test
python3 monthly_kernel_report.py

# Or trigger the launchd job immediately
launchctl start com.redhat.kernel.monthly
```

#### 4. Check logs

```bash
# View execution logs
tail -f logs/monthly_report.log

# View error logs
tail -f logs/monthly_report_error.log
```

---

### Option 2: Using cron (Alternative)

```bash
# Edit crontab
crontab -e

# Add this line (runs 1st of month at 9:00 AM):
0 9 1 * * cd /Users/anareddy/Desktop/Claude_Agentic_Kernel_Publication && /usr/bin/python3 monthly_kernel_report.py >> logs/monthly_report.log 2>&1

# Verify crontab
crontab -l
```

**Note:** cron on macOS requires Full Disk Access permission:
- System Preferences → Security & Privacy → Privacy → Full Disk Access
- Add `/usr/sbin/cron` or Terminal app

---

## Configuration

### Email Configuration

**Method 1: Environment Variables (Recommended)**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="anareddy@redhat.com"
export RECIPIENT_EMAIL="anareddy@redhat.com"
export SMTP_PASSWORD="your-app-password"
```

**Method 2: Config File**
```bash
# Copy template
cp config/email_config.json.template config/email_config.json

# Edit configuration
nano config/email_config.json
```

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "anareddy@redhat.com",
  "recipient_email": "anareddy@redhat.com"
}
```

**⚠️ SECURITY:** Never store SMTP password in config file. Always use environment variable `SMTP_PASSWORD`.

---

## SMTP Setup by Email Provider

### Gmail (smtp.gmail.com)

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Mac"
   - Click "Generate"
   - Copy the 16-character password

3. **Set Environment Variable**
   ```bash
   export SMTP_PASSWORD="abcd efgh ijkl mnop"  # Your app password
   ```

### Red Hat Corporate Email

Contact Red Hat IT for:
- SMTP server address (e.g., smtp.corp.redhat.com)
- SMTP port (usually 587 or 25)
- Authentication requirements
- VPN requirements

```bash
export SMTP_SERVER="smtp.corp.redhat.com"  # Verify with IT
export SMTP_PORT="587"  # Verify with IT
export SMTP_PASSWORD="your-red-hat-password"
```

---

## File Structure

```
Claude_Agentic_Kernel_Publication/
│
├── monthly_kernel_report.py           # Main automation script
├── com.redhat.kernel.monthly.plist    # macOS LaunchAgent configuration
│
├── agents/
│   └── collector_optimized.py         # Kernel data collector
│
├── linkedin_blog_generator.py         # Blog post generator
├── generate_pdf.py                    # PDF generator
│
├── config/
│   ├── email_config.json.template     # Email config template
│   └── email_config.json              # Actual config (not in git)
│
├── logs/
│   ├── monthly_report.log             # Execution logs
│   └── monthly_report_error.log       # Error logs
│
└── data/
    └── drafts/
        ├── linkedin_kernel_update_apr_may_2026.md
        ├── Linux_Kernel_Storage_Update_Apr_May_2026.html
        └── Linux_Kernel_Storage_Update_Apr_May_2026.pdf
```

---

## Testing the Automation

### 1. Manual Test Run

```bash
cd /Users/anareddy/Desktop/Claude_Agentic_Kernel_Publication

# Run the monthly report manually
python3 monthly_kernel_report.py
```

**Expected output:**
```
======================================================================
MONTHLY LINUX KERNEL STORAGE REPORT GENERATOR
======================================================================
Execution Time: 2026-05-08 15:30:00
======================================================================

============================================================
STEP 1: Collecting Latest Kernel Changes
============================================================
Cloning Linux kernel repository...
✓ Data collection completed successfully

============================================================
STEP 2: Generating LinkedIn Blog Post
============================================================
Analyzing subsystems...
✓ Blog generation completed successfully

============================================================
STEP 3: Generating PDF Report
============================================================
✓ HTML generated successfully
✓ PDF generated: .../Linux_Kernel_Storage_Update_Apr_May_2026.pdf

============================================================
STEP 4: Sending Email Report
============================================================
✓ Attached PDF: Linux_Kernel_Storage_Update_Apr_May_2026.pdf
✓ Attached HTML: Linux_Kernel_Storage_Update_Apr_May_2026.html

Connecting to SMTP server: smtp.gmail.com:587
✓ Email sent successfully to: anareddy@redhat.com
  Subject: Linux Kernel Storage & Filesystem Update - May 2026

======================================================================
✓ MONTHLY REPORT GENERATION COMPLETED SUCCESSFULLY
======================================================================
Report sent to: anareddy@redhat.com
Execution completed: 2026-05-08 15:35:42
```

### 2. Test Email Sending Only

```bash
# Set SMTP password first
export SMTP_PASSWORD="your-app-password"

# Run with existing reports
python3 -c "
from monthly_kernel_report import send_email_report, load_email_config
config = load_email_config()
send_email_report(config)
"
```

---

## Monitoring & Troubleshooting

### Check LaunchAgent Status

```bash
# List all launch agents
launchctl list | grep com.redhat

# Check if job is loaded
launchctl list com.redhat.kernel.monthly

# View next scheduled run
# (Use third-party tools like LaunchControl, or check system logs)
```

### View Logs

```bash
# Real-time log monitoring
tail -f logs/monthly_report.log

# View last 100 lines
tail -n 100 logs/monthly_report.log

# Search for errors
grep -i error logs/monthly_report_error.log
```

### Common Issues

**Issue: Email authentication fails**
```
ERROR: SMTP authentication failed
```
**Solution:**
- Verify SMTP_PASSWORD is set correctly
- For Gmail, ensure you're using App Password (not regular password)
- Check 2-factor authentication is enabled

**Issue: LaunchAgent not running**
```bash
# Unload and reload
launchctl unload ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist
launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist
```

**Issue: Permission denied**
```bash
# Make script executable
chmod +x monthly_kernel_report.py

# Check file permissions
ls -la monthly_kernel_report.py
```

**Issue: Python module not found**
```bash
# Install required packages
pip3 install anthropic google-cloud-aiplatform
```

---

## Customization

### Change Schedule

**Edit plist file:**
```xml
<!-- Current: 1st of month at 9:00 AM -->
<key>StartCalendarInterval</key>
<dict>
    <key>Day</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

**Change to run on 15th at 2:00 PM:**
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Day</key>
    <integer>15</integer>
    <key>Hour</key>
    <integer>14</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

**Reload after changes:**
```bash
launchctl unload ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist
launchctl load ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist
```

### Change Email Recipients

**Edit email_config.json:**
```json
{
  "recipient_email": "team-list@redhat.com"
}
```

Or use environment variable:
```bash
export RECIPIENT_EMAIL="team-list@redhat.com,backup@redhat.com"
```

### Change Report Content

Modify subsystems in `config/subsystems.json`:
```json
{
  "xfs": {
    "name": "XFS",
    "repo_url": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
    "path": "fs/xfs/",
    "enabled": true
  }
}
```

---

## Uninstalling

### Remove LaunchAgent

```bash
# Unload the agent
launchctl unload ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

# Remove plist file
rm ~/Library/LaunchAgents/com.redhat.kernel.monthly.plist

# Verify removal
launchctl list | grep com.redhat.kernel.monthly
```

### Remove cron job

```bash
# Edit crontab
crontab -e

# Delete the line with monthly_kernel_report.py
# Save and exit
```

---

## Security Best Practices

1. **Never commit SMTP passwords to git**
   - Use environment variables
   - Add `config/email_config.json` to `.gitignore`

2. **Use App Passwords (Gmail)**
   - More secure than regular password
   - Can be revoked independently

3. **Restrict file permissions**
   ```bash
   chmod 600 config/email_config.json  # If you must store config
   chmod 700 logs/  # Restrict log access
   ```

4. **Use Red Hat corporate SMTP when possible**
   - More secure for corporate communications
   - No personal account credentials needed

---

## Email Report Preview

**Subject:** Linux Kernel Storage & Filesystem Update - May 2026

**Content:**
- Professional HTML email body
- Summary of covered subsystems
- Key upstream themes
- Attached PDF (publication-ready)
- Attached HTML (web-viewable)

**Attachments:**
- `Linux_Kernel_Storage_Update_May_2026.pdf` (~260 KB)
- `Linux_Kernel_Storage_Update_May_2026.html` (~30 KB)

---

## Support & Feedback

**For issues:**
- Check logs: `logs/monthly_report.log` and `logs/monthly_report_error.log`
- Review this documentation
- Test manually: `python3 monthly_kernel_report.py`

**For questions:**
- Email: anareddy@redhat.com

---

## Summary Checklist

### Initial Setup
- [ ] Set `SMTP_PASSWORD` environment variable
- [ ] Copy plist to `~/Library/LaunchAgents/`
- [ ] Load LaunchAgent: `launchctl load ...`
- [ ] Test run: `python3 monthly_kernel_report.py`
- [ ] Verify email received at anareddy@redhat.com

### Ongoing Monitoring
- [ ] Check logs monthly: `tail logs/monthly_report.log`
- [ ] Verify email delivery on 1st of month
- [ ] Review generated reports for quality
- [ ] Update subsystem configuration as needed

### Maintenance
- [ ] Renew SMTP App Password annually (if Gmail)
- [ ] Update LaunchAgent if schedule changes
- [ ] Monitor disk space in `data/repos/` directory
- [ ] Archive old reports periodically

---

**Status:** ✅ Ready for Production Deployment

*Automation configured: May 08, 2026*
*Next scheduled run: June 1, 2026 at 9:00 AM*
*Email recipient: anareddy@redhat.com*

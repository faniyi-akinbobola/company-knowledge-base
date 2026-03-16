# IT Support Guide

**Document Information**
- Version: 2.3
- Last Updated: January 11, 2026
- Document Owner: IT Operations
- Contact: itsupport@apextech.solutions | ext. 4357
- Emergency Line: ext. 4911 (after hours)

---

## Table of Contents
1. [Getting IT Support](#getting-it-support)
2. [Common Issues & Solutions](#common-issues--solutions)
3. [Password Management](#password-management)
4. [Hardware & Equipment](#hardware--equipment)
5. [Software Access Requests](#software-access-requests)
6. [VPN & Remote Access](#vpn--remote-access)
7. [Email & Calendar](#email--calendar)
8. [Security & Data Protection](#security--data-protection)
9. [Troubleshooting Tips](#troubleshooting-tips)

---

## Getting IT Support

### IT Service Portal
**Primary support channel**: itservices.apextech.com

**How to Submit a Ticket:**
1. Log in with your company credentials (SSO)
2. Click "Submit a Ticket"
3. Select category (Hardware, Software, Access, Network, etc.)
4. Describe the issue clearly:
   - What were you trying to do?
   - What happened instead?
   - Error messages (screenshots help!)
   - When did it start?
5. Set priority (Critical, High, Normal, Low)
6. Submit

**Response Times (SLA):**
- **Critical** (system down, security issue): 1 hour
- **High** (major feature broken): 4 hours
- **Normal** (inconvenience, workaround exists): 24 hours
- **Low** (questions, enhancement requests): 48 hours

### Alternative Contact Methods

**Slack**: #tech-support
- For quick questions
- Informal troubleshooting
- Community help (other employees may answer)
- IT monitors during business hours

**Email**: itsupport@apextech.solutions
- Automatically creates ticket
- Good for non-urgent issues
- Include screenshots/details

**Phone**: ext. 4357 (HELP)
- Monday-Friday, 8:00 AM - 6:00 PM PT
- For urgent issues requiring immediate assistance
- After hours: ext. 4911 (emergencies only)

**Walk-Up Support** (SF Office Only)
- Location: Building A, 1st Floor, IT Desk
- Hours: Monday-Friday, 9:00 AM - 5:00 PM
- Best for hardware issues, equipment pickup

### Checking Ticket Status
- Portal: View "My Tickets" dashboard
- Email: Updates sent automatically
- Slack: DM @ITBot with ticket number

---

## Common Issues & Solutions

### Can't Log In to Computer

**Possible Causes:**
- Incorrect password
- Account locked (too many failed attempts)
- Password expired
- Network/domain issue

**Solutions:**
1. Double-check Caps Lock is off
2. Try password reset: apextech.com/password-reset
3. If locked out, call IT: ext. 4357
4. For Mac FileVault: Use recovery key (check 1Password vault)

### Computer Running Slow

**Quick Fixes:**
1. **Restart your computer** (solves 70% of performance issues)
2. **Close unused apps** (check Activity Monitor/Task Manager)
3. **Clear browser cache** (Chrome: Settings → Privacy → Clear browsing data)
4. **Check available storage** (macOS: Apple menu → About This Mac → Storage)
   - Should have at least 20GB free
   - Delete old files or request storage expansion

**Still slow? Submit ticket with:**
- How long has it been slow?
- Which apps are affected?
- Screenshot of Activity Monitor/Task Manager

### Wi-Fi Connection Issues

**Troubleshooting Steps:**
1. Toggle Wi-Fi off and back on
2. Forget network and reconnect:
   - Network name: **ApexTech-Secure**
   - Password: Check 1Password or ask IT
3. Restart computer
4. Try ethernet cable (adapters available from IT)
5. Check status page: status.apextech.com

**If still not working:**
- Connect to guest network temporarily: **ApexTech-Guest** (password: Guest2026!)
- Submit ticket or call IT

### Can't Print

**Checklist:**
1. Is the printer turned on and connected?
2. Are you connected to correct printer?
   - Printer naming: `BLDG-A-2F-Color-01`
3. Check printer queue (clear stuck jobs)
4. Try printing test page from printer settings
5. Restart your computer

**Adding a New Printer:**
- Windows: Settings → Devices → Printers & scanners → Add printer
- Mac: System Preferences → Printers & Scanners → "+" button
- Printer list: apextech.notion.so/printers

### Application Crashes or Won't Open

**Steps:**
1. Force quit the application
2. Restart the application
3. Restart computer
4. Check for updates (Mac: App Store; Windows: Microsoft Store)
5. Uninstall and reinstall (if allowed)

**If still broken:**
Submit ticket with:
- Which application?
- Error message or crash log
- What you were doing when it crashed

### Email Not Syncing

**Solutions:**
1. Check internet connection
2. Verify storage quota (Google Workspace: 30GB limit)
   - Check usage: drive.google.com
   - Delete old emails or request increase
3. Sign out and sign back in
4. Clear Gmail cache (if using web)
5. Check gmail.com directly (bypass email client)

**For Outlook/Mail app issues:**
- Remove and re-add account
- Check sync settings (fetch new data frequency)

---

## Password Management

### Password Requirements

All passwords must meet these criteria:
- Minimum **12 characters**
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*)

**Password Expiry:** Every 90 days (you'll receive reminder emails)

**Do NOT:**
- Reuse old passwords
- Share passwords with anyone
- Use the same password across multiple systems
- Write passwords down physically
- Use easily guessable passwords (birthday, "Password123!")

### 1Password (Company Standard)

**What is 1Password?**
A password manager that securely stores all your credentials. You only need to remember one master password.

**Setup:**
1. Visit apextech.1password.com
2. Log in with company email
3. Download 1Password app (Mac/Windows/iOS/Android)
4. Set up strong master password (this is the ONLY password you need to memorize)
5. Enable biometric unlock (fingerprint/Face ID)

**Using 1Password:**
- Browser extension auto-fills passwords
- Generate strong random passwords for new accounts
- Store secure notes (WiFi passwords, access codes, etc.)
- Share credentials securely with teammates (via vaults)

**Shared Vaults:**
- **Team vaults**: Department-specific credentials
- **Project vaults**: Temporary project access
- **Admin vaults**: Privileged access (limited users)

### Self-Service Password Reset

**For Your Computer:**
- Visit: apextech.com/password-reset
- Enter company email
- Answer security questions
- Set new password

**For Other Systems:**
Most systems use SSO (Single Sign-On), so resetting your computer password resets everything.

**Exceptions (separate passwords):**
- 1Password master password
- Some legacy systems (contact IT)

### Locked Out?
Call IT immediately: ext. 4357
- We can unlock accounts remotely
- You may need to verify identity (employee ID, manager name, etc.)

---

## Hardware & Equipment

### Standard Equipment Packages

**All Employees Receive:**
- Laptop (Mac or Windows, your choice)
- Monitor (24" or 27")
- Keyboard and mouse
- Webcam (if not built-in)
- Headset with microphone
- Laptop stand
- Docking station (if needed)

**Remote Employees Get Additional:**
- $500 home office stipend for desk, chair, lighting
- Upgraded monitor (27" or 32")
- Ethernet adapter

### Requesting Additional Equipment

**Process:**
1. Submit request via IT Service Portal
2. Select "Hardware Request"
3. Specify item and business justification
4. Manager approval required for items >$100
5. Turnaround: 3-5 business days (standard items)

**Commonly Approved Items:**
- Second monitor
- Ergonomic keyboard/mouse
- Laptop riser
- USB-C hub/adapters
- External hard drive

**Approval Needed:**
- Specialized equipment (drawing tablets, high-end monitors)
- Expensive items (>$500)
- Non-standard requests

### Equipment Refresh Cycle
- **Laptops**: Every 3 years
- **Monitors**: Every 5 years
- **Peripherals**: As needed (when broken)

You'll receive notification when eligible for refresh.

### Returning Equipment
When leaving the company or upgrading:
1. Back up personal files (to approved cloud storage)
2. Remove personal data
3. Ship to IT (prepaid label provided) or return to office
4. IT wipes and refurbishes equipment

### Lost or Stolen Equipment
**IMMEDIATE ACTION REQUIRED:**
1. Call IT emergency line: ext. 4911
2. Email security@apextech.solutions
3. File police report (for stolen items)

IT will:
- Remotely wipe device
- Deactivate accounts
- Arrange replacement

**Prevention:**
- Enable FileVault/BitLocker encryption (required)
- Use laptop lock cable in office
- Never leave equipment in cars
- Enable "Find My" (Mac) or "Find My Device" (Windows)

---

## Software Access Requests

### Requesting New Software

**Approved Software List:** apextech.notion.so/approved-software
- Pre-approved for quick installation
- Vetted for security and licensing

**For Software NOT on List:**
1. Submit request via IT Portal
2. Provide business justification
3. Security review (1-2 weeks)
4. License procurement (if purchased)
5. Installation or account provisioning

**Factors Affecting Approval:**
- Security/compliance
- Licensing cost
- Business need
- Existing alternatives

### Common Software & Access

**Productivity:**
- Google Workspace (email, docs, drive) - Auto-provisioned
- Slack - Auto-provisioned
- Zoom - Auto-provisioned
- Notion - Auto-provisioned
- 1Password - Auto-provisioned

**Engineering:**
- GitHub - Request via IT Portal
- AWS Console - Request via IT Portal (manager approval)
- Jira - Auto-provisioned
- Figma - Auto-provisioned

**Sales/Marketing:**
- Salesforce - Auto-provisioned (sales roles)
- HubSpot - Request via manager
- LinkedIn Sales Navigator - Request via manager

### Software Installation Permissions

**Employees CAN Install (without IT):**
- Apps from Mac App Store / Microsoft Store
- Browser extensions (from official stores)
- Approved software list items

**Employees CANNOT Install:**
- Pirated or unlicensed software
- Software requiring admin privileges (contact IT)
- P2P file sharing apps
- Crypto mining software

**Need Admin Rights?**
Submit ticket explaining why. Temporary admin access can be granted for specific installations.

---

## VPN & Remote Access

### When to Use VPN

**Required:**
- Accessing internal systems from outside office
- Connecting to corporate network remotely
- Accessing databases or development environments
- Handling sensitive customer data

**NOT Required:**
- Google Workspace (email, Drive, Docs)
- Slack, Zoom, Notion
- Public-facing websites and tools

### Setting Up VPN (Cisco AnyConnect)

**First-Time Setup:**
1. Download Cisco AnyConnect from IT Portal
2. Install application
3. Open AnyConnect
4. Enter server: `vpn.apextech.com`
5. Log in with company credentials + MFA

**Connection:**
1. Open Cisco AnyConnect
2. Toggle "Connect"
3. Approve MFA notification (Duo Push)
4. Status shows "Connected" with green checkmark

**Troubleshooting VPN:**
- **Won't connect**: Check internet connection first
- **Slow connection**: Disconnect when not needed (VPN routes all traffic)
- **MFA not working**: Ensure Duo app installed and synced
- **Connection drops**: Check VPN client for updates

### Remote Desktop (If Needed)

Some roles require access to office desktop computers remotely.

**Setup:**
1. Request remote desktop access (IT Portal)
2. IT enables remote access on your office computer
3. Use Microsoft Remote Desktop (Mac) or Remote Desktop Connection (Windows)
4. Connect via VPN first, then remote desktop

---

## Email & Calendar

### Email Best Practices

**Inbox Management:**
- Use labels/folders to organize
- Archive old emails (don't delete unless necessary)
- Unsubscribe from unwanted newsletters
- Set up filters for automated sorting

**Email Quotas:**
- Standard: 30GB per user
- Approaching limit? Delete large attachments or request increase
- Use Google Drive links instead of email attachments

### Out of Office (OOO) Auto-Responder

**When to Set:**
- Vacation/PTO
- Extended sick leave
- Business travel (optional)
- Out for the day (if unavailable)

**How to Set:**
1. Gmail → Settings (gear icon) → See all settings
2. Scroll to "Vacation responder"
3. Enable and set dates
4. Write message (template: apextech.notion.so/ooo-template)
5. Check "Send a response only to people in my organization" (optional)
6. Save

**Good OOO Message Example:**
```
I'm out of office until [date] with limited access to email.

For urgent matters, please contact:
- [Colleague Name] for [topic]: colleague@apextech.solutions
- My manager [Manager Name]: manager@apextech.solutions

I'll respond to your email when I return. Thanks!
```

### Calendar Management

**Scheduling Meetings:**
- Use "Find a time" feature to check availability
- Send calendar invites (don't just email meeting details)
- Include Zoom link, agenda, and any pre-reads
- Set reminders (default: 10 min before)

**Blocking Focus Time:**
- Mark as "Busy" or "Do Not Disturb"
- Title: "Focus Time" or "Deep Work"
- Decline meeting requests during these blocks (politely)

**Sharing Your Calendar:**
- Default: Show "free/busy" to coworkers
- Share details with manager and assistant (if applicable)
- Settings → Share with specific people

---

## Security & Data Protection

### Multi-Factor Authentication (MFA)

**Required On:**
- Email (Google Workspace)
- VPN access
- AWS Console
- GitHub
- Any system with customer data

**Setup Duo Mobile:**
1. Download Duo Mobile app (iOS/Android)
2. Scan QR code during MFA enrollment
3. Approve push notifications to log in

**Backup Codes:**
- Save backup codes in 1Password (under "Duo Backup Codes")
- Use if phone is unavailable

### Phishing Awareness

**Red Flags:**
- Urgent language ("Act now!" "Your account will be closed!")
- Suspicious sender (check email address carefully)
- Requests for passwords, SSN, or financial info
- Unexpected attachments or links
- Spelling/grammar errors

**What to Do:**
1. **DO NOT CLICK** links or download attachments
2. Hover over links to see true destination
3. Forward to phishing@apextech.solutions
4. Delete the email
5. Report in #security Slack channel

**IT will never ask for your password via email or Slack.**

### Data Classification

**Public**: Can be shared freely (marketing materials, public blog posts)
**Internal**: Company-only (internal docs, roadmaps, non-sensitive data)
**Confidential**: Restricted access (customer data, financials, contracts)
**Highly Confidential**: Extremely restricted (trade secrets, legal, HR records)

**Handling Confidential Data:**
- Store in approved locations (Google Drive with permissions)
- Encrypt when sending externally (password-protected zip or secure file transfer)
- Never share via personal email or messaging apps
- Delete when no longer needed
- See [Security Policy](security_policy.md) for full guidelines

### Device Security

**Required:**
- FileVault (Mac) or BitLocker (Windows) encryption - Enabled by default
- Screen lock after 5 minutes idle
- Strong password (no simple PINs)
- Automatic updates enabled
- Antivirus software (IT-managed)

**Best Practices:**
- Lock screen when leaving desk (Win+L / Ctrl+Cmd+Q)
- Don't share computer with family/friends
- Report lost/stolen devices immediately

---

## Troubleshooting Tips

### Before Contacting IT

**Try These First:**
1. **Turn it off and on again** (seriously, this fixes most issues)
2. **Check cables and connections**
3. **Search company wiki** (this document + others)
4. **Ask in #tech-support Slack** (community help)
5. **Google the error message** (someone else had this problem)

### Information to Include in Tickets

**For Best/Fastest Support:**
- **Exact error message** (screenshot is best)
- **Steps to reproduce**:
  1. I opened X application
  2. I clicked Y button
  3. Error appeared
- **What you've already tried**
- **When it started** (today? last week? always?)
- **Operating system & version** (Mac 13.2, Windows 11, etc.)
- **Urgency level** (How does this impact your work?)

### Self-Help Resources

**IT Knowledge Base:** itservices.apextech.com/kb
- Searchable articles for common issues
- Video tutorials
- Setup guides

**Company Wiki:** [Company Wiki](company_wiki.md)
- Software documentation
- Process guides

**LinkedIn Learning:** (via apextech.linkedin.com)
- Software training courses
- IT skills development

---

## Frequently Asked Questions

**Q: Can I use my personal laptop for work?**
A: No. For security and compliance, you must use company-issued devices. Personal devices cannot access company systems.

**Q: What if I spill coffee on my laptop?**
A: Immediately:
1. Unplug and power off
2. Turn upside down to drain
3. Contact IT: ext. 4357
4. Do NOT attempt to turn on

We'll assess damage and provide replacement if needed.

**Q: Can I install software myself?**
A: Some software, yes (see Approved Software List). For anything requiring admin rights or not on the list, submit IT ticket.

**Q: How do I get IT support if I'm traveling abroad?**
A: IT Portal and Slack work globally. For urgent issues, use emergency line: ext. 4911 (international rates apply) or email itsupport@apextech.solutions.

**Q: Why do I need to change my password every 90 days?**
A: Security policy requirement to protect against compromised credentials. Use 1Password to generate and store strong passwords easily.

**Q: Can IT see my personal emails/files?**
A: IT does not monitor individual activities. However, company devices and accounts are company property. For privacy, keep personal data on personal devices.

**Q: What's the fastest way to get help?**
A: For quick questions: #tech-support Slack. For issues needing tracking: IT Portal ticket. For emergencies: Call ext. 4357.

---

## Related Documents
- [Security Policy](security_policy.md) - Data protection and security requirements
- [Onboarding Guide](onboarding_guide.md) - Account setup for new employees
- [Remote Work Policy](remote_work_policy.md) - VPN and remote access guidelines
- [Company Wiki](company_wiki.md) - Technical documentation

---

**IT Support Contact**
- Portal: itservices.apextech.com
- Email: itsupport@apextech.solutions
- Phone: ext. 4357 (HELP)
- Emergency: ext. 4911
- Slack: #tech-support
- Walk-Up: Building A, 1st Floor (SF Office, Mon-Fri 9-5)

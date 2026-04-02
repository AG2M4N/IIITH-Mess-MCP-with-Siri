# Raspberry Pi & Siri Integration Guide

Complete guide to set up the IIITH Mess API on your Raspberry Pi and integrate it with Siri Shortcuts.

---

## Architecture

```
Your iPhone (IIIT VPN)
        ↓
   Siri Shortcut  
   (calls local Pi IP)
        ↓
  Raspberry Pi (IIIT VPN)
        ↓
  Flask API Server
  (port 5000)
        ↓
  mess.iiit.ac.in (via VPN)
```

**No tunneling, no port forwarding — both on the same VPN!**

---

## Prerequisites

- Raspberry Pi (any model with Wi-Fi)
- Python 3.11+ on the Pi
- Pi connected to IIIT VPN
- iPhone with IIIT VPN app installed
- Your MESS_AUTH_KEY from [mess.iiit.ac.in/settings](https://mess.iiit.ac.in/settings)

---

## Step 1: Set Up Raspberry Pi

### SSH into your Pi

```bash
ssh pi@raspberrypi.local
# or
ssh pi@192.168.1.X  # Replace with your Pi's IP
```

### Clone the repository

```bash
cd ~
git clone https://github.com/AG2M4N/IIITH-Mess-MCP-with-Siri-.git
cd IIITH-Mess-MCP-with-Siri-
```

### Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2: Configure AuthenticationKey

### Create `.env` file on Pi

```bash
nano .env
```

Add this line:
```env
MESS_AUTH_KEY=your-actual-auth-key-from-mess.iiit.ac.in
```

Save with: `Ctrl+X → Y → Enter`

### Verify it loaded

```bash
source venv/bin/activate
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Auth key set!' if os.environ.get('MESS_AUTH_KEY') else 'Not found!')"
```

---

## Step 3: Test the API Server (Local)

### Start the server

```bash
source venv/bin/activate
python3 api_wrapper.py
```

You should see:
```
============================================================
IIITH Mess MCP - Siri Integration API
============================================================
Starting server on http://localhost:5000
API Documentation: http://localhost:5000/api/help
...
============================================================
```

### Test in another terminal

```bash
# SSH into Pi in new terminal
ssh pi@raspberrypi.local

# Test the API
curl http://localhost:5000/api/health
```

Should return:
```json
{"status":"ok","authenticated":true}
```

---

## Step 4: Find Your Pi's Local IP

```bash
hostname -I
```

Example output:
```
192.168.1.42
```

**Remember this IP!** You'll use it in Siri Shortcuts.

---

## Step 5: Connect iPhone to IIIT VPN

1. Open iPhone Settings
2. Go to VPN section
3. Add IIIT VPN profile (get from IT services)
4. Connect to VPN
5. Keep it connected when using Shortcuts

---

## Step 6: Create Siri Shortcuts

### Shortcut 1: Health Check

To test the connection:

1. Open **Shortcuts** app
2. Create new shortcut
3. Add action: **URL** → `http://192.168.1.42:5000/api/health` (replace IP with yours)
4. Add action: **Get contents of URL**
5. Add action: **Show Result**
6. Tap ▶️ to test

Should show: `{"status":"ok","authenticated":true}`

---

### Shortcut 2: Register for Meal

**Voice Command:** "Register me for lunch"

1. New Shortcut
2. Add action: **Ask for Text**
   - Prompt: "Date? (YYYY-MM-DD)"
   - Save as: `date`
3. Add action: **Ask for Text**
   - Prompt: "Meal? (breakfast/lunch/snacks/dinner)"
   - Save as: `meal`
4. Add action: **Ask for Text**
   - Prompt: "Mess? (kadamba-nonveg/yuktahar/etc)"
   - Save as: `mess`
5. Add action: **URL** → `http://192.168.1.42:5000/api/meal/register`
6. Add action: **Get contents of URL**
   - Method: **POST**
   - Headers: Add header
     - Key: `Content-Type`
     - Value: `application/json`
   - Request body:
     ```
     {"meal_date": "[date]", "meal_type": "[meal]", "mess_id": "[mess]"}
     ```
7. Add action: **Get Dictionary Value**
   - Select: `message`
8. Add action: **Speak Text**

Test it before adding to Siri!

---

### Shortcut 3: Get Today's Menu

**Voice Command:** "What's for lunch today?"

1. New Shortcut
2. Add action: **URL** → `http://192.168.1.42:5000/api/menus`
3. Add action: **Get contents of URL**
4. Add action: **Show Result**

---

### Shortcut 4: Check Registrations

**Voice Command:** "Show my meals"

1. New Shortcut
2. Add action: **URL** → `http://192.168.1.42:5000/api/meals/registrations`
3. Add action: **Get contents of URL**
4. Add action: **Show Result**

---

### Shortcut 5: Cancel a Meal

**Voice Command:** "Cancel my lunch"

1. New Shortcut
2. Add action: **Ask for Text**
   - Prompt: "Date? (YYYY-MM-DD)"
   - Save as: `date`
3. Add action: **Ask for Text**
   - Prompt: "Meal? (breakfast/lunch/snacks/dinner)"
   - Save as: `meal`
4. Add action: **URL** → `http://192.168.1.42:5000/api/meal/cancel`
5. Add action: **Get contents of URL**
   - Method: **POST**
   - Headers: `Content-Type: application/json`
   - Body: `{"meal_date": "[date]", "meal_type": "[meal]"}`
6. Add action: **Get Dictionary Value** → `message`
7. Add action: **Speak Text**

---

## Step 7: Add to Siri

For each Shortcut:

1. Tap **...** (menu button)
2. Tap **Add to Siri**
3. Tap record button 🎤
4. Say your command (e.g., "Register me for lunch")
5. Tap **Done**

Now you can say: **"Hey Siri, register me for lunch"**

---

## Optional: Auto-start on Pi Boot

### Create systemd service

```bash
sudo nano /etc/systemd/system/mess-api.service
```

Paste:
```ini
[Unit]
Description=IIITH Mess API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/IIITH-Mess-MCP-with-Siri-
Environment="PATH=/home/pi/IIITH-Mess-MCP-with-Siri-/venv/bin"
ExecStart=/home/pi/IIITH-Mess-MCP-with-Siri-/venv/bin/python3 api_wrapper.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and start

```bash
sudo systemctl enable mess-api
sudo systemctl start mess-api
sudo systemctl status mess-api
```

### Check logs

```bash
sudo journalctl -u mess-api -f
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" in Shortcut | Make sure Pi is running: `ssh pi@raspberrypi.local` then check `ps aux\|grep api_wrapper` |
| "Timeout" error | Ensure both Pi and iPhone are on IIIT VPN |
| "Authentication failed" | Check MESS_AUTH_KEY in `.env` on Pi |
| Can't find Pi IP | On Pi: `hostname -I` or on Mac: `nmap -sn 192.168.1.0/24` |
| Shortcut can't reach Pi | Try: `curl http://192.168.1.42:5000/api/health` from iPhone on VPN (via Shortcuts URL action) |

---

## Quick Command Reference

```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Check if API is running
ps aux | grep api_wrapper

# View logs (if running as service)
sudo journalctl -u mess-api -f

# Restart service
sudo systemctl restart mess-api

# Find Pi's IP
hostname -I

# Test API
curl http://192.168.1.42:5000/api/health
```

---

## API Endpoints

```
GET  /api/health                  - Health check
GET  /api/help                    - API documentation
GET  /api/menus?date=YYYY-MM-DD   - Get menus
POST /api/meal/register           - Register for meal
POST /api/meal/cancel             - Cancel meal
GET  /api/meals/registrations     - Get your registrations
GET  /api/messes                  - List all messes
```

---

## Next Steps

1. ✅ SSH to Pi and clone repo
2. ✅ Set up `.env` with MESS_AUTH_KEY
3. ✅ Test locally with `curl`
4. ✅ Create one test Shortcut
5. ✅ Connect iPhone to VPN
6. ✅ Test Shortcut from iPhone
7. ✅ Add to Siri
8. ✅ Say "Hey Siri, ..." 🎙️

Enjoy voice-controlled meal registration! 🚀

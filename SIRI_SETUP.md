# Siri Integration for IIITH Mess MCP

Complete guide to integrate your IIITH Mess registration with Siri on iOS/macOS.

## Overview

The REST API wrapper (`api_wrapper.py`) creates a local web server that Siri Shortcuts can communicate with. You can then create voice commands like:

- "Register me for lunch tomorrow at Kadamba"
- "What's on the menu today?"
- "Show my meal registrations"
- "Cancel my dinner registration"

---

## Step 1: Start the REST API Server

### Option A: Local Development (Testing)

```bash
# Install dependencies
pip install flask flask-cors

# Set your auth key
export MESS_AUTH_KEY="your-api-key-from-mess.iiit.ac.in"

# Run the API server
python api_wrapper.py
```

Server runs on `http://localhost:5000`

### Option B: Deploy to Cloud (Production)

Recommended platforms:
- **Vercel** (free tier, Python support)
- **Railway** (free credits)
- **Heroku** (paid, but simple)
- **AWS Lambda** + API Gateway

For persistent hosting, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Step 2: Create Siri Shortcuts

### Shortcut 1: Login to Mess Service

**Requirements:**
- Shortcut app (iOS 14+/macOS 11+)

**Setup:**

1. Open **Shortcuts** app
2. Tap **+ Create Shortcut**
3. Add action: **URL**
   - Enter: `http://localhost:5000/api/auth/login` (or your deployed server URL)
4. Add action: **Request Body**
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "user": "your-email@msitprogram.net",
       "password": "your-password"
     }
     ```
5. Add action: **Get Dictionary Value**
   - Select: `success` key
6. Add action: **Show Result** or **Speak Text**

---

### Shortcut 2: Register for a Meal

**Voice Command:** "Register me for lunch"

1. Open **Shortcuts** app
2. Tap **+ Create Shortcut**
3. Add action: **Ask for [Text]**
   - Prompt: "What date? (YYYY-MM-DD, or 'tomorrow')"
   - Save as: `date_input`
4. Add action: **Ask for [Number]**
   - Prompt: "Breakfast (1), Lunch (2), Snacks (3), or Dinner (4)?"
   - Save as: `meal_choice`
5. Add action: **Choose from List**
   - Items: breakfast, lunch, snacks, dinner
   - Save as: `meal`
6. Add action: **Ask for [Text]**
   - Prompt: "Which mess? (e.g., kadamba-nonveg, yuktahar)"
   - Save as: `mess`
7. Add action: **URL** 
   - Text: `http://localhost:5000/api/meal/register`
8. Add action: **Get contents of URL**
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Body (use **Text** action to construct):
     ```
     {
       "meal_date": "[date_input]",
       "meal_type": "[meal]",
       "mess_id": "[mess]"
     }
     ```
9. Add action: **Get Dictionary Value** → `message`
10. Add action: **Speak Text**

---

### Shortcut 3: Get Today's Menu

**Voice Command:** "What's for lunch today?"

1. Create new shortcut
2. Add action: **Ask for [Text]**
   - Prompt: "Which meal? (breakfast, lunch, snacks, dinner)"
   - Save as: `meal`
3. Add action: **URL**
   - Text: `http://localhost:5000/api/menus`
4. Add action: **Get contents of URL**
   - Method: `GET`
5. Add action: **Get Dictionary Value** → `menus`
6. Add action: **Choose from List**
   - Items: Show available messes
7. Add action: **Speak Text**

---

### Shortcut 4: Check My Registrations

**Voice Command:** "Show my meal registrations"

1. Create new shortcut
2. Add action: **URL**
   - Text: `http://localhost:5000/api/meals/registrations`
3. Add action: **Get contents of URL**
   - Method: `GET`
4. Add action: **Get Dictionary Value** → `registrations`
5. Add action: **Show Result** (displays list)

---

### Shortcut 5: Cancel a Meal

**Voice Command:** "Cancel my lunch"

1. Create new shortcut
2. Add action: **Ask for [Text]**
   - Prompt: "Which date? (YYYY-MM-DD)"
   - Save as: `date`
3. Add action: **Ask for [Text]**
   - Prompt: "Which meal? (breakfast, lunch, snacks, dinner)"
   - Save as: `meal`
4. Add action: **URL**
   - Text: `http://localhost:5000/api/meal/cancel`
5. Add action: **Get contents of URL**
   - Method: `POST`
   - Body: `{"meal_date": "[date]", "meal_type": "[meal]"}`
6. Add action: **Get Dictionary Value** → `message`
7. Add action: **Speak Text**

---

## Step 3: Add Voice Commands

### iOS/macOS Siri Integration

1. Open each Shortcut
2. Tap **...** (more menu)
3. Tap **Add to Siri**
4. Tap the record button 🎤
5. Say your phrase, e.g., "Register me for lunch"
6. Tap **Done**

Now you can say: **"Hey Siri, register me for lunch"** and it will walk you through the process!

---

## Step 4: Advanced Setup

### Using Devices on Same WiFi Network

If your Mac/iPhone is on the same network as your API server:

1. Get your Mac's local IP: `ifconfig | grep inet`
2. Replace `localhost:5000` with `192.168.1.X:5000` in shortcuts

### Using ngrok for Remote Access (Testing)

```bash
brew install ngrok
ngrok http 5000
```

Uses the provided HTTPS URL in your Shortcuts instead of `localhost`.

---

## API Endpoint Reference

### Authentication
```
POST /api/auth/login
Body: { "user": "email@msit.net", "password": "pwd" }

POST /api/auth/logout
```

### Registrations
```
POST /api/meal/register
Body: { "meal_date": "2026-04-05", "meal_type": "lunch", "mess_id": "kadamba-nonveg" }

POST /api/meal/cancel
Body: { "meal_date": "2026-04-05", "meal_type": "lunch" }

GET /api/meals/registrations?from_date=2026-04-01&to_date=2026-04-30
```

### Info
```
GET /api/menus?date=2026-04-05
GET /api/messes
GET /api/health
```

---

## Troubleshooting

### "Connection Refused" Error in Shortcut

**Cause:** Server not running or wrong IP/port  
**Fix:**
```bash
# Check if server is running
curl http://localhost:5000/api/health

# If not, start it
python api_wrapper.py
```

### "Timeout" Error

**Cause:** Server is on VPN, shortcut is not  
**Fix:** Make sure both your Mac and iPhone are on IIIT VPN before running shortcuts

### "Authentication Failed"

**Cause:** Wrong credentials or expired session  
**Fix:** Re-login via the Login shortcut first

### Server Returns "Missing MESS_AUTH_KEY"

**Fix:**
```bash
export MESS_AUTH_KEY="your-key-here"
python api_wrapper.py
```

---

## Next Steps

1. ✅ Run `python api_wrapper.py`
2. ✅ Create one Shortcut (start with "Register for Meal")
3. ✅ Test via Shortcut app before adding to Siri
4. ✅ Add voice phrase via "Add to Siri"
5. ✅ Say "Hey Siri, ..." to test!

---

## Security Notes

⚠️ **Important:** 
- Don't hardcode passwords in shortcuts (use login shortcut first)
- Deploy to HTTPS endpoint if exposed to internet
- Use API keys instead of passwords when possible
- Keep `MESS_AUTH_KEY` private

---

## Support

For issues with:
- **Shortcuts syntax**: Check Apple's Shortcuts documentation
- **REST API errors**: Test endpoint with `curl` first
- **MCP tools**: Check [iiith_mess_mcp documentation](README.md)

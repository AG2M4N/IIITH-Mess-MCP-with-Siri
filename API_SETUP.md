# REST API Setup & Deployment Guide

Complete guide to set up and deploy the REST API wrapper for the IIITH Mess MCP Server.

---

## Local Setup (Development)

### Prerequisites

- Python 3.13+
- `uv` or `pip`
- IIIT VPN access
- Auth key from [mess.iiit.ac.in/settings](https://mess.iiit.ac.in/settings)

### Installation

```bash
# Clone the repository
git clone https://github.com/Kallind/IIITH-Mess-MCP.git
cd IIITH-Mess-MCP

# Install dependencies
uv pip install -e .
# OR with pip:
# pip install -e .

# Create .env file
cp .env.example .env  # or manually create it
```

### Configuration

Edit `.env`:

```env
MESS_AUTH_KEY=your-api-key-from-mess.iiit.ac.in
FLASK_ENV=development
FLASK_DEBUG=true
```

### Running the API Server

```bash
# Terminal 1: Start the API server
python api_wrapper.py
```

Output:
```
============================================================
IIITH Mess MCP - Siri Integration API
============================================================
Starting server on http://localhost:5000
API Documentation: http://localhost:5000/api/help
...
============================================================
```

### Testing the API

In another terminal:

```bash
# Health check
curl http://localhost:5000/api/health

# Get API documentation
curl http://localhost:5000/api/help

# Get menus for today
curl http://localhost:5000/api/menus

# Get all messes
curl http://localhost:5000/api/messes

# Register for a meal (requires auth)
curl -X POST http://localhost:5000/api/meal/register \
  -H "Content-Type: application/json" \
  -d '{
    "meal_date": "2026-04-05",
    "meal_type": "lunch",
    "mess_id": "kadamba-nonveg"
  }'
```

---

## Remote Deployment

### Option 1: Railway (Recommended for Beginners)

Railway is free tier-friendly with simple GitHub integration.

#### Steps:

1. **Create Railway account**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your IIITH-Mess-MCP fork

3. **Configure environment**
   - Go to Project Settings → Variables
   - Add: `MESS_AUTH_KEY=your-key-here`

4. **Deploy**
   - Railway auto-deploys on GitHub push
   - Your API is live at: `https://your-project.railway.app`

5. **Test**
   ```bash
   curl https://your-project.railway.app/api/health
   ```

---

### Option 2: Vercel (Python Support)

#### Steps:

1. **Create Vercel account** (vercel.com)
2. **Install Vercel CLI**: `npm install -g vercel`
3. **Deploy Django/FastAPI app instead** (Vercel has limited Python support)
   - OR use Railway/Heroku for better Python support

---

### Option 3: Heroku (Traditional Approach)

#### Steps:

1. **Sign up** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI**:
   ```bash
   brew tap heroku/brew && brew install heroku
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create iiith-mess-api
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set MESS_AUTH_KEY="your-key-here"
   ```

5. **Create `Procfile`** in repo root:
   ```
   web: python api_wrapper.py
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **View logs**:
   ```bash
   heroku logs --tail
   ```

---

### Option 4: AWS Lambda + API Gateway

For a serverless approach:

1. Use [Zappa](https://github.com/zappa/Zappa) to deploy Flask to AWS Lambda
2. Or migrate to AWS Lambda-native function

```bash
pip install zappa
zappa init
zappa deploy production
```

---

### Option 5: Self-Hosted (Your Own Server)

For a VPS/dedicated server:

1. **SSH into server**
2. **Install Python 3.13+**
3. **Clone repo**:
   ```bash
   git clone <repo>
   cd IIITH-Mess-MCP
   ```

4. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

5. **Set environment variables**:
   ```bash
   export MESS_AUTH_KEY="your-key"
   ```

6. **Run with Gunicorn** (production server):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api_wrapper:app
   ```

7. **Setup reverse proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
       }
   }
   ```

8. **Enable HTTPS** with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot run -n --agree-tos -d your-domain.com -m your-email@example.com
   ```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "api_wrapper.py"]
```

### Build & Run

```bash
# Build image
docker build -t iiith-mess-api .

# Run locally
docker run -e MESS_AUTH_KEY="your-key" -p 5000:5000 iiith-mess-api

# Push to Docker Hub
docker tag iiith-mess-api yourusername/iiith-mess-api
docker push yourusername/iiith-mess-api
```

### Deploy to Docker Container Service
- **AWS ECS**
- **Google Cloud Run**
- **Azure Container Instances**

---

## Using ngrok for Testing (Without Public Deployment)

Useful for testing Shortcuts on your iPhone without deploying:

```bash
# Install ngrok
brew install ngrok

# Start API server locally
python api_wrapper.py

# In another terminal, expose it
ngrok http 5000
```

You'll get a URL like: `https://abc123.ngrok.io`

Use this URL in your Siri Shortcuts instead of `localhost:5000`.

---

## Monitoring & Logs

### Local Development

```bash
# Run with verbose logging
FLASK_DEBUG=true python api_wrapper.py
```

### Production (Heroku)

```bash
heroku logs --tail
```

### Production (Railway)

View logs in Railway dashboard

### Production (Self-hosted)

```bash
# Using systemd
sudo journalctl -u iiith-mess-api -f

# Or check gunicorn logs
tail -f /var/log/iiith-mess-api/access.log
```

---

## Performance Optimization

### For High Traffic

1. **Add caching**:
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   ```

2. **Use async workers**:
   ```bash
   gunicorn -w 8 -k gevent api_wrapper:app
   ```

3. **Add rate limiting**:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   ```

4. **Use a database** to cache menus/info

---

## Security Checklist

- [ ] Move `MESS_AUTH_KEY` to environment variables (never commit to git)
- [ ] Enable CORS only for trusted domains (if public)
- [ ] Use HTTPS in production
- [ ] Add rate limiting to prevent abuse
- [ ] Add input validation on all endpoints
- [ ] Use API key authentication for shortcut requests
- [ ] Enable logging for audit trail
- [ ] Rotate API keys regularly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install flask flask-cors` |
| `Port 5000 already in use` | `lsof -i :5000` to find process, then kill it |
| `Timeout errors` | Check IIIT VPN connectivity, MESS_AUTH_KEY validity |
| `CORS errors in Shortcuts` | Make sure `flask_cors.CORS(app)` is called in api_wrapper.py |
| `500 Internal Server Error` | Check server logs with `python api_wrapper.py` in debug mode |

---

## Next Steps

1. ✅ Run `python api_wrapper.py` locally
2. ✅ Test endpoints with `curl`
3. ✅ Create Siri Shortcuts (see [SIRI_SETUP.md](SIRI_SETUP.md))
4. ✅ Test Shortcuts on device
5. ✅ Deploy to production (Railway/Heroku)
6. ✅ Update Shortcut URLs to use deployed endpoint

---

## Support

- API issues? Run `curl http://localhost:5000/api/help`
- Flask docs: https://flask.palletsprojects.com
- MCP tools: See [iiith_mess_mcp documentation](README.md)

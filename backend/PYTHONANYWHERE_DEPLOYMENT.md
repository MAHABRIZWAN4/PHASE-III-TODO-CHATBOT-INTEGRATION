# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (free tier)
- GitHub repository with your code

## Step-by-Step Deployment Instructions

### Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Click "Start running Python online in less than a minute!"
3. Sign up for a free Beginner account
4. Verify your email

### Step 2: Open Bash Console
1. After login, go to "Consoles" tab
2. Click "Bash" to open a new bash console

### Step 3: Clone Your Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO/backend
```

### Step 4: Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 myenv
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Create Web App
1. Go to "Web" tab in PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Click "Next"

### Step 7: Configure WSGI File
1. In the "Web" tab, find "Code" section
2. Click on the WSGI configuration file link
3. Delete all existing content
4. Copy content from your `wsgi.py` file
5. Update the following:
   - Replace `YOUR_USERNAME` with your PythonAnywhere username
   - Update all environment variables with your actual values
6. Save the file

### Step 8: Set Virtual Environment Path
1. In "Web" tab, find "Virtualenv" section
2. Enter: `/home/YOUR_USERNAME/.virtualenvs/myenv`
3. Replace `YOUR_USERNAME` with your actual username

### Step 9: Configure Static Files (Optional)
If you have static files:
1. In "Web" tab, find "Static files" section
2. Add URL: `/static/`
3. Add Directory: `/home/YOUR_USERNAME/backend/static/`

### Step 10: Reload Web App
1. Scroll to top of "Web" tab
2. Click the green "Reload" button
3. Wait for reload to complete

### Step 11: Test Your API
1. Your API will be available at: `https://YOUR_USERNAME.pythonanywhere.com`
2. Test endpoints:
   - `https://YOUR_USERNAME.pythonanywhere.com/health`
   - `https://YOUR_USERNAME.pythonanywhere.com/docs`

## Environment Variables to Update in wsgi.py

**IMPORTANT:** Copy these values from your `backend/.env` file. Do NOT commit real API keys to GitHub!

```python
os.environ['DATABASE_URL'] = 'your_neon_database_url_here'
os.environ['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_EXPIRE_MINUTES'] = '10080'
os.environ['BETTER_AUTH_SECRET'] = 'your_better_auth_secret_here'
os.environ['BETTER_AUTH_URL'] = 'https://YOUR_USERNAME.pythonanywhere.com'
os.environ['AI_PROVIDER'] = 'groq'
os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
os.environ['GROQ_MODEL'] = 'llama-3.1-8b-instant'
os.environ['OPENROUTER_API_KEY'] = 'your_openrouter_api_key_here'
os.environ['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
os.environ['OPENROUTER_MODEL'] = 'google/gemini-flash-1.5-8b'
```

**Where to find these values:**
- All values are in your `backend/.env` file
- Copy them from there when configuring wsgi.py on PythonAnywhere

## Troubleshooting

### Error: "ImportError: No module named 'fastapi'"
- Make sure you activated the virtual environment
- Run: `pip install -r requirements.txt`

### Error: "Application not loading"
- Check error logs in "Web" tab → "Log files" section
- Verify WSGI file configuration
- Ensure virtual environment path is correct

### Error: "Database connection failed"
- Verify DATABASE_URL in wsgi.py
- Check if Neon database is accessible from PythonAnywhere

### Chat not working
- Check error logs
- Verify all environment variables are set
- Ensure app.models and app.services are properly imported

## Important Notes

1. **Free Tier Limitations:**
   - Your app will sleep after inactivity
   - Limited CPU time per day
   - No HTTPS for custom domains (only pythonanywhere.com subdomain)

2. **Updating Code:**
   ```bash
   cd ~/YOUR_REPO/backend
   git pull origin main
   # Then reload web app from dashboard
   ```

3. **Viewing Logs:**
   - Go to "Web" tab
   - Scroll to "Log files" section
   - Check error.log and server.log

## Success Indicators

✓ Web app shows "Running" status (green)
✓ `/health` endpoint returns `{"status": "healthy"}`
✓ `/docs` shows Swagger UI
✓ Chat endpoint works without 404 error

## Next Steps After Deployment

1. Update frontend environment variable:
   - `NEXT_PUBLIC_API_URL=https://YOUR_USERNAME.pythonanywhere.com`
2. Redeploy frontend on Vercel
3. Test complete application flow

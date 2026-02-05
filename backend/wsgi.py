"""
WSGI configuration for PythonAnywhere deployment.

This file configures the WSGI application for running FastAPI on PythonAnywhere.
"""

import sys
import os
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/backend'  # Update this with your PythonAnywhere username
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DATABASE_URL'] = 'your_database_url_here'
os.environ['JWT_SECRET_KEY'] = 'your_jwt_secret_here'
os.environ['JWT_ALGORITHM'] = 'HS256'
os.environ['JWT_EXPIRE_MINUTES'] = '10080'
os.environ['BETTER_AUTH_SECRET'] = 'your_auth_secret_here'
os.environ['BETTER_AUTH_URL'] = 'https://YOUR_USERNAME.pythonanywhere.com'
os.environ['AI_PROVIDER'] = 'groq'
os.environ['GROQ_API_KEY'] = 'your_groq_api_key_here'
os.environ['GROQ_MODEL'] = 'llama-3.1-8b-instant'
os.environ['OPENROUTER_API_KEY'] = 'your_openrouter_key_here'
os.environ['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
os.environ['OPENROUTER_MODEL'] = 'google/gemini-flash-1.5-8b'

# Import the FastAPI application
from main import app

# PythonAnywhere expects an 'application' variable
application = app

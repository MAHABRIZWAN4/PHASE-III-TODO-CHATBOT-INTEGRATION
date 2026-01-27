# Dashboard Loading Issue - Debug Steps

## Issue
Dashboard page stuck on loading spinner, not showing content.

## Possible Causes
1. Backend not running
2. API call failing
3. CORS issue
4. Authentication token issue

## Debug Steps

### Step 1: Check if backend is running
```bash
# In terminal 1
cd backend
uvicorn app.main:app --reload
```

### Step 2: Check browser console
Open browser DevTools (F12) and check:
- Console tab for JavaScript errors
- Network tab for failed API requests
- Look for `/api/tasks` request status

### Step 3: Test API directly
```bash
# Get your auth token from localStorage (in browser console):
# localStorage.getItem('auth_token')

# Then test API:
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/tasks
```

## Quick Fix

If backend is running but still loading, add error handling to dashboard:

1. Check if getTasks() is throwing an error
2. Add console.log to see what's happening
3. Check if auth token exists

## Common Solutions

1. **Backend not running**: Start backend with `uvicorn app.main:app --reload`
2. **No auth token**: Logout and login again
3. **CORS issue**: Check backend CORS settings
4. **API endpoint wrong**: Verify NEXT_PUBLIC_API_URL in .env.local

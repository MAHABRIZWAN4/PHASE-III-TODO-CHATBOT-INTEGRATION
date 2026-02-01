# 🔐 Environment Variables Reference

## How to Get Your Secret Values

All the secret values you need are in your `backend/.env` file. Here's how to use them:

### Step 1: View Your Secrets

Run this command to see your environment variables:

```bash
cat backend/.env
```

### Step 2: Copy Values for Vercel

When configuring Vercel, copy the exact values from your `backend/.env` file for these variables:

#### For Frontend (3 variables):
1. `NEXT_PUBLIC_API_URL` = `https://backend-one-wine-71.vercel.app` (already provided)
2. `BETTER_AUTH_SECRET` = Copy from `backend/.env`
3. `BETTER_AUTH_URL` = `https://frontend-kappa-ruddy-34.vercel.app` (already provided)

#### For Backend (11 variables):
1. `DATABASE_URL` = Copy from `backend/.env`
2. `BETTER_AUTH_SECRET` = Copy from `backend/.env` (same as frontend)
3. `JWT_SECRET_KEY` = Copy from `backend/.env`
4. `JWT_ALGORITHM` = `HS256` (already provided)
5. `JWT_EXPIRE_MINUTES` = `10080` (already provided)
6. `BETTER_AUTH_URL` = `https://backend-one-wine-71.vercel.app` (already provided)
7. `AI_PROVIDER` = `groq` (already provided)
8. `GROQ_API_KEY` = Copy from `backend/.env`
9. `GROQ_MODEL` = `llama-3.1-8b-instant` (already provided)
10. `OPENROUTER_API_KEY` = Copy from `backend/.env`
11. `OPENROUTER_BASE_URL` = `https://openrouter.ai/api/v1` (already provided)
12. `OPENROUTER_MODEL` = `google/gemini-flash-1.5-8b` (already provided)

### Quick Reference Table

| Variable | Where to Get Value |
|----------|-------------------|
| `DATABASE_URL` | `backend/.env` line 4 |
| `BETTER_AUTH_SECRET` | `backend/.env` line 7 |
| `JWT_SECRET_KEY` | `backend/.env` line 10 |
| `GROQ_API_KEY` | `backend/.env` line 22 |
| `OPENROUTER_API_KEY` | `backend/.env` line 26 |

---

## Security Note

⚠️ **IMPORTANT**: These values are secrets and should NEVER be committed to Git or shared publicly. They are only stored in:
- Your local `backend/.env` file (already in .gitignore)
- Vercel's encrypted environment variables (secure)

The documentation files now reference these values without exposing them.

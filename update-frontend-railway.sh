#!/bin/bash
# Frontend Update Script for Railway Backend
# Usage: ./update-frontend-railway.sh <RAILWAY_BACKEND_URL>

RAILWAY_URL=$1

if [ -z "$RAILWAY_URL" ]; then
    echo "Usage: ./update-frontend-railway.sh <RAILWAY_URL>"
    echo "Example: ./update-frontend-railway.sh https://backend-production-xxxx.up.railway.app"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         UPDATING FRONTEND TO USE RAILWAY BACKEND               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Railway Backend URL: $RAILWAY_URL"
echo ""

# Update Vercel environment variable
echo "1️⃣  Updating Vercel environment variable..."
cd frontend
vercel env rm NEXT_PUBLIC_API_URL production --yes 2>/dev/null
vercel env add NEXT_PUBLIC_API_URL production <<EOF
$RAILWAY_URL
EOF

echo "2️⃣  Redeploying frontend on Vercel..."
vercel --prod --yes

echo ""
echo "✅ Frontend updated and redeployed!"
echo ""
echo "Frontend URL: https://frontend-kappa-ruddy-34.vercel.app"
echo "Backend URL: $RAILWAY_URL"

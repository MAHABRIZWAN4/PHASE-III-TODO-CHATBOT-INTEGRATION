#!/bin/bash
# Frontend Update Script for Render Backend
# Usage: ./update-frontend-render.sh <RENDER_BACKEND_URL>

RENDER_URL=$1

if [ -z "$RENDER_URL" ]; then
    echo "Usage: ./update-frontend-render.sh <RENDER_URL>"
    echo "Example: ./update-frontend-render.sh https://backend-production-xxxx.up.render.app"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         UPDATING FRONTEND TO USE RENDER BACKEND               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Render Backend URL: $RENDER_URL"
echo ""

# Update Vercel environment variable
echo "1️⃣  Updating Vercel environment variable..."
cd frontend
vercel env rm NEXT_PUBLIC_API_URL production --yes 2>/dev/null
vercel env add NEXT_PUBLIC_API_URL production <<EOF
$RENDER_URL
EOF

echo "2️⃣  Redeploying frontend on Vercel..."
vercel --prod --yes

echo ""
echo "✅ Frontend updated and redeployed!"
echo ""
echo "Frontend URL: https://frontend-kappa-ruddy-34.vercel.app"
echo "Backend URL: $RENDER_URL"

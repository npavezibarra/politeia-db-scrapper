#!/bin/bash

# Session Hijacking Setup Script
# This script helps you set up Chrome for session hijacking

echo "============================================================"
echo "CHROME SESSION HIJACKING SETUP"
echo "============================================================"
echo ""
echo "This will:"
echo "1. Kill any existing Chrome processes"
echo "2. Start Chrome with remote debugging enabled"
echo "3. Open the Emol website for you"
echo ""
echo "Press ENTER to continue..."
read

echo ""
echo "🔴 Killing existing Chrome processes..."
killall "Google Chrome" 2>/dev/null || true
sleep 2

echo "✓ Chrome closed"
echo ""
echo "🚀 Starting Chrome with remote debugging..."
echo ""
echo "IMPORTANT: Do NOT close this Terminal window!"
echo "           Keep Chrome running in the background."
echo ""
echo "In the Chrome window that opens:"
echo "  1. Click 'Alcaldes'"
echo "  2. Click Region 'I' (Tarapacá)"
echo "  3. Scroll around, move your mouse (act human!)"
echo ""
echo "Then, in a NEW Terminal window, run:"
echo "  python3 /Users/nicolas/Desktop/PoliteiaDB/I/scrape_with_user_session.py"
echo ""
echo "============================================================"
echo ""

# Start Chrome and open the URL
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug \
  "https://www.emol.com/especiales/2024/nacional/elecciones2024/resultados.asp" \
  &

echo "✓ Chrome started with debugging enabled"
echo "✓ Opening Emol website..."
echo ""
echo "Keep this window open! Chrome is running in the background."
echo "Press Ctrl+C when you're done scraping to close Chrome."
echo ""

# Wait for user to finish
wait

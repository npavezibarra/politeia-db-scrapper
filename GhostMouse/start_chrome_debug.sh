#!/bin/bash
echo "🚀 Starting Google Chrome in Remote Debugging Mode (Port 9222)..."
echo "⚠️  Please close any other running instances of Chrome first!"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug-session"

echo "✅ Chrome closed."

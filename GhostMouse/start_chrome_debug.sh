#!/bin/bash
echo "🚀 Starting Google Chrome in Remote Debugging Mode (Port 9222)..."
echo "⚠️  Please close any other running instances of Chrome first!"


# Generate a unique temporary directory for this session
USER_DATA_DIR=$(mktemp -d /tmp/chrome-debug-XXXXXX)
echo "📂 Using temporary profile: $USER_DATA_DIR"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$USER_DATA_DIR" \
  --no-first-run \
  --no-default-browser-check

echo "✅ Chrome closed."

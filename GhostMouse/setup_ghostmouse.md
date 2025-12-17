# GhostMouse Setup Guide 👻

The **GhostMouse** scraper uses the `pyautogui` library to simulate physical mouse movements and clicks. This is necessary to bypass Emol's bot detection, which checks for "trusted" (human) events.

On macOS, applications are blocked from controlling the mouse by default. You must explicitly grant permission.

## 🚨 Critical Step: Granting Accessibility Permissions

If you do not do this, the script will run but the mouse **will not move**.

1.  Open **System Settings** (or System Preferences).
2.  Go to **Privacy & Security** -> **Accessibility**.
3.  Look for your **Terminal Application** in the list.
    *   If you are running the script from **VS Code**, look for "Visual Studio Code".
    *   If you are running from **iTerm** or standard **Terminal**, look for those names.
4.  **Toggle the switch to ON (Blue)**.

### What if my app is not in the list?
1.  Click the small **`+`** button at the bottom of the list.
2.  Navigate to **Applications** (or `Applications/Utilities`).
3.  Select your Terminal app (e.g., `Terminal.app`, `iTerm.app`, or `Visual Studio Code.app`).
4.  Click **Open**.
5.  Ensure the toggle is **ON**.

## 🔄 Restart Required!
Permissions **do not take effect immediately**. You must:
1.  **Quit** your Terminal or VS Code completely (Cmd+Q).
2.  **Re-open** it.

## ✅ Verification
We have included a simple test script to verify that permissions are working correctly.

Run this command:
```bash
python3 /Users/nicolas/Desktop/PoliteiaDB/GhostMouse/test_mouse.py
```

*   **Success:** The mouse cursor moves in a square shape.
*   **Failure:** The mouse stays still (you likely need to check permissions or restart).

## Running the Scraper
Once verified, you can run the full scraper:

```bash
python3 /Users/nicolas/Desktop/PoliteiaDB/GhostMouse/scraper_2021.py
```

**⚠️ IMPORTANT:** Do not touch the mouse while the scraper is running!


import subprocess
import time
import os

def launch_chrome_debug():
    """
    Launches Google Chrome on macOS with remote debugging enabled on port 9222.
    Uses a temporary user data directory to avoid conflicts with your main Chrome instance.
    """
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    if not os.path.exists(chrome_path):
        print(f"Error: Chrome executable not found at {chrome_path}")
        return

    # Check if a Chrome instance is already running on port 9222 (simple check)
    # This isn't perfect but helps avoid multiple instances
    # You can also manually check with fields like `lsof -i :9222`
    
    command = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=/tmp/chrome_dev_session",
        "https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp"
    ]
    
    print("Launching Chrome with remote debugging...")
    print(f"Command: {' '.join(command)}")
    
    # process = subprocess.Popen(command)
    # Using Popen allows the script to finish while Chrome stays open
    subprocess.Popen(command)
    
    print("\nChrome launched!")
    print("1. Ensure the window is visible on your screen (do not minimize).")
    print("2. You can now run the scraper: python3 GhostMouse/scraper_2021.py")

if __name__ == "__main__":
    launch_chrome_debug()

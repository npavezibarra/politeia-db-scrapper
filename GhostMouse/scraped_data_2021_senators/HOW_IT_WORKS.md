# How the 2021 Senatorial Scraper Works ("GhostMouse" Method)

This scraper differs significantly from traditional web scrapers (like Beautiful Soup or standard Selenium/Playwright) because it is designed to bypass **aggressive bot detection** and CAPTCHAs, specifically for the Emol 2021 results page.

## The Core Problem

The Emol 2021 elections page uses advanced security measures that detect:
1.  **Headless Browsers**: Scripts running without a visible UI are blocked.
2.  **Non-Human Inputs**: Programmatic clicks (via JS or standard WebDriver API) often fail or trigger "Are you a robot?" checks.
3.  **Clean Sessions**: Browsers without cookies/history/user-profiles are flagged.

## The "GhostMouse" Solution

To overcome this, we utilize a **Hybrid "GhostMouse" Approach**:

1.  **Human-Controlled Browser Session**: 
    - We do NOT launch a new browser instance from Python.
    - Instead, the **User** launches Google Chrome manually with a special flag: `--remote-debugging-port=9222`.
    - This allows the Python script to "hijack" an existing, legitimate, human-operated window.

2.  **Physical Mouse Simulation (`pyautogui`)**:
    - Instead of asking the browser to "click selector `#btn`" (which can be detected), the script calculates the **screen coordinates** (pixels X, Y) of the element.
    - It then uses the operating system's mouse driver to physically move the cursor and click. To the website, this looks 100% like a human user.

3.  **Data Extraction via CDP (`playwright`)**:
    - While the mouse clicks are physical, reading the data is done via the **Chrome DevTools Protocol (CDP)**.
    - We connect `playwright` to the `localhost:9222` debug port.
    - This allows us to read the DOM (HTML) instantly after a click to extract text, numbers, and classes (like "ganador").

## Technical Workflow

### 1. Initialization
The user runs `./GhostMouse/start_chrome_debug.sh`. This starts Chrome with the remote debugging port open. The user **manually navigates** to the target page ("Emol Senadores 2021"). This ensures all "human" checks (CAPTCHAs, cookies) are passed before the script even starts.

### 2. Targeting
The script (`scraper_2021_senators.py`) connects to the browser. For each region (e.g., "II", "IV"):
- It finds the HTML element for that region button.
- It calculates where that element is on your screen.
- It moves the mouse and clicks it.

### 3. Extraction
Once the region is clicked, the specific senator results for that region load dynamically. The script then:
- Scrapes the Regional Total stats (Valid, Null, Blank votes).
- Iterates through the list of candidates to extract names, parties, votes, and "elected" status.
- Saves the data to `scraped_data_2021_senators/{REGION}/region_{code}_data.json`.

## Why this is customized
Standard scrapers iterate through **Communes**. However, for the Senatorial view on this specific site, the data is presented by **Region** (Circunscripción Senatorial). The script was adapted to:
- **Skip Commune Iteration**: It grabs the regional total immediately.
- **Scroll Fixes**: It uses JavaScript `scrollIntoView` to make sure elements are visible to the "GhostMouse" before clicking.
- **Data Post-Processing**: We added a step to clean the data (separating "Región de Coquimbo3" into Name: "Región de Coquimbo" + Escaños: 3).

## Improvements over Standard Methods
- **Undetectable**: Because the session is real and clicks are hardware-simulated.
- **Resilient**: If the DOM changes slightly, the physical click might still work if the general layout is preserved.
- **Visual Debugging**: You can verify what the scraper is doing in real-time because you are watching it happen on your screen.

# Hacking the Election: How we Built the "GhostMouse" Scraper for Chile's 2021 Diputados Results

**Target URL:** [Emol 2021 Resultados](https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp)

Scraping modern, dynamic websites is rarely a walk in the park. It often requires more than just fetching HTML; it requires simulating a real user to bypass complex navigation flows and anti-bot measures. This is the story of how we built **GhostMouse**, a hybrid remote-debugging scraper that successfully extracted granular 2021 Diputados election data for every region and district in Chile.

## The Challenge

The target website, Emol's breakdown of the 2021 elections, presented several unique hurdles:

1.  **Dynamic SPA Behavior:** The site is a Single Page Application (SPA). Clicking tabs or regions doesn't reload the page but dynamically updates the DOM.
2.  **Anti-Bot Triggers:** Standard Selenium/Playwright headless browsers are often blocked or redirected to generic "Access Denied" or news pages.
3.  **Hidden Navigation**: The "Distritos" list is technically present in the DOM for *all* regions at once but is hidden via CSS. Interacting with the wrong hidden element causes crashes.
4.  **Flat HTML Structure**: The candidate data wasn't nested hierarchy-wise (e.g., `Pact -> Candidate`). Instead, it was a flat list of `<h5>` headers (Pacts) followed by sibling `<li>` items (Candidates), making standard extraction logic fail.

## The Solution: GhostMouse Architecture

To overcome these, we moved away from standard headless browsing and built **GhostMouse**.

### 1. Hybrid Remote Debugging
Instead of spawning a fresh browser instance that screams "I am a robot," we launch a standard Google Chrome instance with standard flags enabling remote debugging port 9222.
```bash
/Applications/Google\ Chrome.app/... --remote-debugging-port=9222 --user-data-dir="/tmp/clean-profile"
```
Our Python script then connects to this *existing* browser session via Playwright. To the website, it looks exactly like a normal user is browsing.

### 2. "Ghost" Interactions
We bypassed standard Playwright clicks (which can sometimes be detected) by calculating the bounding box of elements and using `pyautogui` to physically move the mouse cursor and click at those screen coordinates. This adds human-like jitter and timing.

### 3. Surgical Selectors
During debugging, we discovered that the "DIPUTADOS" tab was not an `<a>` tag but a `<span>` inside a `<li>`. Similarly, region navigation required targeting specific `<li>` elements by their `data-region` attribute (e.g., `li[data-region='xv']`), as visual labels were sometimes misleading.

### 4. Sequential Sibling Extraction
To handle the flat HTML candidate list, we implemented a state-machine parser:
```python
current_pact = None
for child in children:
    if child.tagName == "H5":
         # New Pact discovered, switch context
         current_pact = create_new_pact(child.text)
    elif child.tagName == "LI":
         # Add candidate to the currently active pact
         current_pact.add_candidate(extract_info(child))
```
This allowed us to correctly group candidates under their respective political pacts despite the lack of nesting.

## The Result

The scraper now autonomously:
1.  **Navigates** to the Diputados tab without triggering redirects.
2.  **Iterates** through every Chilean region (XV, I, II... XII).
3.  **Clicks** exactly on every District in the sidebar.
4.  **Extracts** high-fidelity JSON data including:
    *   District metadata (Seat count, Communes)
    *   Full Candidate list with Party, Votes, Percentage, and "Elected" status.
    *   Identification of "Independent in Quota" candidates vs true independents.
    *   Comprehensive voting summary stats (Null, Blank, Valid votes).

We now have a complete, structured dataset of the 2021 Diputados election ready for database import and analysis.

Data saved to: `scrap_data_2021_diputados/`

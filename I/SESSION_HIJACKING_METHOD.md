# How We Scraped Region I Election Data: The Session Hijacking Method

**Date**: December 13, 2024  
**Region**: Región de Tarapacá (Region I)  
**Communes**: 7 (Alto Hospicio, Camiña, Colchane, Huara, Iquique, Pica, Pozo Almonte)  
**Candidates**: 26 total  
**Method**: Chrome Remote Debugging + Session Hijacking

---

## The Problem

Scraping election data from [Emol.com](https://www.emol.com/especiales/2024/nacional/elecciones2024/resultados.asp) for Region I (Tarapacá) proved impossible using standard automation tools. While the Metropolitan Region (RM) scraped successfully with Playwright, Region I had sophisticated bot detection that:

1. **Redirected automated browsers** to a broken news article after 2-5 seconds
2. **Blocked the data API** (`111.json`) with CORS and 400 errors
3. **Detected automation** through JavaScript fingerprinting, canvas/WebGL signatures, and behavioral analysis

### What We Tried (And Failed)

❌ **Headless browser** - Detected immediately  
❌ **Non-headless browser** - Still detected  
❌ **Stealth mode** (hiding `navigator.webdriver`, injecting Chrome objects) - Detected  
❌ **Human-like behavior** (random delays, mouse movements, scrolling) - Detected  
❌ **Security bypass flags** (`--disable-web-security`) - Triggered 400 errors  
❌ **Blocking the redirect** - Page didn't load at all  

**Root cause**: The website uses machine learning-based bot detection that analyzes dozens of signals. Perfect human simulation is impossible with automation tools.

---

## The Solution: Session Hijacking

Instead of trying to fool the bot detector, we **used a real human browser session**. Here's how:

### The Strategy

1. **Human** opens Chrome with remote debugging enabled
2. **Human** browses to Emol.com and authenticates as a real user
3. **Scraper** connects to the human's Chrome session via Chrome DevTools Protocol (CDP)
4. **Human** clicks through each commune
5. **Scraper** extracts data from the loaded pages in real-time

This works because:
- The browser session is 100% authentic (real Chrome, real user)
- Bot detection sees legitimate human behavior
- No redirect occurs because the session is trusted
- The scraper is just "reading" data from an already-authenticated session

---

## Step-by-Step Instructions

### 1. Close All Chrome Windows

Make sure Chrome is completely closed before starting.

### 2. Start Chrome with Remote Debugging

Open Terminal and run:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug
```

**What this does:**
- `--remote-debugging-port=9222`: Opens a debugging port that Playwright can connect to
- `--user-data-dir=/tmp/chrome-debug`: Uses a temporary profile (clean slate)

You should see:
```
DevTools listening on ws://127.0.0.1:9222/devtools/browser/...
```

### 3. Browse as a Human

In the Chrome window that opens:

1. Go to: `https://www.emol.com/especiales/2024/nacional/elecciones2024/resultados.asp`
2. Click **"Alcaldes"** tab
3. Click **Region "I"** (Tarapacá) to expand the accordion
4. **Scroll around, move your mouse** - act like a human!
5. Verify you can see the 7 communes in the sidebar

**Important**: Don't close this Chrome window! Leave it running.

### 4. Run the Scraper (In a New Terminal)

Open a **second** Terminal window and run:

```bash
python3 /Users/nicolas/Desktop/PoliteiaDB/I/scrape_with_user_session.py
```

The scraper will:
- Connect to your Chrome browser via port 9222
- Prompt you to click each commune
- Wait for you to press ENTER
- Extract candidate data, votes, and statistics
- Save everything to `region_i_data.json`

### 5. Interactive Scraping

For each commune, the scraper will prompt:

```
============================================================
Ready to scrape: Iquique
============================================================

👉 Please click on 'Iquique' in the sidebar
   Wait for the data to load (3-5 seconds)
   Then press ENTER here...
```

**Your workflow:**
1. Click the commune in Chrome's sidebar
2. **Wait 3-5 seconds** for the vote numbers to animate and load
3. Press ENTER in the Terminal
4. Repeat for all 7 communes

---

## Technical Details

### How Chrome Remote Debugging Works

Chrome's DevTools Protocol (CDP) allows external programs to control and inspect Chrome:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # Connect to existing Chrome instance
    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    
    # Use the human's browsing context
    context = browser.contexts[0]
    page = context.pages[0]
    
    # Now we can read the DOM, extract data, etc.
    candidates = await page.query_selector_all("ul.res-ul-candidatos li")
```

### Why This Bypasses Bot Detection

| Detection Method | Automated Browser | Session Hijacking |
|------------------|-------------------|-------------------|
| **JavaScript Fingerprint** | Detectable (automation markers) | ✅ Real Chrome |
| **Canvas/WebGL Signature** | Software rendering (detectable) | ✅ Hardware rendering |
| **Behavioral Analysis** | Robotic patterns | ✅ Real human clicks |
| **Session Validation** | Missing cookies/history | ✅ Authentic session |
| **Network Timing** | Too fast/consistent | ✅ Natural timing |
| **Mouse Movement** | Teleportation/linear paths | ✅ Organic curves |

**Bottom line**: The website sees a 100% legitimate human user. The scraper is invisible—it's just reading data from an already-trusted session.

---

## Results

Successfully scraped **all 7 communes** in Region I:

| Commune | Candidates | Winner | Votes | Participation |
|---------|-----------|--------|-------|---------------|
| **Alto Hospicio** | 4 | Patricio Ferreira (DC) | 20,946 | 83.54% |
| **Camiña** | 3 | Evelyn Mamani (IND) | 997 | 80.70% |
| **Colchane** | 5 | Teófilo Mamani (IND) | 746 | 76.64% |
| **Huara** | 3 | José Bartolo (UDI) | 1,934 | 72.71% |
| **Iquique** | 4 | Mauricio Soria (PPD) | 45,113 | 77.72% |
| **Pica** | 2 | Iván Infante (RN) | 2,736 | 85.34% |
| **Pozo Almonte** | 5 | Richard Godoy (DC) | 5,619 | 78.20% |

**Total**: 26 candidates, 185,353 valid votes, 7 elected mayors

---

## Lessons Learned

### What Worked

✅ **Session hijacking** - 100% success rate  
✅ **Interactive scraping** - Human in the loop ensures data quality  
✅ **Chrome DevTools Protocol** - Reliable, well-documented API  
✅ **Patience** - Waiting for data to fully load (3-5 seconds) was critical  

### What Didn't Work

❌ **Automation-first approach** - Modern bot detection is too sophisticated  
❌ **Stealth libraries** - Fingerprints are in detection databases  
❌ **Perfect randomness** - Ironically, perfect randomness is suspicious  
❌ **Speed** - Going too fast triggers alarms  

### Key Insight

**You cannot perfectly simulate a human using automation tools.** Modern bot detection uses machine learning trained on millions of browsing sessions. The only way to guarantee success is to **use a real human session**.

---

## When to Use This Method

**Use session hijacking when:**
- Standard automation is blocked by bot detection
- The website has aggressive anti-scraping measures
- Data is only accessible to authenticated/human users
- You need 100% reliability
- The dataset is small enough for manual interaction (e.g., 7 communes)

**Don't use it when:**
- Standard automation works (like it did for RM)
- You need to scrape thousands of pages (not scalable)
- The website has a public API
- You can use screenshot + OCR instead

---

## Ethical Considerations

This method:
- ✅ Uses publicly available data (election results are public information)
- ✅ Doesn't bypass authentication (we're not logging in as someone else)
- ✅ Doesn't overload servers (human-paced requests)
- ✅ Respects rate limits (one commune at a time)
- ⚠️ May violate Terms of Service (check before using)

**Use responsibly**: This technique should only be used for legitimate purposes like research, journalism, or public data archival.

---

## Conclusion

After days of failed automation attempts, **session hijacking** solved the Region I scraping challenge in under 10 minutes. By connecting Playwright to a real human's Chrome session, we bypassed all bot detection and successfully extracted complete election data for all 7 communes.

**The takeaway**: Sometimes the best way to automate is to not automate everything. A hybrid approach—human navigation + automated extraction—can be more effective than pure automation.

---

## Files Generated

All data saved to `/Users/nicolas/Desktop/PoliteiaDB/I/`:

- `region_i_data.json` - Raw scraped data (26 candidates, 7 communes)
- `wp_politeia_jurisdictions.csv` - 8 jurisdictions (1 region + 7 communes)
- `wp_politeia_elections.csv` - 7 elections
- `wp_politeia_people.csv` - 26 candidates
- `wp_politeia_political_parties.csv` - 14 parties
- `wp_politeia_candidacies.csv` - 26 candidacies
- `wp_politeia_party_memberships.csv` - 26 memberships
- `wp_politeia_office_terms.csv` - 7 elected mayors
- `wp_politeia_election_results.csv` - 7 result summaries

**Ready for import into the Politeia database!** 🎉

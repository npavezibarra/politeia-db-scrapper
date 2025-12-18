# Running the 2021 Diputados Scraper

## Prerequisites

1. **Accessibility Permissions**: Ensure Terminal/VS Code has accessibility permissions
   - See [setup_ghostmouse.md](file:///Users/nicolasibarra/Desktop/Antigravity/politeia-db-scrapper/GhostMouse/setup_ghostmouse.md) for instructions

2. **Chrome with Remote Debugging**: Start Chrome in debug mode
   ```bash
   cd /Users/nicolasibarra/Desktop/Antigravity/politeia-db-scrapper/GhostMouse
   ./start_chrome_debug.sh
   ```

3. **Navigate to Emol**: In the Chrome window that opens, go to:
   ```
   https://www.emol.com/especiales/2021/nacional/carrera-presidencial/resultados.asp
   ```

## Running the Scraper

```bash
cd /Users/nicolasibarra/Desktop/Antigravity/politeia-db-scrapper/GhostMouse
python3 scraper_2021_diputados.py
```

## What to Expect

1. **Initial Setup** (~5 seconds)
   - Scraper connects to Chrome via CDP
   - Clicks DIPUTADOS tab
   - Waits for page to load

2. **Region Processing** (~15-20 minutes total)
   - For each of 17 regions (XV, I, II, ..., EXT):
     - Clicks region button
     - Waits for distritos to load
     - For each distrito in the region:
       - Clicks distrito
       - Waits for candidate data
       - Extracts all pacts and candidates
       - Extracts voting statistics
   - Saves JSON file for each region

3. **Output Location**
   ```
   GhostMouse/scrap_data_2021_diputados/
   ├── XV/region_xv_diputados.json
   ├── I/region_i_diputados.json
   ├── II/region_ii_diputados.json
   ...
   └── EXT/region_ext_diputados.json
   ```

## Important Notes

⚠️ **DO NOT TOUCH** the mouse or keyboard while the scraper is running!

⚠️ **Failsafe**: If you need to abort, slam the mouse to any screen corner

⚠️ **Estimated Runtime**: 15-20 minutes for all 17 regions

## Troubleshooting

### "Could not find tab DIPUTADOS"
- Make sure you're on the Emol results page
- The page might have different tab names - check the HTML

### "Failed to click Region"
- Region might already be selected
- Try clicking manually to verify the selector works

### "No data collected"
- Increase wait times in the script (change `asyncio.sleep(4)` to `asyncio.sleep(6)`)
- Check if the page structure has changed

### Mouse clicks miss the target
- Adjust `TOOLBAR_HEIGHT_ESTIMATE` constant in the script
- Verify Chrome window is on primary display
- Ensure window is not maximized (use normal size)

## Verifying Output

After completion, check:
1. **File count**: Should have 17 JSON files (one per region)
2. **File sizes**: Each should be > 10KB (not empty)
3. **JSON validity**: Open a file and verify structure
4. **Data accuracy**: Compare a sample distrito against the website

Example verification:
```bash
# Count files
ls -1 scrap_data_2021_diputados/*/region_*.json | wc -l

# Check file sizes
du -h scrap_data_2021_diputados/*/region_*.json

# Validate JSON
python3 -m json.tool scrap_data_2021_diputados/RM/region_rm_diputados.json > /dev/null && echo "Valid JSON"
```

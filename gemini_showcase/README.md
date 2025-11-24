# Gemini Showcase

A curated showcase of experimental projects built with Google Gemini AI.

## Structure

- `index.html` - Main showcase page with card-style layout
- `projects.json` - Project metadata (title, description, path, tags)
- `images/` - Thumbnail images for projects
- `generate_thumbnails_20251124.py` - Automated thumbnail generator

## Adding New Projects

### Method 1: Manual (Quick)

1. Open `projects.json`
2. Add a new entry:
```json
{
    "title": "My Project",
    "description": "Short description here.",
    "path": "../path/to/project.html",
    "tag": "Category",
    "icon": "cube"
}
```

Available icons: `cube`, `chart`, `magic`, `gear`

For external links (e.g., Gemini shares), use full URLs:
```json
{
    "title": "Gemini Chat",
    "description": "A shared conversation.",
    "path": "https://gemini.google.com/share/xxxxx",
    "tag": "AI",
    "image": "images/my_screenshot.png",
    "icon": "magic"
}
```

### Method 2: Automated Thumbnails (Recommended)

Use Playwright to automatically generate thumbnails:

#### Setup (First Time Only)
```bash
# Activate shared venv
source ~/.python-venvs/pdms-shared/bin/activate

# Install Playwright (if not already installed)
pip install playwright
playwright install chromium
```

**Note:** The script uses the shared venv at `~/.python-venvs/pdms-shared`

#### Generate Thumbnails
```bash
# Method 1: Run directly (uses shared venv)
./generate_thumbnails_20251124.py --test    # Dry-run
./generate_thumbnails_20251124.py           # Generate

# Method 2: Activate venv first
source ~/.python-venvs/pdms-shared/bin/activate
python generate_thumbnails_20251124.py --test
python generate_thumbnails_20251124.py
```

This will:
1. Start a local server
2. Navigate to each project URL
3. Capture a screenshot
4. Save to `images/` folder
5. Update `projects.json` with image paths

#### Options
```bash
--test          # Dry-run mode
--width 1200    # Viewport width (default: 1200)
--height 800    # Viewport height (default: 800)
--port 8000     # Local server port (default: 8000)
```

## Viewing Locally

### Quick Preview (No Server Required!)

The page works by double-clicking `index.html` thanks to `projects.js`:

1. Edit `projects.json` as needed
2. Run: `./sync_projects_20251124.py` (syncs JSON → JS)
3. Double-click `index.html` to open in browser

### With a Web Server

If you prefer using a server:

**Option 1: Python**
```bash
python3 -m http.server 8000
# Visit http://localhost:8000/gemini_showcase/
```

**Option 2: GitHub Pages** (always works)
```
https://sugarsmax.github.io/Pete_Sandbox_personal/gemini_showcase/
```

**How it works:** The page checks for `PROJECTS_DATA` from `projects.js` first (works with `file://`), then falls back to fetching `projects.json` (requires server).

## Design

The design uses a **Supergraphics** style inspired by 1970s BMW M1 Procar livery:
- Color palette: Light Blue (#4EBAF0), Dark Blue (#2B1E79), Red (#D12531)
- Bold diagonal stripes
- Swiss typography (Helvetica Neue)
- Hard-edge hover effects

## Technologies

- Pure HTML/CSS/JavaScript (no frameworks)
- Playwright for automated screenshots
- JSON for data management


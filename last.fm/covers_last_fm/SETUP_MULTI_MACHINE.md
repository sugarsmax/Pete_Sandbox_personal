# Multi-Machine Setup Guide

> This page was built by an AI assistant (Claude Opus 4.5)

This project supports running on multiple computers with different Python environments. The setup automatically detects and uses the appropriate venv based on your machine.

## Quick Start

### First Time Setup

#### On This Computer (with ~/python/venv)

```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
```

This will auto-detect and use `~/python/venv` if it exists, otherwise create one.

#### On Other Computers (with shared team venv)

```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
```

This will auto-detect `/Users/maxfiep/.python-venvs/pdms-shared` if it exists.

#### On Windows

```batch
cd last.fm\covers_last_fm
scripts\activate_venv.bat
```

## Venv Priority Order

The activation scripts check in this order:

1. **Environment Variable**: `COVERS_VENV` (highest priority)
   ```bash
   export COVERS_VENV=/custom/path/to/venv
   source scripts/activate_venv.sh
   ```

2. **Local Machine Override** (macOS/Linux): `~/python/venv`
   - Create once: `python3 -m venv ~/python/venv`
   - Auto-detected and used on subsequent runs

3. **Shared Team Venv**: `/Users/maxfiep/.python-venvs/pdms-shared`
   - For team members with the shared venv installed

4. **Project Local Venv** (fallback): `.venv/`
   - Auto-created on first run if no other venv is found

## Setup Scenarios

### Scenario 1: Local Python on This Computer

**One-time setup:**
```bash
python3 -m venv ~/python/venv
source ~/python/venv/bin/activate
pip install requests beautifulsoup4 pyyaml playwright
playwright install chromium
```

**Every run:**
```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
python scripts/whosampled_scraper_20251209.py
```

### Scenario 2: Shared Team Venv on Other Computers

No setup needed if `/Users/maxfiep/.python-venvs/pdms-shared` exists.

**Every run:**
```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
python scripts/whosampled_scraper_20251209.py
```

### Scenario 3: Custom Venv Location

**Setup with environment variable:**
```bash
export COVERS_VENV=/my/custom/venv/path
source scripts/activate_venv.sh
```

Or add to `~/.zshrc` / `~/.bashrc`:
```bash
export COVERS_VENV=/my/custom/venv/path
```

### Scenario 4: Windows with Local Python

**One-time setup:**
```batch
python -m venv %USERPROFILE%\python\venv
%USERPROFILE%\python\venv\Scripts\activate.bat
pip install requests beautifulsoup4 pyyaml playwright
python -m playwright install chromium
```

**Every run:**
```batch
cd last.fm\covers_last_fm
scripts\activate_venv.bat
python scripts\whosampled_scraper_20251209.py
```

## Customizing Paths for Different Machines

If your Last.fm data is in different locations on different machines, set environment variables:

```bash
# In ~/.zshrc or ~/.bashrc
export MUSIC_DATA=/path/to/music/data
```

Then update `config.yaml`:
```yaml
source:
  top_tracks_path: "$MUSIC_DATA/top_tracks.json"
```

## Troubleshooting

### "Command not found: python3"
- Install Python 3: https://www.python.org/downloads/
- Or use `python` instead of `python3`

### "ModuleNotFoundError: No module named 'playwright'"
- Re-run: `source scripts/activate_venv.sh`
- Or manually: `pip install playwright && playwright install chromium`

### "No Python virtual environment found"
- You're being prompted - choose option 1-3 or set `COVERS_VENV`

### Playwright timeouts on scraping
- Increase `scraping.timeout` in `config.yaml`
- Default is 30 seconds; try 60 for slower connections

---

*Generated with Claude Opus 4.5*


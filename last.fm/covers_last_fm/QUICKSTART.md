# Quick Start Guide

> This page was built by an AI assistant (Claude Opus 4.5)

## One-Time Setup

### This Computer (macOS/Linux)
```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
# Choose option 1 to create ~/python/venv, then wait for setup
```

### This Computer (Windows)
```batch
cd last.fm\covers_last_fm
scripts\activate_venv.bat
REM Choose option 1 to create %USERPROFILE%\python\venv, then wait for setup
```

### Other Computers
```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
# Will auto-use /Users/maxfiep/.python-venvs/pdms-shared if available
```

## Every Run

### macOS/Linux
```bash
cd last.fm/covers_last_fm
source scripts/activate_venv.sh
python scripts/whosampled_scraper_20251209.py [options]
```

### Windows
```batch
cd last.fm\covers_last_fm
scripts\activate_venv.bat
python scripts\whosampled_scraper_20251209.py [options]
```

## Common Commands

```bash
# Dry run - test without scraping
python scripts/whosampled_scraper_20251209.py --dry-run --limit 5

# Search first 50 songs
python scripts/whosampled_scraper_20251209.py --limit 50

# Search all (resumes from cache)
python scripts/whosampled_scraper_20251209.py

# Re-fetch everything
python scripts/whosampled_scraper_20251209.py --force

# Search specific artist
python scripts/whosampled_scraper_20251209.py --artist "Queens of the Stone Age"

# Show detailed output
python scripts/whosampled_scraper_20251209.py --verbose
```

## Output Files

After running, check:
- `data/covers_master_YYYYMMDD.csv` - All covers (spreadsheet)
- `data/covers_by_song_YYYYMMDD.json` - Covers by song (structured)
- `output/covers_report_YYYYMMDD.md` - HTML-ready report

## Customizing for Your Machine

Edit `config.yaml` to:
- Change minimum scrobbles threshold
- Filter by artist or genre
- Adjust request delay (slower = more respectful to WhoSampled)
- Adjust timeout for slow connections

## Help

- Full setup guide: `SETUP_MULTI_MACHINE.md`
- What changed: `ENHANCEMENTS.md`
- Main README: `README.md`

---

*Generated with Claude Opus 4.5*


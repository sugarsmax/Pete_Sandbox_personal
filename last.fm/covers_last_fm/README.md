# WhoSampled Covers Finder

> This page was built by an AI assistant (Claude Opus 4.5)

Discover covers of your favorite songs by scraping WhoSampled.com.

## Overview

This tool takes your Last.fm top tracks and searches WhoSampled.com to find cover versions of each song. Results are cached to allow resuming interrupted runs.

## Directory Structure

```
covers_last_fm/
├── cache/
│   └── search_log.json      # Tracks what's been searched (enables resume)
├── data/
│   ├── covers_master_*.csv  # All covers (flat format)
│   └── covers_by_song_*.json # Covers grouped by original song
├── output/
│   └── covers_report_*.md   # Human-readable report
├── scripts/
│   └── whosampled_scraper_20251209.py
├── config.yaml
└── README.md
```

## Setup

### Quick Start

**macOS/Linux:**
```bash
source scripts/activate_venv.sh
```

**Windows:**
```batch
scripts\activate_venv.bat
```

The activation scripts automatically detect and use the appropriate Python environment:
- `~/python/venv` (local on this machine)
- `/Users/maxfiep/.python-venvs/pdms-shared` (shared team venv on other machines)
- `COVERS_VENV` environment variable (custom location)
- `.venv/` in project (auto-created if none exist)

### Multi-Machine Setup

For detailed setup instructions for different machines and configurations, see **[SETUP_MULTI_MACHINE.md](SETUP_MULTI_MACHINE.md)**.

### Configuration

Edit `config.yaml` to adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `filters.min_scrobbles` | 10 | Minimum plays to include a song |
| `filters.excluded_genres` | classical, easy listening | Skip these artists |
| `filters.excluded_cover_genres` | classical, easy listening | Filter out these cover genres |
| `scraping.request_delay` | 2.5 | Seconds between requests |

## Usage

### Basic Commands

```bash
# Dry run - see what would be fetched without making requests
python scripts/whosampled_scraper_20251209.py --dry-run --limit 10

# Process first 50 songs
python scripts/whosampled_scraper_20251209.py --limit 50

# Process all songs (uses cached results, only fetches new)
python scripts/whosampled_scraper_20251209.py

# Force re-fetch everything (ignore cache)
python scripts/whosampled_scraper_20251209.py --force

# Filter to specific artist
python scripts/whosampled_scraper_20251209.py --artist "Queens of the Stone Age"

# Override minimum scrobbles
python scripts/whosampled_scraper_20251209.py --min-scrobbles 50
```

### Options

| Flag | Description |
|------|-------------|
| `--dry-run` / `--test` | Print URLs without fetching |
| `--limit N` | Process only first N songs |
| `--force` | Re-fetch even if cached |
| `--min-scrobbles N` | Override min scrobbles threshold |
| `--artist "X"` | Filter to specific artist (partial match) |
| `--verbose` / `-v` | Show detailed progress |

## Output Files

### covers_master_YYYYMMDD.csv

Flat CSV with all covers found:

```
original_rank,original_artist,original_track,original_scrobbles,cover_artist,cover_track,cover_year,cover_genre,whosampled_url,fetched_at
```

### covers_by_song_YYYYMMDD.json

JSON grouped by original song:

```json
{
  "queens_of_the_stone_age__no_one_knows": {
    "original_artist": "Queens of the Stone Age",
    "original_track": "No One Knows",
    "covers": [
      {"cover_artist": "Mark Ronson", "cover_year": "2007", ...}
    ]
  }
}
```

### covers_report_YYYYMMDD.md

Human-readable markdown report sorted by most covers.

## Caching / Resume

The script saves progress to `cache/search_log.json` after each request. If interrupted:

1. Re-run the same command
2. Already-searched songs are skipped
3. Only new songs are fetched

To start fresh, delete `cache/search_log.json`.

## Rate Limiting

Default: 2.5 seconds between requests. This is intentionally slow to be respectful to WhoSampled.com. Adjust `scraping.request_delay` in config.yaml if needed.

## Estimated Runtime

| Songs | Time (@ 2.5s/request) |
|-------|----------------------|
| 10 | ~25 seconds |
| 100 | ~4 minutes |
| 500 | ~21 minutes |

---

*Built for the Last.fm analysis project*



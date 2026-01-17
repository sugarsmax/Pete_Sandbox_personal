# Recent Listen Cleanup

> **Note**: This page was built by an AI assistant (Claude Opus 4.5).

Tools to identify and manage artists with low scrobble counts in your Last.fm library.

## Purpose

Collect artists you've only listened to 1-2 times in the last 90 days for review/cleanup. Useful for:
- Identifying one-off listens vs. regular rotation
- Cleaning up library recommendations
- Tracking listening breadth over time

## Scripts

### collect_low_scrobble_artists_YYYYMMDD.py

Fetches artists with low scrobble counts from the Last.fm API.

**Usage:**

```bash
# Dry-run (no API calls, sample data)
python collect_low_scrobble_artists_20260116.py --dry-run

# Live run (default: artists with 1-2 scrobbles)
python collect_low_scrobble_artists_20260116.py

# Custom max scrobbles
python collect_low_scrobble_artists_20260116.py --max-scrobbles 3

# Different user
python collect_low_scrobble_artists_20260116.py --username otheruser
```

**Options:**
| Flag | Description | Default |
|------|-------------|---------|
| `--dry-run, -n` | Test mode with sample data | False |
| `--username, -u` | Last.fm username | sugarsmax |
| `--max-scrobbles, -m` | Max scrobbles to include | 2 |
| `--output, -o` | Output filename | low_scrobble_artists_YYYYMMDD.csv |

**Output:**
- CSV file in `data/` folder with columns: `artist`, `scrobbles`, `library_url`
- Library URLs link directly to the artist's page in your Last.fm library

## Credentials

Uses shared Last.fm API credentials from `../Lyrics_top_songs/.env`:
- `LASTFM_API_KEY`
- `LASTFM_API_SECRET`

## Monthly Updates

Run this script monthly to track changes in listening habits:

```bash
# Creates dated output file automatically
python collect_low_scrobble_artists_20260116.py
# Output: data/low_scrobble_artists_20260116.csv
```

Compare files month-over-month to see which artists you've started listening to more frequently.

---
*Model: Claude Opus 4.5*

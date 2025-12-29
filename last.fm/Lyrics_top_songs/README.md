# Lyrics Top Songs Theme Analysis

> This project was built by Claude Opus 4.5

Analyze your most-played Last.fm tracks by lyrical themes using BERTopic clustering.

## Quick Start

```bash
# 1. Activate shared venv
source /Users/maxfiep/.python-venvs/pdms-shared/bin/activate

# 2. Run pipeline in test mode
python scripts/fetch_top_tracks_20251206.py --test
python scripts/fetch_lyrics_20251206.py --test
python scripts/compile_lyrics_20251206.py --test
python scripts/analyze_themes_20251206.py --test
```

## Pipeline Steps

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `fetch_top_tracks` | Get your top N tracks from Last.fm |
| 2 | `fetch_lyrics` | Fetch lyrics from Musixmatch (or other provider) |
| 3 | `compile_lyrics` | Merge tracks + lyrics into Parquet |
| 4 | `analyze_themes` | Run BERTopic clustering, output markdown |

## Configuration

Edit `config.yaml` to adjust:

- `lastfm.username` - Your Last.fm username
- `lastfm.top_tracks_limit` - How many tracks (default: 10)
- `lyrics.provider` - Lyrics source: `musixmatch`, `genius`, `azlyrics`
- `analysis.nr_topics` - Number of themes (`auto` or integer)

## Switching Lyrics Providers

```yaml
# In config.yaml
lyrics:
  provider: "genius"  # Change from musixmatch
  genius:
    api_key: "YOUR_API_KEY"
```

## Common Commands

```bash
# View cached tracks
python scripts/fetch_top_tracks_20251206.py --show-cache

# Check lyrics cache status
python scripts/fetch_lyrics_20251206.py --status

# Force refresh all lyrics
python scripts/fetch_lyrics_20251206.py --force

# Dry run (preview without changes)
python scripts/analyze_themes_20251206.py --dry-run
```

## Output Files

```
cache/
  top_tracks.json       # Cached track list
  lyrics/               # Individual lyrics files
  fetch_log.json        # Fetch history

data/
  compiled_lyrics_*.parquet   # Analysis-ready data
  theme_assignments_*.csv     # Song-to-theme mapping

output/
  theme_analysis_*.md   # Final markdown summary
```

## Dependencies

```bash
pip install pyyaml pandas pyarrow bertopic sentence-transformers
```

---

*Model: Claude Opus 4.5*


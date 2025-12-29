#!/usr/bin/env python3
"""
Compile Lyrics into Analysis-Ready Format

Merges track metadata with cached lyrics into a Parquet file
for efficient analysis.

Created: 2025-12-06
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

CONFIG_PATH = PROJECT_DIR / "config.yaml"
CACHE_DIR = PROJECT_DIR / "cache"
LYRICS_CACHE_DIR = CACHE_DIR / "lyrics"
TRACKS_CACHE_PATH = CACHE_DIR / "top_tracks.json"
DATA_DIR = PROJECT_DIR / "data"


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def slugify(text: str) -> str:
    """Convert text to safe filename slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text)
    return text[:50]


def normalize_special_chars(text: str) -> str:
    """Normalize non-English special characters to ASCII equivalents."""
    import unicodedata
    normalized = unicodedata.normalize('NFD', text)
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_text


def slugify_artist(artist: str) -> str:
    """
    Convert artist name to folder slug, moving articles to end.
    
    - Moves 'The', 'A', 'An' from start to end
    - Normalizes special characters (ö->o, é->e, etc.)
    """
    import re
    artist = normalize_special_chars(artist)
    artist_lower = artist.lower().strip()
    
    if artist_lower.startswith("the "):
        artist = artist[4:].strip() + ", The"
    elif artist_lower.startswith("an "):
        artist = artist[3:].strip() + ", An"
    elif artist_lower.startswith("a "):
        artist = artist[2:].strip() + ", A"
    
    slug = slugify(artist)
    slug = re.sub(r"__+", "_", slug)
    if slug.endswith("_"):
        slug = slug[:-1]
    return slug


def get_lyrics_cache_path(artist: str, track: str) -> Path:
    """Get cache file path for a track's lyrics (artist subfolder structure)."""
    artist_slug = slugify_artist(artist)  # Moves "The" to end
    track_slug = slugify(track)
    return LYRICS_CACHE_DIR / artist_slug / f"{track_slug}.txt"


def load_tracks() -> list:
    """Load tracks from cache."""
    if not TRACKS_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"No tracks cache found at {TRACKS_CACHE_PATH}. "
            "Run fetch_top_tracks first."
        )
    
    with open(TRACKS_CACHE_PATH, "r") as f:
        data = json.load(f)
    
    return data["tracks"], data.get("fetched_at", "unknown")


def load_lyrics(artist: str, track: str) -> str | None:
    """Load lyrics from cache if available."""
    cache_path = get_lyrics_cache_path(artist, track)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    return None


def compile_data(tracks: list, tracks_fetched_at: str) -> pd.DataFrame:
    """Compile tracks and lyrics into a DataFrame."""
    rows = []
    
    for track in tracks:
        artist = track["artist"]
        track_name = track["track"]
        
        lyrics = load_lyrics(artist, track_name)
        lyrics_path = get_lyrics_cache_path(artist, track_name)
        
        row = {
            "rank": track["rank"],
            "artist": artist,
            "track": track_name,
            "scrobbles": track["scrobbles"],
            "lyrics": lyrics,
            "has_lyrics": lyrics is not None,
            "lyrics_length": len(lyrics) if lyrics else 0,
            "lyrics_word_count": len(lyrics.split()) if lyrics else 0,
            "lyrics_cache_path": str(lyrics_path) if lyrics_path.exists() else None,
            "tracks_fetched_at": tracks_fetched_at,
            "compiled_at": datetime.now().isoformat()
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Compile tracks and lyrics into analysis-ready format"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run in test mode (show preview, don't save)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be compiled without saving"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Custom output filename (without extension)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["parquet", "csv", "both"],
        default="parquet",
        help="Output format (default: parquet)"
    )
    
    args = parser.parse_args()
    
    # Load tracks
    try:
        tracks, tracks_fetched_at = load_tracks()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    print(f"Compiling {len(tracks)} tracks...")
    
    # Compile data
    df = compile_data(tracks, tracks_fetched_at)
    
    # Summary
    with_lyrics = df["has_lyrics"].sum()
    without_lyrics = len(df) - with_lyrics
    total_words = df["lyrics_word_count"].sum()
    
    print(f"\nCompilation summary:")
    print(f"  Total tracks: {len(df)}")
    print(f"  With lyrics: {with_lyrics}")
    print(f"  Without lyrics: {without_lyrics}")
    print(f"  Total lyrics words: {total_words:,}")
    
    if args.test or args.dry_run:
        print(f"\nPreview (first 5 rows):")
        preview_cols = ["rank", "artist", "track", "scrobbles", "has_lyrics", "lyrics_word_count"]
        print(df[preview_cols].head().to_string(index=False))
        
        if not args.test:
            print("\n[DRY RUN] Would save compiled data")
        return 0
    
    # Save output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    base_name = args.output or f"compiled_lyrics_{date_str}"
    
    if args.format in ["parquet", "both"]:
        parquet_path = DATA_DIR / f"{base_name}.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"\nSaved: {parquet_path}")
    
    if args.format in ["csv", "both"]:
        csv_path = DATA_DIR / f"{base_name}.csv"
        # For CSV, truncate lyrics to avoid huge files
        df_csv = df.copy()
        df_csv["lyrics"] = df_csv["lyrics"].apply(
            lambda x: x[:500] + "..." if x and len(x) > 500 else x
        )
        df_csv.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


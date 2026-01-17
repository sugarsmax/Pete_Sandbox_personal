#!/usr/bin/env python3
"""
Collect Long Artist Names from Last.fm

Fetches artists with names longer than 50 characters from the last 365 days.
Useful for identifying verbose artist names that may need cleanup.

Supports:
- --dry-run mode for testing without API calls
- Configurable minimum length threshold

Created: 2026-01-16
"""

import argparse
import csv
import json
import os
import sys
import unicodedata
import urllib.parse
from datetime import datetime
from pathlib import Path

import pylast
from dotenv import load_dotenv

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent  # last.fm folder
ENV_PATH = PROJECT_DIR / "Lyrics_top_songs" / ".env"  # Shared credentials

# Output paths
DATA_DIR = SCRIPT_DIR / "data"

# Load environment variables
load_dotenv(ENV_PATH)


# Classical composers and performers to detect (case-insensitive matching)
CLASSICAL_INDICATORS = [
    # Major composers
    "bach", "mozart", "beethoven", "chopin", "brahms", "handel", "händel", "haydn",
    "schubert", "tchaikovsky", "vivaldi", "debussy", "liszt", "mendelssohn",
    "rachmaninoff", "rachmaninov", "ravel", "schumann", "strauss", "wagner", 
    "dvorak", "dvořák", "mahler", "verdi", "puccini", "stravinsky", "prokofiev", 
    "shostakovich", "grieg", "sibelius", "elgar", "holst", "bernstein", "copland", 
    "barber", "satie", "fauré", "faure", "saint-saëns", "saint-saens",
    "rimsky-korsakov", "mussorgsky", "borodin", "paganini", "telemann",
    # Baroque/early music
    "corelli", "scarlatti", "monteverdi", "purcell", "couperin", "rameau",
    "albinoni", "boccherini", "pergolesi", "lully",
    # Classical orchestras/ensembles (common patterns)
    "philharmonic", "symphony", "orchestra", "chamber", "quartet", "quintet",
    "ensemble", "soloists", "academy of", "conservatory",
    # Classical performers
    "horowitz", "rubinstein", "heifetz", "perlman", "yo-yo ma", "yunchan",
    "lang lang", "argerich", "brendel", "pollini", "ashkenazy", "richter",
    "gould", "grumiaux", "oistrakh", "rostropovich", "karajan", "solti",
    "barenboim", "rattle", "dudamel", "muti", "abbado", "haitink",
    # Catalog numbers (BWV, Op., K., etc.)
    "bwv", "opus", " op.", " op ", "k.", "köchel", "kochel",
]


def is_classical(artist_name: str) -> bool:
    """Check if an artist name indicates classical music."""
    normalized = unicodedata.normalize('NFD', artist_name.lower())
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    for indicator in CLASSICAL_INDICATORS:
        indicator_norm = unicodedata.normalize('NFD', indicator.lower())
        indicator_ascii = ''.join(c for c in indicator_norm if unicodedata.category(c) != 'Mn')
        if indicator_ascii in ascii_text:
            return True
    return False


def get_lastfm_network() -> pylast.LastFMNetwork:
    """Initialize Last.fm API connection using environment variables."""
    api_key = os.getenv("LASTFM_API_KEY")
    api_secret = os.getenv("LASTFM_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Missing Last.fm API credentials. "
            f"Expected in: {ENV_PATH}"
        )
    
    return pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)


def build_library_url(username: str, artist_name: str) -> str:
    """Build the Last.fm library URL for an artist."""
    encoded_artist = urllib.parse.quote(artist_name, safe='')
    return f"https://www.last.fm/user/{username}/library/music/{encoded_artist}"


# Articles to move to end of name
ARTICLES = ["The", "A", "An"]


def move_article_to_end(name: str) -> str:
    """Move leading articles (The, A, An) to the end of the name."""
    for article in ARTICLES:
        prefix = f"{article} "
        if name.startswith(prefix):
            remainder = name[len(prefix):]
            return f"{remainder}, {article}"
    return name


def fetch_long_name_artists(
    username: str,
    min_length: int = 50,
    dry_run: bool = False
) -> list[dict]:
    """
    Fetch artists with long names from the last 365 days.
    
    Args:
        username: Last.fm username
        min_length: Minimum character length to include (default: 50)
        dry_run: If True, return sample data without API calls
    
    Returns:
        List of dicts with artist info and library URLs
    """
    if dry_run:
        print(f"[DRY-RUN] Would fetch artists for user: {username}")
        print(f"[DRY-RUN] Period: Last 365 days (PERIOD_12MONTHS)")
        print(f"[DRY-RUN] Filter: name_length > {min_length}")
        
        # Sample test data with long names
        sample_artists = [
            {"artist": "Academy of St Martin in the Fields, Sir Neville Marriner, Kenneth Sillito", "scrobbles": 5},
            {"artist": "Amsterdam Bach Soloists, Henk Rubingh, Gewandhausorchester Leipzig, Kurt Masur", "scrobbles": 3},
            {"artist": "The Andrews Sisters, Vic Schoen & His Orchestra", "scrobbles": 2},
            {"artist": "András Schiff, Orchestra Of The Age Of Enlightenment", "scrobbles": 1},
            {"artist": "Short Name", "scrobbles": 10},  # Should be filtered out
        ]
        
        results = []
        for item in sample_artists:
            artist_name = item["artist"]
            if len(artist_name) > min_length:
                results.append({
                    "artist": artist_name,
                    "artist_sort": move_article_to_end(artist_name),
                    "name_length": len(artist_name),
                    "classical": 1 if is_classical(artist_name) else "",
                    "scrobbles": item["scrobbles"],
                    "library_url": build_library_url(username, artist_name)
                })
        
        print(f"[DRY-RUN] Would return {len(results)} sample artists")
        return results
    
    # Production mode: Use Last.fm API
    print(f"Fetching artists for user: {username}")
    print(f"Period: Last 365 days (PERIOD_12MONTHS)")
    print(f"Filter: name_length > {min_length}")
    
    try:
        network = get_lastfm_network()
        user = network.get_user(username)
        
        # Fetch all artists from the last 12 months
        print("Fetching artist data from Last.fm API...")
        top_artists = user.get_top_artists(period=pylast.PERIOD_12MONTHS, limit=1000)
        
        results = []
        total_fetched = 0
        
        for item in top_artists:
            total_fetched += 1
            artist_name = str(item.item)
            play_count = int(item.weight)
            
            # Only include artists with long names
            if len(artist_name) > min_length:
                results.append({
                    "artist": artist_name,
                    "artist_sort": move_article_to_end(artist_name),
                    "name_length": len(artist_name),
                    "classical": 1 if is_classical(artist_name) else "",
                    "scrobbles": play_count,
                    "library_url": build_library_url(username, artist_name)
                })
        
        print(f"Fetched {total_fetched} total artists from API")
        print(f"Found {len(results)} artists with name length > {min_length}")
        
        # Sort by name length descending, then alphabetically
        results.sort(key=lambda x: (-x["name_length"], x["artist_sort"].lower()))
        
        return results
        
    except pylast.WSError as e:
        print(f"Last.fm API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching artists: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_to_csv(artists: list[dict], output_path: Path) -> None:
    """Save artist data to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ["artist", "artist_sort", "name_length", "classical", "scrobbles", "library_url"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(artists)
    
    print(f"Saved {len(artists)} artists to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect artists with long names (>50 chars) from Last.fm"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Run in test mode with sample data (no API calls)"
    )
    parser.add_argument(
        "--username", "-u",
        default="sugarsmax",
        help="Last.fm username (default: sugarsmax)"
    )
    parser.add_argument(
        "--min-length", "-l",
        type=int,
        default=50,
        help="Minimum name length to include (default: 50)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output CSV filename (default: long_artist_names_YYYYMMDD.csv)"
    )
    
    args = parser.parse_args()
    
    # Generate default output filename with date
    if args.output:
        output_filename = args.output
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"long_artist_names_{date_str}.csv"
    
    output_path = DATA_DIR / output_filename
    
    print("=" * 60)
    print("Long Artist Name Collector")
    print("=" * 60)
    print(f"Username: {args.username}")
    print(f"Min name length: {args.min_length}")
    print(f"Output: {output_path}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()
    
    # Fetch artists
    artists = fetch_long_name_artists(
        username=args.username,
        min_length=args.min_length,
        dry_run=args.dry_run
    )
    
    if not artists:
        print("\nNo artists found matching criteria.")
        return
    
    # Display preview
    classical_count = sum(1 for a in artists if a["classical"] == 1)
    print(f"\nPreview (first 10 of {len(artists)}, {classical_count} classical):")
    print("-" * 80)
    print(f"  {'Len':>3} | {'Scr':>4} | {'Cls':>3} | Artist")
    print("-" * 80)
    for artist in artists[:10]:
        cls_mark = "  *" if artist["classical"] == 1 else ""
        # Truncate long names for display
        display_name = artist["artist"][:55] + "..." if len(artist["artist"]) > 58 else artist["artist"]
        print(f"  {artist['name_length']:3} | {artist['scrobbles']:4} | {cls_mark:>3} | {display_name}")
    if len(artists) > 10:
        print(f"  ... and {len(artists) - 10} more")
    print("-" * 80)
    
    # Save to CSV
    if not args.dry_run:
        save_to_csv(artists, output_path)
    else:
        print(f"\n[DRY-RUN] Would save {len(artists)} artists to: {output_path}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

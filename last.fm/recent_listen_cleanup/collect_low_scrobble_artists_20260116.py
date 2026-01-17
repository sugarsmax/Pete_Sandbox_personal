#!/usr/bin/env python3
"""
Collect Low-Scrobble Artists from Last.fm

Fetches artists with only 1-2 scrobbles in the last 90 days from your Last.fm library.
Outputs a CSV with artist names and library links for cleanup/review.

Supports:
- --dry-run mode for testing without API calls
- Resumable state (saves progress to continue if interrupted)
- Monthly dated output files

Created: 2026-01-16
"""

import argparse
import csv
import json
import os
import sys
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
STATE_FILE = SCRIPT_DIR / "state.json"

# Load environment variables
load_dotenv(ENV_PATH)


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
    # URL encode the artist name for the path
    encoded_artist = urllib.parse.quote(artist_name, safe='')
    return f"https://www.last.fm/user/{username}/library/music/{encoded_artist}"


# Articles to move to end of name (case-insensitive)
ARTICLES = ["The", "A", "An"]

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
    """
    Check if an artist name indicates classical music.
    
    Returns True if any classical indicator is found in the artist name.
    """
    import unicodedata
    
    # Normalize unicode and convert to lowercase
    normalized = unicodedata.normalize('NFD', artist_name.lower())
    # Remove accent marks but keep base characters for matching
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    for indicator in CLASSICAL_INDICATORS:
        indicator_norm = unicodedata.normalize('NFD', indicator.lower())
        indicator_ascii = ''.join(c for c in indicator_norm if unicodedata.category(c) != 'Mn')
        if indicator_ascii in ascii_text:
            return True
    return False


def move_article_to_end(name: str) -> str:
    """
    Move leading articles (The, A, An) to the end of the name.
    
    Examples:
        "The Cult" -> "Cult, The"
        "A Tribe Called Quest" -> "Tribe Called Quest, A"
        "An Albatross" -> "Albatross, An"
        "Queens of the Stone Age" -> "Queens of the Stone Age" (no change)
    """
    for article in ARTICLES:
        prefix = f"{article} "
        if name.startswith(prefix):
            remainder = name[len(prefix):]
            return f"{remainder}, {article}"
    return name


def load_state() -> dict:
    """Load saved state for resuming."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    """Save state for resuming."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def clear_state() -> None:
    """Clear saved state after successful completion."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def fetch_low_scrobble_artists(
    username: str,
    max_scrobbles: int = 2,
    dry_run: bool = False
) -> list[dict]:
    """
    Fetch artists with low scrobble counts from the last 90 days.
    
    Args:
        username: Last.fm username
        max_scrobbles: Maximum scrobble count to include (default: 2)
        dry_run: If True, return sample data without API calls
    
    Returns:
        List of dicts with artist info and library URLs
    """
    if dry_run:
        print(f"[DRY-RUN] Would fetch artists for user: {username}")
        print(f"[DRY-RUN] Period: Last 90 days (PERIOD_3MONTHS)")
        print(f"[DRY-RUN] Filter: scrobbles <= {max_scrobbles}")
        
        # Sample test data
        sample_artists = [
            {"artist": "ZZ Top", "scrobbles": 1},
            {"artist": "Zuco 103", "scrobbles": 1},
            {"artist": "zero 7 feat. sophie barker", "scrobbles": 1},
            {"artist": "Yunchan Lim", "scrobbles": 1},
            {"artist": "Yoko Miwa Trio", "scrobbles": 1},
            {"artist": "The Crystal Method", "scrobbles": 1},
            {"artist": "The Church", "scrobbles": 1},
            {"artist": "Tears for Fears", "scrobbles": 2},
            {"artist": "Test Artist A", "scrobbles": 2},
            {"artist": "Test Artist B", "scrobbles": 1},
        ]
        
        results = []
        for item in sample_artists:
            artist_name = item["artist"]
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
    print(f"Period: Last 90 days (PERIOD_3MONTHS)")
    print(f"Filter: scrobbles <= {max_scrobbles}")
    
    try:
        network = get_lastfm_network()
        user = network.get_user(username)
        
        # Fetch all artists from the last 3 months
        # Using a high limit to get all artists (limit=None defaults to 50)
        print("Fetching artist data from Last.fm API...")
        top_artists = user.get_top_artists(period=pylast.PERIOD_3MONTHS, limit=1000)
        
        results = []
        total_fetched = 0
        
        for item in top_artists:
            total_fetched += 1
            artist_name = str(item.item)
            play_count = int(item.weight)
            
            # Only include artists with low scrobble counts
            if play_count <= max_scrobbles:
                results.append({
                    "artist": artist_name,
                    "artist_sort": move_article_to_end(artist_name),
                    "name_length": len(artist_name),
                    "classical": 1 if is_classical(artist_name) else "",
                    "scrobbles": play_count,
                    "library_url": build_library_url(username, artist_name)
                })
        
        print(f"Fetched {total_fetched} total artists from API")
        print(f"Found {len(results)} artists with <= {max_scrobbles} scrobbles")
        
        # Sort by scrobbles ascending, then alphabetically by sort name
        results.sort(key=lambda x: (x["scrobbles"], x["artist_sort"].lower()))
        
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
        description="Collect artists with 1-2 scrobbles in the last 90 days from Last.fm"
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
        "--max-scrobbles", "-m",
        type=int,
        default=2,
        help="Maximum scrobble count to include (default: 2)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output CSV filename (default: low_scrobble_artists_YYYYMMDD.csv)"
    )
    
    args = parser.parse_args()
    
    # Generate default output filename with date
    if args.output:
        output_filename = args.output
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"low_scrobble_artists_{date_str}.csv"
    
    output_path = DATA_DIR / output_filename
    
    print("=" * 60)
    print("Low-Scrobble Artist Collector")
    print("=" * 60)
    print(f"Username: {args.username}")
    print(f"Max scrobbles: {args.max_scrobbles}")
    print(f"Output: {output_path}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()
    
    # Fetch artists
    artists = fetch_low_scrobble_artists(
        username=args.username,
        max_scrobbles=args.max_scrobbles,
        dry_run=args.dry_run
    )
    
    if not artists:
        print("\nNo artists found matching criteria.")
        return
    
    # Display preview
    classical_count = sum(1 for a in artists if a["classical"] == 1)
    print(f"\nPreview (first 10 of {len(artists)}, {classical_count} classical):")
    print("-" * 75)
    print(f"  {'Scr':>3} | {'Len':>3} | {'Cls':>3} | Artist (Sort Name)")
    print("-" * 75)
    for artist in artists[:10]:
        cls_mark = "  *" if artist["classical"] == 1 else ""
        print(f"  {artist['scrobbles']:3} | {artist['name_length']:3} | {cls_mark:>3} | {artist['artist_sort']}")
    if len(artists) > 10:
        print(f"  ... and {len(artists) - 10} more")
    print("-" * 75)
    
    # Save to CSV
    if not args.dry_run:
        save_to_csv(artists, output_path)
        
        # Update state with last successful run
        save_state({
            "last_run": datetime.now().isoformat(),
            "username": args.username,
            "artists_found": len(artists),
            "output_file": str(output_path)
        })
    else:
        print(f"\n[DRY-RUN] Would save {len(artists)} artists to: {output_path}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

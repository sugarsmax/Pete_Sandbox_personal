#!/usr/bin/env python3
"""
Fetch Top Tracks from Last.fm

Uses the Last.fm API to fetch your top tracks by scrobble count and caches them locally.
Supports --test mode for dry runs.

Created: 2025-12-06
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pylast
import yaml
from dotenv import load_dotenv

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

# Load environment variables from .env
load_dotenv(PROJECT_DIR / ".env")

# Paths
CONFIG_PATH = PROJECT_DIR / "config.yaml"
CACHE_DIR = PROJECT_DIR / "cache"
TRACKS_CACHE_PATH = CACHE_DIR / "top_tracks.json"
FETCH_LOG_PATH = CACHE_DIR / "fetch_log.json"


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def slugify(text: str) -> str:
    """Convert text to safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text)
    return text


def update_fetch_log(action: str, details: dict) -> None:
    """Update the fetch log with latest action."""
    log = {}
    if FETCH_LOG_PATH.exists():
        with open(FETCH_LOG_PATH, "r") as f:
            log = json.load(f)
    
    log[action] = {
        "timestamp": datetime.now().isoformat(),
        **details
    }
    
    with open(FETCH_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


# Classical composers/performers to filter out (case-insensitive matching)
CLASSICAL_FILTER = [
    # Major composers
    "bach", "mozart", "beethoven", "chopin", "brahms", "handel", "händel", "haydn",
    "schubert", "tchaikovsky", "vivaldi", "debussy", "liszt", "mendelssohn",
    "rachmaninoff", "ravel", "schumann", "strauss", "wagner", "dvorak", "dvořák",
    "mahler", "verdi", "puccini", "stravinsky", "prokofiev", "shostakovich",
    "grieg", "sibelius", "elgar", "holst", "bernstein", "copland", "barber",
    "gershwin", "satie", "fauré", "faure", "saint-saëns", "saint-saens",
    "rimsky-korsakov", "mussorgsky", "borodin", "paganini", "telemann",
    # Baroque/early music
    "corelli", "scarlatti", "monteverdi", "purcell", "couperin", "rameau",
    "albinoni", "boccherini", "pergolesi", "lully",
    # Classical performers (harpsichordists, etc)
    "sebestyén", "sebestyen", "gould", "horowitz", "rubinstein", "heifetz",
    # BWV/opus indicators (Bach catalog)
    "bwv ",
]


def normalize_for_filter(text: str) -> str:
    """Normalize text for classical filter matching (handle accents)."""
    import unicodedata
    # Normalize unicode and convert to lowercase
    normalized = unicodedata.normalize('NFD', text.lower())
    # Remove accent marks but keep base characters
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_text


def is_classical(artist: str, track: str = "") -> bool:
    """Check if artist/track matches classical composers or catalog numbers."""
    artist_norm = normalize_for_filter(artist)
    track_norm = normalize_for_filter(track)
    combined = f"{artist_norm} {track_norm}"
    
    for term in CLASSICAL_FILTER:
        term_norm = normalize_for_filter(term)
        if term_norm in combined:
            return True
    return False


def get_lastfm_network() -> pylast.LastFMNetwork:
    """Initialize Last.fm API connection using environment variables."""
    api_key = os.getenv("LASTFM_API_KEY")
    api_secret = os.getenv("LASTFM_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Missing Last.fm API credentials. "
            "Set LASTFM_API_KEY and LASTFM_API_SECRET in .env file."
        )
    
    return pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)


def fetch_top_tracks_from_lastfm(username: str, limit: int, test_mode: bool = False) -> list:
    """
    Fetch top tracks from Last.fm user library via API.
    
    In test mode, returns sample data without making API calls.
    """
    if test_mode:
        print(f"[TEST MODE] Would fetch top {limit} tracks for user: {username}")
        print(f"[TEST MODE] Using Last.fm API (pylast)")
        
        # Return sample test data
        return [
            {"rank": 1, "artist": "Queens of the Stone Age", "track": "No One Knows", "scrobbles": 156},
            {"rank": 2, "artist": "Stone Temple Pilots", "track": "Plush", "scrobbles": 142},
            {"rank": 3, "artist": "The Cult", "track": "She Sells Sanctuary", "scrobbles": 138},
            {"rank": 4, "artist": "Van Halen", "track": "Jump", "scrobbles": 125},
            {"rank": 5, "artist": "Soundgarden", "track": "Black Hole Sun", "scrobbles": 119},
            {"rank": 6, "artist": "Alice in Chains", "track": "Man in the Box", "scrobbles": 112},
            {"rank": 7, "artist": "Pearl Jam", "track": "Alive", "scrobbles": 108},
            {"rank": 8, "artist": "Nirvana", "track": "Smells Like Teen Spirit", "scrobbles": 101},
            {"rank": 9, "artist": "Foo Fighters", "track": "Everlong", "scrobbles": 97},
            {"rank": 10, "artist": "Red Hot Chili Peppers", "track": "Under the Bridge", "scrobbles": 93},
        ][:limit]
    
    # Production mode: Use Last.fm API
    print(f"Fetching top {limit} tracks for user: {username} via Last.fm API...")
    print("Filtering out classical composers...")
    
    try:
        network = get_lastfm_network()
        user = network.get_user(username)
        
        # Fetch extra tracks to account for filtered classical tracks
        # Last.fm API max is 1000 per request
        fetch_limit = min(int(limit * 1.2), 1000)  # Cap at API max
        top_tracks = user.get_top_tracks(period=pylast.PERIOD_OVERALL, limit=fetch_limit)
        
        tracks = []
        filtered_count = 0
        for item in top_tracks:
            track = item.item
            artist_name = str(track.artist)
            track_title = str(track.title)
            
            if is_classical(artist_name, track_title):
                filtered_count += 1
                continue
            
            tracks.append({
                "rank": len(tracks) + 1,  # Rank after filtering
                "artist": artist_name,
                "track": str(track.title),
                "scrobbles": item.weight  # Play count
            })
            
            if len(tracks) >= limit:
                break
        
        print(f"Filtered out {filtered_count} classical tracks.")
        print(f"Successfully fetched {len(tracks)} tracks from API.")
        return tracks
        
    except pylast.WSError as e:
        print(f"Last.fm API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching tracks: {e}")
        return []


def save_tracks_cache(tracks: list) -> None:
    """Save tracks to cache file."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_data = {
        "fetched_at": datetime.now().isoformat(),
        "track_count": len(tracks),
        "tracks": tracks
    }
    
    with open(TRACKS_CACHE_PATH, "w") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(tracks)} tracks to: {TRACKS_CACHE_PATH}")


def load_tracks_cache() -> dict | None:
    """Load tracks from cache if exists."""
    if TRACKS_CACHE_PATH.exists():
        with open(TRACKS_CACHE_PATH, "r") as f:
            return json.load(f)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Fetch top tracks from Last.fm user library"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run in test mode with sample data (no actual fetching)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force refresh even if cache exists"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        help="Override track limit from config"
    )
    parser.add_argument(
        "--show-cache",
        action="store_true",
        help="Display current cache contents and exit"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    username = config["lastfm"]["username"]
    limit = args.limit or config["lastfm"]["top_tracks_limit"]
    
    # Show cache mode
    if args.show_cache:
        cache = load_tracks_cache()
        if cache:
            print(f"Cache from: {cache['fetched_at']}")
            print(f"Track count: {cache['track_count']}")
            print("\nTracks:")
            for track in cache["tracks"]:
                print(f"  {track['rank']:3}. {track['artist']} - {track['track']} ({track['scrobbles']} scrobbles)")
        else:
            print("No cache found.")
        return
    
    # Check cache unless forced
    if not args.force:
        cache = load_tracks_cache()
        if cache:
            print(f"Cache exists from {cache['fetched_at']} with {cache['track_count']} tracks.")
            print("Use --force to refresh, or --show-cache to view.")
            return
    
    # Fetch tracks
    tracks = fetch_top_tracks_from_lastfm(username, limit, test_mode=args.test)
    
    if tracks:
        save_tracks_cache(tracks)
        update_fetch_log("top_tracks", {
            "username": username,
            "track_count": len(tracks),
            "test_mode": args.test
        })
        
        print(f"\nFetched {len(tracks)} tracks:")
        for track in tracks[:5]:
            print(f"  {track['rank']:3}. {track['artist']} - {track['track']} ({track['scrobbles']} scrobbles)")
        if len(tracks) > 5:
            print(f"  ... and {len(tracks) - 5} more")
    else:
        print("\nNo tracks fetched. Check your API credentials in .env or run with --test for sample data.")


if __name__ == "__main__":
    main()


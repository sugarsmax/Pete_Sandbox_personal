#!/usr/bin/env python3
"""
Fetch Lyrics for Top Tracks

Retrieves lyrics from configured provider (Musixmatch, Genius, etc.)
Caches lyrics locally to avoid re-fetching.
Supports --test mode for dry runs.

Created: 2025-12-06
"""

import argparse
import json
import os
import re
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import yaml

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

# Load .env file if it exists
ENV_FILE = PROJECT_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

CONFIG_PATH = PROJECT_DIR / "config.yaml"
CACHE_DIR = PROJECT_DIR / "cache"
LYRICS_CACHE_DIR = CACHE_DIR / "lyrics"
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
    return text[:50]  # Limit length


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


# =============================================================================
# LYRICS PROVIDER ABSTRACTION
# =============================================================================
# To add a new provider:
# 1. Create a new class inheriting from LyricsProvider
# 2. Implement fetch_lyrics() method
# 3. Add to PROVIDERS dict at bottom
# =============================================================================

class LyricsProvider(ABC):
    """Abstract base class for lyrics providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""
        pass
    
    @abstractmethod
    def fetch_lyrics(self, artist: str, track: str, test_mode: bool = False) -> str | None:
        """
        Fetch lyrics for a track.
        
        Returns:
            Lyrics text if found, None otherwise.
        """
        pass


class MusixmatchProvider(LyricsProvider):
    """
    Musixmatch lyrics provider.
    
    Note: Musixmatch's free API only returns partial lyrics (30%).
    For full lyrics, requires paid subscription or web scraping.
    This implementation uses web scraping approach.
    """
    
    @property
    def name(self) -> str:
        return "musixmatch"
    
    def fetch_lyrics(self, artist: str, track: str, test_mode: bool = False) -> str | None:
        if test_mode:
            return self._get_test_lyrics(artist, track)
        
        # Production: Use Playwright MCP to scrape Musixmatch
        # URL format: https://www.musixmatch.com/lyrics/{artist}/{track}
        artist_slug = slugify(artist).replace("_", "-")
        track_slug = slugify(track).replace("_", "-")
        url = f"https://www.musixmatch.com/lyrics/{artist_slug}/{track_slug}"
        
        print(f"  [Musixmatch] URL: {url}")
        print(f"  [INFO] Use Playwright MCP browser to fetch lyrics from this page.")
        
        return None
    
    def _get_test_lyrics(self, artist: str, track: str) -> str:
        """Return sample lyrics for test mode."""
        # Sample lyrics snippets (not real copyrighted lyrics)
        samples = {
            "no one knows": "We drive through the night\nSearching for meaning in the darkness\nNo one knows where the road leads\nBut we keep on driving",
            "plush": "And I feel that time's a wasted go\nSo where ya going to tomorrow?\nAnd I see that these are lies to come\nWould you even care?",
            "she sells sanctuary": "The world drags me down\nBut she gives me shelter\nIn her eyes I find\nA sanctuary from the storm",
            "jump": "I get up, and nothing gets me down\nYou got it tough, I've seen the toughest around\nAnd I know, baby, just how you feel",
            "black hole sun": "In my eyes, indisposed\nIn disguises no one knows\nHides the face, lies the snake\nThe sun in my disgrace",
            "man in the box": "I'm the man in the box\nBuried in my pit\nWon't you come and save me\nSave me",
            "alive": "Is something wrong, she said\nOf course there is\nYou're still alive, she said\nOh, and do I deserve to be",
            "smells like teen spirit": "Load up on guns, bring your friends\nIt's fun to lose and to pretend\nShe's over-bored and self-assured",
            "everlong": "Hello, I've waited here for you\nEverlong\nTonight, I throw myself into\nAnd out of the red",
            "under the bridge": "Sometimes I feel like I don't have a partner\nSometimes I feel like my only friend\nIs the city I live in, the city of angels",
        }
        
        track_lower = track.lower()
        for key, lyrics in samples.items():
            if key in track_lower:
                return lyrics
        
        # Default sample
        return f"[Sample lyrics for '{track}' by {artist}]\nThis is placeholder text for testing.\nReal lyrics would be fetched from Musixmatch."


class GeniusProvider(LyricsProvider):
    """
    Genius lyrics provider.
    
    Reads API token from GENIUS_ACCESS_TOKEN environment variable.
    Uses lyricsgenius library.
    """
    
    def __init__(self, api_key: str | None = None):
        # Try environment variable first, then passed key
        self.api_key = os.environ.get("GENIUS_ACCESS_TOKEN") or api_key
    
    @property
    def name(self) -> str:
        return "genius"
    
    def fetch_lyrics(self, artist: str, track: str, test_mode: bool = False) -> str | None:
        if test_mode:
            return f"[Genius test lyrics for '{track}' by {artist}]"
        
        if not self.api_key:
            print("  [Genius] No API token found.")
            print("  [Genius] Set GENIUS_ACCESS_TOKEN env var or create .env file")
            return None
        
        try:
            import lyricsgenius
            genius = lyricsgenius.Genius(self.api_key, verbose=False, remove_section_headers=True)
            song = genius.search_song(track, artist)
            if song:
                # Clean up lyrics (remove embed text at end)
                lyrics = song.lyrics
                if "Embed" in lyrics:
                    lyrics = lyrics.rsplit("Embed", 1)[0].strip()
                # Remove song title header if present
                if lyrics.startswith(track):
                    lines = lyrics.split("\n", 1)
                    if len(lines) > 1:
                        lyrics = lines[1].strip()
                return lyrics
        except ImportError:
            print("  [Genius] lyricsgenius not installed. Run: pip install lyricsgenius")
        except Exception as e:
            print(f"  [Genius] Error: {e}")
        
        return None


class AZLyricsProvider(LyricsProvider):
    """
    AZLyrics scraper provider.
    
    Warning: AZLyrics has aggressive anti-scraping measures.
    Use with caution and respect rate limits.
    """
    
    @property
    def name(self) -> str:
        return "azlyrics"
    
    def fetch_lyrics(self, artist: str, track: str, test_mode: bool = False) -> str | None:
        if test_mode:
            return f"[AZLyrics test lyrics for '{track}' by {artist}]"
        
        # AZLyrics URL format
        artist_clean = re.sub(r"[^a-z]", "", artist.lower())
        track_clean = re.sub(r"[^a-z]", "", track.lower())
        url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{track_clean}.html"
        
        print(f"  [AZLyrics] URL: {url}")
        print(f"  [WARNING] AZLyrics has aggressive anti-scraping. May require browser automation.")
        
        return None


# Provider registry - add new providers here
PROVIDERS = {
    "musixmatch": MusixmatchProvider,
    "genius": GeniusProvider,
    "azlyrics": AZLyricsProvider,
}


def get_provider(config: dict) -> LyricsProvider:
    """Get configured lyrics provider."""
    provider_name = config["lyrics"]["provider"]
    
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}. Options: {list(PROVIDERS.keys())}")
    
    provider_class = PROVIDERS[provider_name]
    
    # Handle provider-specific initialization
    if provider_name == "genius":
        # API key is read from environment variable in the GeniusProvider class
        genius_config = config.get("lyrics", {}).get("genius") or {}
        api_key = genius_config.get("api_key") if isinstance(genius_config, dict) else None
        return provider_class(api_key=api_key)
    
    return provider_class()


# =============================================================================
# CACHE MANAGEMENT
# =============================================================================

def get_lyrics_cache_path(artist: str, track: str) -> Path:
    """Get cache file path for a track's lyrics (organized by artist folder)."""
    artist_dir = LYRICS_CACHE_DIR / slugify(artist)
    artist_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(track)}.txt"
    return artist_dir / filename


def is_lyrics_cached(artist: str, track: str, max_age_days: int = 30) -> bool:
    """Check if lyrics are cached and not too old."""
    cache_path = get_lyrics_cache_path(artist, track)
    if not cache_path.exists():
        return False
    
    # Check age
    mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
    age_days = (datetime.now() - mtime).days
    return age_days < max_age_days


def load_cached_lyrics(artist: str, track: str) -> str | None:
    """Load lyrics from cache."""
    cache_path = get_lyrics_cache_path(artist, track)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    return None


def save_lyrics_cache(artist: str, track: str, lyrics: str) -> None:
    """Save lyrics to cache."""
    LYRICS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_lyrics_cache_path(artist, track)
    cache_path.write_text(lyrics, encoding="utf-8")


def load_tracks() -> list:
    """Load tracks from cache."""
    if not TRACKS_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"No tracks cache found at {TRACKS_CACHE_PATH}. "
            "Run fetch_top_tracks first."
        )
    
    with open(TRACKS_CACHE_PATH, "r") as f:
        data = json.load(f)
    
    return data["tracks"]


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Fetch lyrics for cached top tracks"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run in test mode with sample lyrics (no actual fetching)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force refresh all lyrics even if cached"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fetched without actually fetching"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show lyrics cache status and exit"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    provider = get_provider(config)
    delay = config["lyrics"]["request_delay"]
    max_age = config["lyrics"]["cache_max_age_days"]
    
    # Load tracks
    try:
        tracks = load_tracks()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    print(f"Lyrics provider: {provider.name}")
    print(f"Tracks to process: {len(tracks)}")
    
    # Status mode
    if args.status:
        cached = 0
        missing = 0
        for track in tracks:
            if is_lyrics_cached(track["artist"], track["track"], max_age):
                cached += 1
            else:
                missing += 1
        
        print(f"\nCache status:")
        print(f"  Cached: {cached}")
        print(f"  Missing: {missing}")
        
        if missing > 0:
            print(f"\nMissing lyrics for:")
            for track in tracks:
                if not is_lyrics_cached(track["artist"], track["track"], max_age):
                    print(f"  - {track['artist']} - {track['track']}")
        return 0
    
    # Process tracks
    fetched = 0
    cached = 0
    failed = 0
    
    for i, track in enumerate(tracks):
        artist = track["artist"]
        track_name = track["track"]
        
        print(f"\n[{i+1}/{len(tracks)}] {artist} - {track_name}")
        
        # Check cache
        if not args.force and is_lyrics_cached(artist, track_name, max_age):
            print("  [CACHED] Lyrics already cached")
            cached += 1
            continue
        
        # Dry run mode
        if args.dry_run:
            print(f"  [DRY RUN] Would fetch lyrics")
            continue
        
        # Fetch lyrics
        lyrics = provider.fetch_lyrics(artist, track_name, test_mode=args.test)
        
        if lyrics:
            save_lyrics_cache(artist, track_name, lyrics)
            print(f"  [SAVED] {len(lyrics)} characters")
            fetched += 1
        else:
            print("  [FAILED] No lyrics retrieved")
            failed += 1
        
        # Rate limiting
        if i < len(tracks) - 1 and not args.test:
            time.sleep(delay)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Already cached: {cached}")
    print(f"  Newly fetched: {fetched}")
    print(f"  Failed: {failed}")
    
    if fetched > 0:
        update_fetch_log("lyrics", {
            "provider": provider.name,
            "fetched": fetched,
            "cached": cached,
            "failed": failed,
            "test_mode": args.test
        })
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


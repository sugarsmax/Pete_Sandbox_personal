#!/usr/bin/env python3
"""
WhoSampled Covers Scraper
=========================
Scrapes whosampled.com to find covers of favorite songs from Last.fm data.
Uses Playwright for JavaScript-rendered content.

Usage:
    python whosampled_scraper_20251209.py [options]

Options:
    --dry-run       Print URLs without fetching (test mode)
    --test          Alias for --dry-run
    --limit N       Process only first N songs
    --force         Re-fetch even if cached
    --retry-errors  Re-fetch only songs that previously had errors
    --min-scrobbles N   Override minimum scrobbles threshold
    --artist "X"    Filter to specific artist (partial match)
    --verbose       Show detailed progress
    --headless      Run browser in headless mode (default: True)

Author: Built by AI Assistant (Claude Opus 4.5)
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# =============================================================================
# CONFIGURATION
# =============================================================================

def get_script_dir() -> Path:
    """Get the directory containing this script."""
    return Path(__file__).parent.resolve()


def get_project_dir() -> Path:
    """Get the project root directory (parent of scripts/)."""
    return get_script_dir().parent


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = get_project_dir() / "config.yaml"
    if not config_path.exists():
        logging.warning(f"Config file not found at {config_path}, using defaults")
        return get_default_config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        # Resolve any environment variable references in paths
        config = _resolve_env_vars(config)
        return config


def _resolve_env_vars(obj):
    """Recursively resolve $VAR and ~/ references in config strings."""
    import os as os_module
    
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(v) for v in obj]
    elif isinstance(obj, str):
        # Expand ~ and environment variables
        expanded = os_module.path.expanduser(obj)
        expanded = os_module.path.expandvars(expanded)
        return expanded
    return obj


def get_default_config() -> dict:
    """Return default configuration."""
    return {
        'source': {'top_tracks_path': '../Lyrics_top_songs/cache/top_tracks.json'},
        'filters': {
            'min_scrobbles': 10,
            'excluded_genres': ['classical', 'easy listening'],
            'excluded_cover_genres': ['classical', 'easy listening'],
            'excluded_cover_artists': ['8 Bit Arcade', 'Music Box Mania', 'String Tribute Players'],
            'include_artists': [],
            'exclude_artists': []
        },
        'scraping': {
            'request_delay': 2.5,
            'max_retries': 3,
            'timeout': 30,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        },
        'output': {
            'cache_dir': 'cache',
            'data_dir': 'data',
            'output_dir': 'output'
        },
        'limits': {
            'max_songs': 0,
            'start_rank': 1
        }
    }


# =============================================================================
# URL GENERATION
# =============================================================================

def slugify_for_whosampled(text: str) -> str:
    """
    Convert artist/track name to WhoSampled URL slug format.
    
    WhoSampled URL encoding rules (discovered through testing):
    - Spaces become dashes
    - & becomes 'and'
    - Some punctuation is URL-encoded: ? ! ' + #
    - Other punctuation is stripped: " ( ) [ ] { } @ $ ^ * = < > , . ; : / \\ | ` ~
    """
    if not text:
        return ""
    
    # Replace & with 'and'
    slug = text.replace('&', 'and')
    
    # First, remove problematic characters (but NOT the ones we'll URL-encode)
    # Note: Don't remove ? ! ' + # as we'll encode them
    slug = re.sub(r'["\(\)\[\]\{\}@$^*=<>,.;:/\\|`~]', '', slug)
    
    # Replace multiple spaces with single space
    slug = re.sub(r'\s+', ' ', slug)
    
    # Replace spaces with dashes
    slug = slug.strip().replace(' ', '-')
    
    # Remove multiple consecutive dashes
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing dashes
    slug = slug.strip('-')
    
    # URL-encode specific punctuation that WhoSampled preserves
    # Do this AFTER other transformations to avoid % being affected
    url_encode_chars = {
        '?': '%3F',   # Question mark (e.g., "Would?")
        '!': '%21',   # Exclamation (e.g., "Help!")
        "'": '%27',   # Apostrophe (e.g., "Don't")  
        '+': '%2B',   # Plus sign
        '#': '%23',   # Hash
    }
    
    for char, encoded in url_encode_chars.items():
        slug = slug.replace(char, encoded)
    
    return slug


def generate_whosampled_url(artist: str, track: str) -> str:
    """Generate the WhoSampled covers URL for a song."""
    artist_slug = slugify_for_whosampled(artist)
    track_slug = slugify_for_whosampled(track)
    return f"https://www.whosampled.com/{artist_slug}/{track_slug}/covered/"


def generate_cache_key(artist: str, track: str) -> str:
    """Generate a cache key for a song."""
    artist_clean = re.sub(r'[^a-z0-9]', '_', artist.lower())
    track_clean = re.sub(r'[^a-z0-9]', '_', track.lower())
    return f"{artist_clean}__{track_clean}"


# =============================================================================
# DATA LOADING
# =============================================================================

def load_top_tracks(config: dict) -> list:
    """Load top tracks from the source JSON file."""
    source_path = config['source']['top_tracks_path']
    
    # Handle relative path
    if not os.path.isabs(source_path):
        source_path = get_project_dir() / source_path
    else:
        source_path = Path(source_path)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Top tracks file not found: {source_path}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('tracks', [])


def load_search_log(config: dict) -> dict:
    """Load the search log from cache."""
    cache_dir = get_project_dir() / config['output']['cache_dir']
    log_path = cache_dir / "search_log.json"
    
    if not log_path.exists():
        return {
            'last_updated': None,
            'total_searched': 0,
            'total_with_covers': 0,
            'searches': {}
        }
    
    with open(log_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_search_log(config: dict, log: dict) -> None:
    """Save the search log to cache."""
    cache_dir = get_project_dir() / config['output']['cache_dir']
    cache_dir.mkdir(parents=True, exist_ok=True)
    log_path = cache_dir / "search_log.json"
    
    log['last_updated'] = datetime.now().isoformat()
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


# =============================================================================
# FILTERING
# =============================================================================

def is_classical_artist(artist: str, excluded_genres: list) -> bool:
    """
    Check if an artist is likely classical based on name patterns.
    """
    classical_indicators = [
        'symphony', 'orchestra', 'philharmonic', 'quartet', 'ensemble',
        'chamber', 'choir', 'chorale', 'opera', 'baroque', 'strings',
        'piano trio', 'wind quintet'
    ]
    
    artist_lower = artist.lower()
    return any(indicator in artist_lower for indicator in classical_indicators)


def filter_tracks(tracks: list, config: dict, args) -> list:
    """Filter tracks based on configuration and CLI arguments."""
    filters = config['filters']
    min_scrobbles = args.min_scrobbles if args.min_scrobbles else filters.get('min_scrobbles', 10)
    excluded_genres = [g.lower() for g in filters.get('excluded_genres', [])]
    exclude_artists = [a.lower() for a in filters.get('exclude_artists', [])]
    include_artists = [a.lower() for a in filters.get('include_artists', [])]
    
    filtered = []
    for track in tracks:
        artist = track.get('artist', '')
        scrobbles = track.get('scrobbles', 0)
        
        # Check minimum scrobbles
        if scrobbles < min_scrobbles:
            continue
        
        # Check artist exclusion
        if any(exc in artist.lower() for exc in exclude_artists):
            continue
        
        # Check artist inclusion (if specified)
        if include_artists and not any(inc in artist.lower() for inc in include_artists):
            continue
        
        # Check if classical artist (heuristic)
        if is_classical_artist(artist, excluded_genres):
            continue
        
        # CLI artist filter
        if args.artist and args.artist.lower() not in artist.lower():
            continue
        
        filtered.append(track)
    
    return filtered


# =============================================================================
# WEB SCRAPING WITH PLAYWRIGHT
# =============================================================================

class WhoSampledScraper:
    """Playwright-based scraper for WhoSampled.com."""
    
    def __init__(self, config: dict, headless: bool = True):
        self.config = config
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent=self.config['scraping'].get('user_agent', 'Mozilla/5.0'),
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            viewport={"width": 1280, "height": 720}
        )
        self.page = self.context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def fetch_covers(self, url: str) -> dict:
        """
        Fetch covers from a WhoSampled URL.
        
        Goes directly to the /covered/ URL since this avoids Cloudflare
        challenges that block the main song page.
        
        Returns dict with:
            - status: 'found' | 'no_covers' | 'not_found' | 'error'
            - covers: list of cover dicts
            - url: the URL attempted
        """
        result = {
            'status': 'error',
            'covers': [],
            'url': url,
            'searched_at': datetime.now().isoformat()
        }
        
        try:
            timeout = self.config['scraping'].get('timeout', 30) * 1000  # ms
            # Use domcontentloaded instead of networkidle (WhoSampled never idles)
            response = self.page.goto(url, timeout=timeout, wait_until='domcontentloaded')
            
            if response and response.status == 404:
                result['status'] = 'not_found'
                return result
            
            # Wait for table to be visible (more reliable than fixed timeout)
            try:
                self.page.wait_for_selector('table tr', timeout=5000)
            except Exception:
                # Table might not exist if no covers
                pass
            
            # Extra wait for JS rendering
            self.page.wait_for_timeout(1500)
            
            # Check if page shows "no covers" message
            no_covers_selector = 'text="has not been covered"'
            if self.page.query_selector(no_covers_selector):
                result['status'] = 'no_covers'
                return result
            
            # Parse covers from the page
            covers = self._parse_covers()
            
            if covers:
                result['status'] = 'found'
                result['covers'] = covers
                result['covers_count'] = len(covers)
            else:
                result['status'] = 'no_covers'
            
            return result
            
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            return result
    
    def _parse_covers(self) -> list:
        """Parse covers from the current page."""
        covers = []
        excluded_cover_genres = [g.lower() for g in 
                                self.config['filters'].get('excluded_cover_genres', [])]
        excluded_cover_artists = [a.lower() for a in 
                                 self.config['filters'].get('excluded_cover_artists', [])]
        
        # WhoSampled uses table rows for covers
        # Each row has: thumbnail, title, artist, year, genre
        rows = self.page.query_selector_all('table tr')
        
        for row in rows:
            try:
                cells = row.query_selector_all('td')
                if len(cells) < 4:
                    continue
                
                # Extract data (skip thumbnail cell)
                title_el = cells[1].query_selector('a') if len(cells) > 1 else None
                title = title_el.inner_text().strip() if title_el else ""
                
                # Get the cover's WhoSampled URL from the title link
                cover_url = ""
                if title_el:
                    href = title_el.get_attribute('href')
                    if href:
                        # Convert relative URL to absolute
                        cover_url = f"https://www.whosampled.com{href}" if href.startswith('/') else href
                
                artist_el = cells[2] if len(cells) > 2 else None
                artist_links = artist_el.query_selector_all('a') if artist_el else []
                artists = [a.inner_text().strip() for a in artist_links]
                artist = ' feat. '.join(artists) if artists else ""
                
                year_el = cells[3] if len(cells) > 3 else None
                year = year_el.inner_text().strip() if year_el else ""
                
                genre_el = cells[4] if len(cells) > 4 else None
                genre = genre_el.inner_text().strip() if genre_el else ""
                
                # Skip if missing essential data
                if not title or not artist:
                    continue
                
                # Filter out excluded cover genres
                if any(exc in genre.lower() for exc in excluded_cover_genres):
                    logging.debug(f"Skipping excluded genre cover: {artist} - {title} [{genre}]")
                    continue
                
                # Filter out excluded cover artists
                if any(exc in artist.lower() for exc in excluded_cover_artists):
                    logging.debug(f"Skipping excluded artist cover: {artist} - {title}")
                    continue
                
                covers.append({
                    'cover_track': title,
                    'cover_artist': artist,
                    'cover_year': year,
                    'cover_genre': genre,
                    'cover_url': cover_url
                })
                
            except Exception as e:
                logging.debug(f"Error parsing row: {e}")
                continue
        
        return covers


def scrape_covers_for_track(track: dict, config: dict, scraper: WhoSampledScraper, 
                           dry_run: bool = False) -> dict:
    """
    Scrape covers for a single track.
    """
    artist = track.get('artist', '')
    track_name = track.get('track', '')
    url = generate_whosampled_url(artist, track_name)
    
    if dry_run:
        return {
            'status': 'dry_run',
            'covers': [],
            'url': url,
            'searched_at': datetime.now().isoformat()
        }
    
    return scraper.fetch_covers(url)


# =============================================================================
# OUTPUT
# =============================================================================

def save_covers_to_csv(covers_data: list, config: dict) -> None:
    """Save all covers to a master CSV file."""
    data_dir = get_project_dir() / config['output']['data_dir']
    data_dir.mkdir(parents=True, exist_ok=True)
    
    date_suffix = datetime.now().strftime('%Y%m%d')
    csv_path = data_dir / f"covers_master_{date_suffix}.csv"
    
    fieldnames = [
        'original_rank', 'original_artist', 'original_track', 'original_scrobbles',
        'cover_artist', 'cover_track', 'cover_year', 'cover_genre',
        'cover_url', 'whosampled_url', 'fetched_at'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(covers_data)
    
    logging.info(f"Saved {len(covers_data)} covers to {csv_path}")


def save_covers_by_song(covers_by_song: dict, config: dict) -> None:
    """Save covers grouped by original song to JSON."""
    data_dir = get_project_dir() / config['output']['data_dir']
    data_dir.mkdir(parents=True, exist_ok=True)
    
    date_suffix = datetime.now().strftime('%Y%m%d')
    json_path = data_dir / f"covers_by_song_{date_suffix}.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(covers_by_song, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Saved covers by song to {json_path}")


def generate_report(covers_by_song: dict, config: dict, stats: dict) -> None:
    """Generate a markdown report of found covers from the full cache."""
    output_dir = get_project_dir() / config['output']['output_dir']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_suffix = datetime.now().strftime('%Y%m%d')
    report_path = output_dir / f"covers_report_{date_suffix}.md"
    
    # Load full cache to get complete picture
    search_log = load_search_log(config)
    
    # Categorize all searched songs
    songs_with_covers = {}
    songs_no_covers = []
    songs_not_found = []
    songs_error = []
    total_covers = 0
    
    for key, data in search_log.get('searches', {}).items():
        status = data.get('status', '')
        covers_count = data.get('covers_count', 0)
        url = data.get('url', '')
        
        # Parse key for display
        parts = key.split("__")
        artist = " ".join(word.capitalize() for word in parts[0].split("_"))
        track = " ".join(word.capitalize() for word in parts[1].split("_")) if len(parts) > 1 else "Unknown"
        display_name = f"{artist} - {track}"
        
        if status == "found" and covers_count > 0:
            songs_with_covers[key] = {
                'display_name': display_name,
                'whosampled_url': url,
                'covers': data.get('covers', [])
            }
            total_covers += covers_count
        elif status == "found" or status == "no_covers":
            songs_no_covers.append((display_name, url))
        elif status == "not_found":
            songs_not_found.append(display_name)
        elif status == "error":
            songs_error.append(display_name)
    
    lines = [
        "# Covers of Favorite Songs",
        "",
        "> This page was built by an AI assistant (Claude Opus 4.5)",
        "",
        "## Summary",
        "",
        f"- **Songs with covers**: {len(songs_with_covers)}",
        f"- **Songs searched (no covers)**: {len(songs_no_covers)}",
        f"- **Songs not on WhoSampled**: {len(songs_not_found)}",
        f"- **Errors (can retry)**: {len(songs_error)}",
        f"- **Total covers found**: {total_covers}",
        f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "# Songs With Covers",
        "",
    ]
    
    # Sort by number of covers (most covered first)
    sorted_songs = sorted(
        songs_with_covers.items(),
        key=lambda x: len(x[1].get('covers', [])),
        reverse=True
    )
    
    for song_key, song_data in sorted_songs:
        covers = song_data.get('covers', [])
        if not covers:
            continue
        
        display_name = song_data.get('display_name', 'Unknown')
        url = song_data.get('whosampled_url', '')
        
        lines.append(f"## {display_name}")
        lines.append("")
        lines.append(f"<a href=\"{url}\" target=\"_blank\">View on WhoSampled</a>")
        lines.append("")
        lines.append(f"**{len(covers)} cover(s) found:**")
        lines.append("")
        
        for cover in covers:
            cover_artist = cover.get('cover_artist', 'Unknown')
            cover_year = cover.get('cover_year', '')
            cover_genre = cover.get('cover_genre', '')
            cover_url = cover.get('cover_url', '')
            year_str = f" ({cover_year})" if cover_year else ""
            genre_str = f" [{cover_genre}]" if cover_genre else ""
            
            # Include link to cover's WhoSampled page if available
            if cover_url:
                lines.append(f"- <a href=\"{cover_url}\" target=\"_blank\">{cover_artist}</a>{year_str}{genre_str}")
            else:
                lines.append(f"- {cover_artist}{year_str}{genre_str}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Songs with no covers section
    if songs_no_covers:
        lines.append("# Songs With No Covers")
        lines.append("")
        lines.append("These songs were searched but had no covers (or only filtered covers).")
        lines.append("")
        songs_no_covers.sort(key=lambda x: x[0])
        for display_name, url in songs_no_covers:
            if url:
                lines.append(f"- <a href=\"{url}\" target=\"_blank\">{display_name}</a>")
            else:
                lines.append(f"- {display_name}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Songs not found section
    if songs_not_found:
        lines.append("# Songs Not Found on WhoSampled")
        lines.append("")
        songs_not_found.sort()
        for song in songs_not_found:
            lines.append(f"- {song}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Songs with errors section
    if songs_error:
        lines.append("# Songs With Errors (Can Retry)")
        lines.append("")
        songs_error.sort()
        for song in songs_error:
            lines.append(f"- {song}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Add footer with agent model info
    lines.append("")
    lines.append("*Generated with Claude Opus 4.5*")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    logging.info(f"Generated report at {report_path}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrape WhoSampled.com for covers of favorite songs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python whosampled_scraper_20251209.py --dry-run --limit 10
  python whosampled_scraper_20251209.py --artist "Queens of the Stone Age"
  python whosampled_scraper_20251209.py --min-scrobbles 50 --limit 100
  python whosampled_scraper_20251209.py --force  # Re-fetch all
  python whosampled_scraper_20251209.py --retry-errors  # Retry failed songs only
  python whosampled_scraper_20251209.py --no-headless  # Show browser
        """
    )
    
    parser.add_argument('--dry-run', '--test', action='store_true',
                        help='Print URLs without fetching (test mode)')
    parser.add_argument('--limit', type=int, default=0,
                        help='Process only first N songs (0 = unlimited)')
    parser.add_argument('--force', action='store_true',
                        help='Re-fetch even if already cached')
    parser.add_argument('--min-scrobbles', type=int, default=None,
                        help='Override minimum scrobbles threshold')
    parser.add_argument('--artist', type=str, default=None,
                        help='Filter to specific artist (partial match)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed progress')
    parser.add_argument('--no-headless', action='store_true',
                        help='Show browser window (default: headless)')
    parser.add_argument('--retry-errors', action='store_true',
                        help='Re-fetch songs that previously had errors')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    # Load configuration
    config = load_config()
    
    # Load source data
    logging.info("Loading top tracks...")
    tracks = load_top_tracks(config)
    logging.info(f"Loaded {len(tracks)} tracks from source")
    
    # Filter tracks
    filtered_tracks = filter_tracks(tracks, config, args)
    logging.info(f"After filtering: {len(filtered_tracks)} tracks")
    
    # Apply limit
    if args.limit > 0:
        filtered_tracks = filtered_tracks[:args.limit]
        logging.info(f"Limited to {len(filtered_tracks)} tracks")
    
    # Load search log (for caching)
    search_log = load_search_log(config)
    
    # Prepare output containers
    all_covers = []
    covers_by_song = {}
    
    # Stats tracking
    stats = {
        'total_searched': 0,
        'songs_with_covers': 0,
        'total_covers': 0,
        'skipped_cached': 0,
        'not_found': 0,
        'errors': 0
    }
    
    request_delay = config['scraping'].get('request_delay', 2.5)
    headless = not args.no_headless
    
    # Use context manager for Playwright
    scraper_context = None if args.dry_run else WhoSampledScraper(config, headless=headless)
    
    try:
        if not args.dry_run:
            scraper_context.__enter__()
        
        # Process each track
        for i, track in enumerate(filtered_tracks):
            artist = track.get('artist', '')
            track_name = track.get('track', '')
            scrobbles = track.get('scrobbles', 0)
            rank = track.get('rank', i + 1)
            
            cache_key = generate_cache_key(artist, track_name)
            
            # Check cache (unless --force or --retry-errors for error entries)
            if not args.force and cache_key in search_log.get('searches', {}):
                cached = search_log['searches'][cache_key]
                
                # If --retry-errors and this was an error, don't skip - fall through to re-fetch
                if args.retry_errors and cached.get('status') == 'error':
                    logging.info(f"[{i+1}/{len(filtered_tracks)}] Retrying error: {artist} - {track_name}")
                    # Don't continue - let it fall through to the scraping code below
                else:
                    # Normal cache hit - skip this track
                    stats['skipped_cached'] += 1
                    
                    # If we have cached covers, add them to output
                    if cached.get('status') == 'found' and 'covers' in cached:
                        covers_by_song[cache_key] = {
                            'original_artist': artist,
                            'original_track': track_name,
                            'original_scrobbles': scrobbles,
                            'original_rank': rank,
                            'whosampled_url': cached.get('url', ''),
                            'covers': cached.get('covers', [])
                        }
                        stats['songs_with_covers'] += 1
                        stats['total_covers'] += len(cached.get('covers', []))
                        
                        # Add to flat list
                        for cover in cached.get('covers', []):
                            all_covers.append({
                                'original_rank': rank,
                                'original_artist': artist,
                                'original_track': track_name,
                                'original_scrobbles': scrobbles,
                                'cover_artist': cover.get('cover_artist', ''),
                                'cover_track': cover.get('cover_track', ''),
                                'cover_year': cover.get('cover_year', ''),
                                'cover_genre': cover.get('cover_genre', ''),
                                'cover_url': cover.get('cover_url', ''),
                                'whosampled_url': cached.get('url', ''),
                                'fetched_at': cached.get('searched_at', '')
                            })
                    
                    if args.verbose:
                        logging.debug(f"[{i+1}/{len(filtered_tracks)}] Cached: {artist} - {track_name}")
                    continue
            
            # Log progress
            logging.info(f"[{i+1}/{len(filtered_tracks)}] {artist} - {track_name}")
            
            # Scrape covers
            result = scrape_covers_for_track(track, config, scraper_context, dry_run=args.dry_run)
            
            if args.dry_run:
                logging.info(f"  URL: {result['url']}")
                continue
            
            stats['total_searched'] += 1
            
            # Process result
            if result['status'] == 'found':
                covers = result['covers']
                stats['songs_with_covers'] += 1
                stats['total_covers'] += len(covers)
                
                logging.info(f"  Found {len(covers)} cover(s)")
                
                # Store in covers_by_song
                covers_by_song[cache_key] = {
                    'original_artist': artist,
                    'original_track': track_name,
                    'original_scrobbles': scrobbles,
                    'original_rank': rank,
                    'whosampled_url': result['url'],
                    'covers': covers
                }
                
                # Add to flat list for CSV
                for cover in covers:
                    all_covers.append({
                        'original_rank': rank,
                        'original_artist': artist,
                        'original_track': track_name,
                        'original_scrobbles': scrobbles,
                        'cover_artist': cover.get('cover_artist', ''),
                        'cover_track': cover.get('cover_track', ''),
                        'cover_year': cover.get('cover_year', ''),
                        'cover_genre': cover.get('cover_genre', ''),
                        'cover_url': cover.get('cover_url', ''),
                        'whosampled_url': result['url'],
                        'fetched_at': result['searched_at']
                    })
                
            elif result['status'] == 'not_found':
                stats['not_found'] += 1
                logging.info(f"  Not found on WhoSampled")
                
            elif result['status'] == 'no_covers':
                logging.info(f"  No covers found")
                
            else:
                stats['errors'] += 1
                logging.warning(f"  Error: {result.get('error', 'Unknown')}")
            
            # Update search log
            search_log['searches'][cache_key] = {
                'searched_at': result['searched_at'],
                'status': result['status'],
                'url': result['url'],
                'covers_count': len(result.get('covers', [])),
                'covers': result.get('covers', []) if result['status'] == 'found' else []
            }
            
            # Save search log after each request (crash-safe)
            search_log['total_searched'] = stats['total_searched']
            search_log['total_with_covers'] = stats['songs_with_covers']
            save_search_log(config, search_log)
            
            # Rate limiting
            if i < len(filtered_tracks) - 1:
                time.sleep(request_delay)
    
    finally:
        if scraper_context and not args.dry_run:
            scraper_context.__exit__(None, None, None)
    
    # Final output
    if not args.dry_run:
        # Always save CSV and JSON if we have covers
        if all_covers:
            save_covers_to_csv(all_covers, config)
            save_covers_by_song(covers_by_song, config)
        # Always regenerate report from cache (includes all searched songs)
        generate_report(covers_by_song, config, stats)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Tracks processed:    {stats['total_searched']}")
    print(f"Skipped (cached):    {stats['skipped_cached']}")
    print(f"Songs with covers:   {stats['songs_with_covers']}")
    print(f"Total covers found:  {stats['total_covers']}")
    print(f"Not on WhoSampled:   {stats['not_found']}")
    print(f"Errors:              {stats['errors']}")
    print("=" * 50)


if __name__ == '__main__':
    main()

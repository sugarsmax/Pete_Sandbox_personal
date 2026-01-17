#!/usr/bin/env python3
"""
Find Duplicate Artists in Last.fm Library

Uses fuzzy string matching to identify potential duplicate artists in your
Last.fm library that may need to be merged or cleaned up.

Supports:
- --dry-run mode for testing without API calls
- Configurable similarity threshold
- Multiple matching strategies (fuzzy, token, normalized)

Created: 2026-01-16
"""

import argparse
import csv
import os
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pylast
from dotenv import load_dotenv
from rapidfuzz import fuzz, process

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent  # last.fm folder
ENV_PATH = PROJECT_DIR / "Lyrics_top_songs" / ".env"  # Shared credentials

# Output paths
DATA_DIR = SCRIPT_DIR / "data"

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


def normalize_artist_name(name: str) -> str:
    """
    Normalize artist name for comparison.
    - Lowercase
    - Remove accents
    - Remove punctuation
    - Remove common prefixes (The, A, An)
    - Normalize whitespace
    """
    # Lowercase
    name = name.lower()
    
    # Remove accents
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Remove "the", "a", "an" from start
    name = re.sub(r'^(the|a|an)\s+', '', name)
    
    # Remove common feature indicators and normalize
    name = re.sub(r'\s*(feat\.?|ft\.?|featuring|&|and|with)\s*', ' ', name)
    
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name


def get_tokens(name: str) -> set:
    """Get normalized word tokens from artist name."""
    normalized = normalize_artist_name(name)
    return set(normalized.split())


def token_similarity(name1: str, name2: str) -> float:
    """Calculate Jaccard similarity between token sets."""
    tokens1 = get_tokens(name1)
    tokens2 = get_tokens(name2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    
    return len(intersection) / len(union) * 100


def build_library_url(username: str, artist_name: str) -> str:
    """Build the Last.fm library URL for an artist."""
    import urllib.parse
    encoded_artist = urllib.parse.quote(artist_name, safe='')
    return f"https://www.last.fm/user/{username}/library/music/{encoded_artist}"


def find_potential_duplicates(
    artists: list[dict],
    threshold: float = 85.0,
    username: str = "sugarsmax"
) -> list[dict]:
    """
    Find potential duplicate artists using multiple matching strategies.
    
    Args:
        artists: List of artist dicts with 'artist' and 'scrobbles' keys
        threshold: Minimum similarity score to consider a match (0-100)
    
    Returns:
        List of potential duplicate pairs with similarity info
    """
    duplicates = []
    n = len(artists)
    
    # Pre-compute normalized names
    normalized = {a['artist']: normalize_artist_name(a['artist']) for a in artists}
    
    print(f"Comparing {n} artists ({n * (n-1) // 2:,} pairs)...")
    
    for i, artist1 in enumerate(artists):
        name1 = artist1['artist']
        norm1 = normalized[name1]
        
        for j in range(i + 1, n):
            artist2 = artists[j]
            name2 = artist2['artist']
            norm2 = normalized[name2]
            
            # Skip if normalized names are identical (definite duplicate)
            if norm1 == norm2 and name1 != name2:
                duplicates.append({
                    'artist_a': name1,
                    'scrobbles_a': artist1['scrobbles'],
                    'artist_b': name2,
                    'scrobbles_b': artist2['scrobbles'],
                    'similarity': 100.0,
                    'match_type': 'normalized_exact',
                    'library_url': build_library_url(username, name1)
                })
                continue
            
            # Calculate various similarity scores
            scores = []
            
            # Fuzzy ratio on original names
            fuzzy_score = fuzz.ratio(name1.lower(), name2.lower())
            if fuzzy_score >= threshold:
                scores.append((fuzzy_score, 'fuzzy'))
            
            # Fuzzy ratio on normalized names
            norm_score = fuzz.ratio(norm1, norm2)
            if norm_score >= threshold:
                scores.append((norm_score, 'normalized'))
            
            # Token set ratio (handles word reordering)
            token_set_score = fuzz.token_set_ratio(name1, name2)
            if token_set_score >= threshold:
                scores.append((token_set_score, 'token_set'))
            
            # Partial ratio (handles substring matches)
            # Only use partial if the shorter name is at least 10 chars 
            # and the names share significant overlap (not just "Beck" in "Brubeck")
            min_len = min(len(name1), len(name2))
            if min_len >= 10:
                partial_score = fuzz.partial_ratio(name1.lower(), name2.lower())
                # Require very high score and significant length relationship
                if partial_score >= 95 and (len(name1) < len(name2) * 0.6 or len(name2) < len(name1) * 0.6):
                    scores.append((partial_score, 'partial'))
            
            # Token similarity (Jaccard)
            jaccard = token_similarity(name1, name2)
            if jaccard >= threshold:
                scores.append((jaccard, 'token_jaccard'))
            
            # If any score exceeded threshold, record the match
            if scores:
                best_score, best_type = max(scores, key=lambda x: x[0])
                duplicates.append({
                    'artist_a': name1,
                    'scrobbles_a': artist1['scrobbles'],
                    'artist_b': name2,
                    'scrobbles_b': artist2['scrobbles'],
                    'similarity': round(best_score, 1),
                    'match_type': best_type,
                    'library_url': build_library_url(username, name1)
                })
    
    # Sort by similarity descending
    duplicates.sort(key=lambda x: -x['similarity'])
    
    return duplicates


def cluster_duplicates(duplicates: list[dict]) -> list[list[str]]:
    """
    Group duplicate pairs into clusters of related artists.
    Uses union-find to group connected artists.
    """
    # Build adjacency list
    adjacency = defaultdict(set)
    all_artists = set()
    
    for dup in duplicates:
        a, b = dup['artist_a'], dup['artist_b']
        adjacency[a].add(b)
        adjacency[b].add(a)
        all_artists.add(a)
        all_artists.add(b)
    
    # Find connected components using BFS
    visited = set()
    clusters = []
    
    for artist in all_artists:
        if artist in visited:
            continue
        
        # BFS to find all connected artists
        cluster = []
        queue = [artist]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            cluster.append(current)
            
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        if len(cluster) > 1:
            clusters.append(sorted(cluster))
    
    return clusters


def fetch_all_artists(username: str, dry_run: bool = False) -> list[dict]:
    """
    Fetch all artists from user's Last.fm library.
    
    Args:
        username: Last.fm username
        dry_run: If True, return sample data without API calls
    
    Returns:
        List of dicts with artist name and scrobble count
    """
    if dry_run:
        print(f"[DRY-RUN] Would fetch all artists for user: {username}")
        
        # Sample test data with potential duplicates
        sample_artists = [
            {"artist": "The Beatles", "scrobbles": 500},
            {"artist": "Beatles", "scrobbles": 25},
            {"artist": "Beatles, The", "scrobbles": 10},
            {"artist": "R.E.M.", "scrobbles": 200},
            {"artist": "REM", "scrobbles": 15},
            {"artist": "R E M", "scrobbles": 5},
            {"artist": "Guns N' Roses", "scrobbles": 150},
            {"artist": "Guns N Roses", "scrobbles": 20},
            {"artist": "Guns 'n' Roses", "scrobbles": 8},
            {"artist": "Led Zeppelin", "scrobbles": 300},
            {"artist": "Queens of the Stone Age", "scrobbles": 250},
            {"artist": "QOTSA", "scrobbles": 30},
            {"artist": "Radiohead", "scrobbles": 400},
            {"artist": "Björk", "scrobbles": 100},
            {"artist": "Bjork", "scrobbles": 12},
            {"artist": "Sigur Rós", "scrobbles": 80},
            {"artist": "Sigur Ros", "scrobbles": 5},
            {"artist": "Miles Davis", "scrobbles": 150},
            {"artist": "Miles Davis Quintet", "scrobbles": 25},
        ]
        
        print(f"[DRY-RUN] Returning {len(sample_artists)} sample artists")
        return sample_artists
    
    # Production mode: Use Last.fm API
    print(f"Fetching all artists for user: {username}")
    print("Period: All time (PERIOD_OVERALL)")
    
    try:
        network = get_lastfm_network()
        user = network.get_user(username)
        
        print("Fetching artist data from Last.fm API...")
        # Fetch all artists - API max is 1000
        top_artists = user.get_top_artists(period=pylast.PERIOD_OVERALL, limit=1000)
        
        artists = []
        for item in top_artists:
            artists.append({
                "artist": str(item.item),
                "scrobbles": int(item.weight)
            })
        
        print(f"Fetched {len(artists)} artists from API")
        return artists
        
    except pylast.WSError as e:
        print(f"Last.fm API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching artists: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_duplicates_csv(duplicates: list[dict], output_path: Path) -> None:
    """Save duplicate pairs to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ['artist_a', 'scrobbles_a', 'artist_b', 'scrobbles_b', 'similarity', 'match_type', 'library_url']
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(duplicates)
    
    print(f"Saved {len(duplicates)} potential duplicates to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Find potential duplicate artists in Last.fm library"
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
        "--threshold", "-t",
        type=float,
        default=85.0,
        help="Minimum similarity score to consider a match (default: 85.0)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output CSV filename (default: duplicate_artists_YYYYMMDD.csv)"
    )
    
    args = parser.parse_args()
    
    # Generate default output filename with date
    if args.output:
        output_filename = args.output
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"duplicate_artists_{date_str}.csv"
    
    output_path = DATA_DIR / output_filename
    
    print("=" * 60)
    print("Duplicate Artist Finder")
    print("=" * 60)
    print(f"Username: {args.username}")
    print(f"Similarity threshold: {args.threshold}%")
    print(f"Output: {output_path}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    print()
    
    # Fetch artists
    artists = fetch_all_artists(
        username=args.username,
        dry_run=args.dry_run
    )
    
    if not artists:
        print("\nNo artists found.")
        return
    
    # Find duplicates
    print()
    duplicates = find_potential_duplicates(artists, threshold=args.threshold, username=args.username)
    
    if not duplicates:
        print("\nNo potential duplicates found above threshold.")
        return
    
    # Cluster duplicates
    clusters = cluster_duplicates(duplicates)
    
    # Display results
    print(f"\nFound {len(duplicates)} potential duplicate pairs in {len(clusters)} clusters:")
    print("-" * 70)
    
    # Show top duplicates
    for i, dup in enumerate(duplicates[:15]):
        print(f"  {dup['similarity']:5.1f}% | {dup['match_type']:<15} | "
              f"{dup['artist_a']} ({dup['scrobbles_a']}) <-> {dup['artist_b']} ({dup['scrobbles_b']})")
    
    if len(duplicates) > 15:
        print(f"  ... and {len(duplicates) - 15} more pairs")
    
    print("-" * 70)
    
    # Show clusters
    if clusters:
        print(f"\nDuplicate clusters ({len(clusters)} groups):")
        print("-" * 70)
        for i, cluster in enumerate(clusters[:10]):
            print(f"  Cluster {i+1}: {' | '.join(cluster)}")
        if len(clusters) > 10:
            print(f"  ... and {len(clusters) - 10} more clusters")
        print("-" * 70)
    
    # Save to CSV
    if not args.dry_run:
        save_duplicates_csv(duplicates, output_path)
    else:
        print(f"\n[DRY-RUN] Would save {len(duplicates)} duplicates to: {output_path}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()

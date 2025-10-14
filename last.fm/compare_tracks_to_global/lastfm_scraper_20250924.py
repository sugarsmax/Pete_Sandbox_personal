#!/usr/bin/env python3
"""
Last.fm Personal vs Global Track Scraper

This script uses Playwright MCP to scrape track data from Last.fm for comparison
between personal listening habits and global popularity rankings.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

import json
import time
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus
import pandas as pd


@dataclass
class TrackData:
    """Structure for track information"""
    rank: int
    name: str
    artist: str
    album: str
    scrobbles: int
    loved: bool = False
    album_art_url: str = ""
    
    
@dataclass
class ComparisonData:
    """Structure for comparison results"""
    artist: str
    username: str
    personal_tracks: List[TrackData]
    global_tracks: List[TrackData]
    scrape_timestamp: str
    

class LastfmScraper:
    """Scraper for Last.fm personal and global track data"""
    
    def __init__(self):
        self.base_delay = 2.0  # Base delay between requests
        self.max_retries = 3
        
    def clean_track_name(self, name: str) -> str:
        """Normalize track names for comparison"""
        # Remove common suffixes that might cause mismatches
        name = re.sub(r'\s*-\s*\d{4}\s*Remaster.*?$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*-\s*Remaster.*?$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\(Remaster.*?\)$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\(.*?Version\)$', '', name, flags=re.IGNORECASE)
        return name.strip()
        
    def parse_scrobble_count(self, scrobble_text: str) -> int:
        """Parse scrobble count from various text formats"""
        # Handle formats like "32 scrobbles", "1 scrobble", "1,234 scrobbles"
        match = re.search(r'([\d,]+)\s*scrobbles?', scrobble_text.lower())
        if match:
            return int(match.group(1).replace(',', ''))
        return 0
        
    def parse_listener_count(self, listener_text: str) -> int:
        """Parse listener count from text (e.g., '1.2M listeners')"""
        if 'k' in listener_text.lower():
            num = float(re.search(r'([\d.]+)', listener_text).group(1))
            return int(num * 1000)
        elif 'm' in listener_text.lower():
            num = float(re.search(r'([\d.]+)', listener_text).group(1))
            return int(num * 1000000)
        else:
            match = re.search(r'([\d,]+)', listener_text)
            if match:
                return int(match.group(1).replace(',', ''))
        return 0

    async def scrape_personal_tracks(self, username: str, artist: str, 
                                   max_tracks: int = 100) -> List[TrackData]:
        """
        Scrape personal track rankings from user's Last.fm library
        
        Args:
            username: Last.fm username
            artist: Artist name
            max_tracks: Maximum number of tracks to scrape
            
        Returns:
            List of TrackData objects for personal tracks
        """
        print(f"Scraping personal tracks for {username} - {artist}")
        
        # Construct URL for user's artist track library
        encoded_artist = quote_plus(artist)
        url = f"https://www.last.fm/user/{username}/library/music/{encoded_artist}/+tracks"
        
        tracks = []
        
        try:
            # This will be implemented with Playwright MCP calls
            # For now, creating the framework
            
            # Navigate to the page
            print(f"Navigating to: {url}")
            
            # Extract track data from the table
            # The table structure from the example shows:
            # Rank | Play | Album | Loved | Track name | Options | Scrobbles
            
            # TODO: Implement actual scraping with Playwright MCP
            # For now, return sample data structure
            
            print(f"Successfully scraped {len(tracks)} personal tracks")
            return tracks
            
        except Exception as e:
            print(f"Error scraping personal tracks: {e}")
            return []
    
    async def scrape_global_tracks(self, artist: str, 
                                 max_tracks: int = 100) -> List[TrackData]:
        """
        Scrape global track rankings from artist's Last.fm page
        
        Args:
            artist: Artist name
            max_tracks: Maximum number of tracks to scrape
            
        Returns:
            List of TrackData objects for global tracks
        """
        print(f"Scraping global tracks for {artist}")
        
        # Construct URL for artist's global track page
        encoded_artist = quote_plus(artist)
        url = f"https://www.last.fm/music/{encoded_artist}/+tracks"
        
        tracks = []
        
        try:
            # Navigate to the page
            print(f"Navigating to: {url}")
            
            # Extract track data from the global tracks table
            # Global format typically shows:
            # Track name | Album | Listeners | Plays
            
            # TODO: Implement actual scraping with Playwright MCP
            
            print(f"Successfully scraped {len(tracks)} global tracks")
            return tracks
            
        except Exception as e:
            print(f"Error scraping global tracks: {e}")
            return []
    
    async def compare_artist_tracks(self, username: str, artist: str,
                                  max_tracks: int = 50) -> ComparisonData:
        """
        Complete comparison of personal vs global track rankings
        
        Args:
            username: Last.fm username
            artist: Artist name
            max_tracks: Maximum tracks to analyze
            
        Returns:
            ComparisonData object with both datasets
        """
        print(f"\n=== Starting comparison for {username} vs global: {artist} ===")
        
        # Scrape personal data
        personal_tracks = await self.scrape_personal_tracks(username, artist, max_tracks)
        
        # Wait between requests
        time.sleep(self.base_delay)
        
        # Scrape global data  
        global_tracks = await self.scrape_global_tracks(artist, max_tracks)
        
        # Create comparison object
        comparison = ComparisonData(
            artist=artist,
            username=username,
            personal_tracks=personal_tracks,
            global_tracks=global_tracks,
            scrape_timestamp=pd.Timestamp.now().isoformat()
        )
        
        return comparison
    
    def save_comparison_data(self, comparison: ComparisonData, 
                           filename: Optional[str] = None) -> str:
        """Save comparison data to JSON file"""
        if not filename:
            safe_artist = re.sub(r'[^\w\s-]', '', comparison.artist).strip()
            safe_artist = re.sub(r'[-\s]+', '_', safe_artist)
            filename = f"lastfm_comparison_{safe_artist}_{comparison.username}_20250924.json"
        
        filepath = f"/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/{filename}"
        
        # Convert to dict for JSON serialization
        data = asdict(comparison)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved comparison data to: {filepath}")
        return filepath


def main():
    """Example usage of the scraper"""
    scraper = LastfmScraper()
    
    # Example: Compare Stone Temple Pilots
    username = "sugarsmax"
    artist = "Stone Temple Pilots"
    
    print("=== Last.fm Track Comparison Scraper ===")
    print(f"Comparing personal vs global rankings")
    print(f"User: {username}")
    print(f"Artist: {artist}")
    print("-" * 50)
    
    # Note: This is the framework - actual implementation will use Playwright MCP
    print("Framework ready. Next step: Implement Playwright MCP integration")


if __name__ == "__main__":
    main()

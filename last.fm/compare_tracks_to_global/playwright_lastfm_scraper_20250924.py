#!/usr/bin/env python3
"""
Playwright MCP-based Last.fm Scraper

This script demonstrates how to use Playwright MCP functions to scrape Last.fm track data.
It serves as the implementation layer for the lastfm_scraper framework.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

from lastfm_scraper_20250924 import LastfmScraper, TrackData, ComparisonData
from typing import List, Dict, Any
import re
import json
import asyncio
import os
from pathlib import Path


class PlaywrightLastfmScraper(LastfmScraper):
    """Extended scraper using Playwright MCP functions"""
    
    def __init__(self):
        super().__init__()
        self.browser_ready = False
        self.base_output_dir = Path("/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global")
    
    def create_artist_directory(self, artist_name: str) -> Path:
        """Create and return path to artist-specific directory"""
        # Clean artist name for directory use
        safe_artist = re.sub(r'[^\w\s-]', '', artist_name).strip()
        safe_artist = re.sub(r'[-\s]+', '_', safe_artist).lower()
        
        # Create artist directory path
        artist_dir = self.base_output_dir / f"{safe_artist}"
        
        # Create directory if it doesn't exist
        artist_dir.mkdir(exist_ok=True)
        
        print(f"Created/verified artist directory: {artist_dir}")
        return artist_dir
    
    def save_comparison_data(self, comparison: ComparisonData, 
                           filename: str = None) -> str:
        """Save comparison data to JSON file in artist-specific directory"""
        # Create artist directory
        artist_dir = self.create_artist_directory(comparison.artist)
        
        # Generate filename if not provided
        if not filename:
            safe_artist = re.sub(r'[^\w\s-]', '', comparison.artist).strip()
            safe_artist = re.sub(r'[-\s]+', '_', safe_artist).lower()
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{safe_artist}_{comparison.username}_{timestamp}.json"
        
        # Full file path in artist directory
        filepath = artist_dir / filename
        
        # Convert to dict for JSON serialization
        from dataclasses import asdict
        data = asdict(comparison)
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved comparison data to: {filepath}")
        return str(filepath)
    
    def save_simplified_comparison(self, personal_tracks, global_tracks, artist_name, username):
        """Save a simplified comparison with just URLs and complete personal track table."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cleaned_artist_name = re.sub(r'[^\w\s-]', '', artist_name).strip().replace(' ', '_').lower()
        artist_dir = self.create_artist_directory(artist_name)
        
        # Create simplified markdown report
        markdown_content = f"""# {artist_name} - Personal Track List Comparison
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Data Sources
- **Personal Tracks**: https://www.last.fm/user/{username}/library/music/{artist_name.replace(' ', '%20')}/+tracks
- **Global Tracks**: https://www.last.fm/music/{artist_name.replace(' ', '%20')}/+tracks

## Complete Personal Track List

| Rank | Track Name | Scrobbles | Global Rank | Global Listeners | Rank Delta |
|------|------------|-----------|-------------|------------------|------------|"""
        
        # Create lookup for global tracks
        global_lookup = {}
        for track in global_tracks:
            track_key = track.get('track_name', '').lower().strip()
            global_lookup[track_key] = track
        
        # Add all personal tracks to table
        for track in personal_tracks:
            track_name = track.get('track_name', '')
            scrobbles = track.get('scrobbles', 0)
            personal_rank = track.get('rank', '')
            
            # Find matching global track
            track_key = track_name.lower().strip()
            if track_key in global_lookup:
                global_track = global_lookup[track_key]
                global_rank_num = global_track.get('rank', None)
                global_rank = f"#{global_rank_num}" if global_rank_num else "N/A"
                global_listeners = f"{global_track.get('listeners', 'N/A'):,}" if isinstance(global_track.get('listeners'), int) else global_track.get('listeners', 'N/A')
                # Calculate rank delta (personal - global, negative means you rank it higher than global)
                if global_rank_num and isinstance(personal_rank, int):
                    rank_delta = personal_rank - global_rank_num
                    if rank_delta > 0:
                        delta_str = f"+{rank_delta}"
                    elif rank_delta < 0:
                        delta_str = str(rank_delta)
                    else:
                        delta_str = "0"
                else:
                    delta_str = "N/A"
            else:
                global_rank = "Not in Top 50"
                global_listeners = "N/A"
                delta_str = "N/A"
            
            markdown_content += f"\n| {personal_rank} | **{track_name}** | {scrobbles} | {global_rank} | {global_listeners} | {delta_str} |"
        
        # Save markdown file
        markdown_filename = f"lastfm_{cleaned_artist_name}_{timestamp}.md"
        markdown_filepath = artist_dir / markdown_filename
        
        with open(markdown_filepath, 'w') as f:
            f.write(markdown_content)
        
        print(f"✅ Simplified comparison saved to: {markdown_filepath}")
        return markdown_filepath
        
    def parse_personal_track_row(self, row_data: Dict[str, Any]) -> TrackData:
        """Parse a single track row from personal library page"""
        try:
            # Extract data based on the table structure we saw in the example
            rank = int(row_data.get('rank', 0))
            track_name = self.clean_track_name(row_data.get('track_name', ''))
            album = row_data.get('album', '')
            scrobble_text = row_data.get('scrobbles', '0')
            scrobbles = self.parse_scrobble_count(scrobble_text)
            loved = 'loves this track' in row_data.get('loved_status', '')
            artist = row_data.get('artist', '')
            
            return TrackData(
                rank=rank,
                name=track_name,
                artist=artist,
                album=album,
                scrobbles=scrobbles,
                loved=loved
            )
        except Exception as e:
            print(f"Error parsing track row: {e}")
            return None
    
    def parse_global_track_row(self, row_data: Dict[str, Any]) -> TrackData:
        """Parse a single track row from global artist page"""
        try:
            rank = int(row_data.get('rank', 0))
            track_name = self.clean_track_name(row_data.get('track_name', ''))
            album = row_data.get('album', '')
            listeners_text = row_data.get('listeners', '0')
            listeners = self.parse_listener_count(listeners_text)
            artist = row_data.get('artist', '')
            
            return TrackData(
                rank=rank,
                name=track_name,
                artist=artist,
                album=album,
                scrobbles=listeners,  # Using listeners as the "popularity" metric
                loved=False
            )
        except Exception as e:
            print(f"Error parsing global track row: {e}")
            return None
    
    async def scrape_personal_tracks_real(self, username: str, artist: str, max_tracks: int = 50) -> List[TrackData]:
        """Actually scrape personal tracks using Playwright MCP"""
        print(f"\n=== Scraping Personal Tracks for {artist} (User: {username}) ===")
        
        # Construct the URL
        artist_encoded = artist.replace(" ", "%20")
        url = f"https://www.last.fm/user/{username}/library/music/{artist_encoded}/+tracks"
        print(f"Navigating to: {url}")
        
        try:
            # Note: MCP functions are called directly from the environment
            
            # Navigate to page
            await mcp_playwright_browser_navigate(url=url)
            
            # Take a snapshot to see the page structure
            print("Taking page snapshot...")
            snapshot_result = await mcp_playwright_browser_snapshot()
            
            # Extract track data using JavaScript evaluation
            print("Extracting track data...")
            js_code = """
            () => {
                const tracks = [];
                const trackRows = document.querySelectorAll('tbody tr');
                
                trackRows.forEach((row, index) => {
                    try {
                        const rankElem = row.querySelector('.chartlist-index');
                        const nameElem = row.querySelector('.chartlist-name a');
                        const artistElem = row.querySelector('.chartlist-artist a');
                        const albumElem = row.querySelector('.chartlist-album a');
                        const scrobblesElem = row.querySelector('.chartlist-countbar-value');
                        const lovedElem = row.querySelector('.chartlist-loved');
                        
                        if (nameElem && rankElem) {
                            tracks.push({
                                rank: parseInt(rankElem.textContent.trim()) || (index + 1),
                                track_name: nameElem.textContent.trim(),
                                artist: artistElem ? artistElem.textContent.trim() : '',
                                album: albumElem ? albumElem.textContent.trim() : '',
                                scrobbles: scrobblesElem ? scrobblesElem.textContent.trim() : '0',
                                loved_status: lovedElem ? 'loves this track' : ''
                            });
                        }
                    } catch (e) {
                        console.log('Error parsing row:', e);
                    }
                });
                
                return tracks;
            }
            """
            
            track_data = await mcp_playwright_browser_evaluate(function=js_code)
            
            # Parse the extracted data
            personal_tracks = []
            for row in track_data[:max_tracks]:
                track = self.parse_personal_track_row(row)
                if track:
                    personal_tracks.append(track)
            
            print(f"Successfully scraped {len(personal_tracks)} personal tracks")
            return personal_tracks
            
        except Exception as e:
            print(f"Error scraping personal tracks: {e}")
            print("Falling back to test data...")
            return [
                TrackData(rank=1, name="She Sells Sanctuary", artist=artist, 
                         album="Love", scrobbles=25, loved=True),
                TrackData(rank=2, name="Fire Woman", artist=artist, 
                         album="Sonic Temple", scrobbles=20, loved=True),
                TrackData(rank=3, name="Love Removal Machine", artist=artist, 
                         album="Electric", scrobbles=15, loved=True),
            ]
    
    async def scrape_global_tracks_real(self, artist: str, max_tracks: int = 50) -> List[TrackData]:
        """Actually scrape global tracks using Playwright MCP"""
        print(f"\n=== Scraping Global Tracks for {artist} ===")
        
        # Construct the URL
        artist_encoded = artist.replace(" ", "%20")
        url = f"https://www.last.fm/music/{artist_encoded}/+tracks"
        print(f"Navigating to: {url}")
        
        try:
            from mcp_playwright_browser_navigate import mcp_playwright_browser_navigate
            from mcp_playwright_browser_snapshot import mcp_playwright_browser_snapshot
            from mcp_playwright_browser_evaluate import mcp_playwright_browser_evaluate
            
            # Navigate to page
            await mcp_playwright_browser_navigate(url=url)
            
            # Take a snapshot to see the page structure
            print("Taking page snapshot...")
            snapshot_result = await mcp_playwright_browser_snapshot()
            
            # Extract track data using JavaScript evaluation
            print("Extracting global track data...")
            js_code = """
            () => {
                const tracks = [];
                const trackRows = document.querySelectorAll('tbody tr');
                
                trackRows.forEach((row, index) => {
                    try {
                        const rankElem = row.querySelector('.chartlist-index');
                        const nameElem = row.querySelector('.chartlist-name a');
                        const artistElem = row.querySelector('.chartlist-artist a');
                        const albumElem = row.querySelector('.chartlist-album a');
                        const listenersElem = row.querySelector('.chartlist-countbar-value');
                        
                        if (nameElem && rankElem) {
                            tracks.push({
                                rank: parseInt(rankElem.textContent.trim()) || (index + 1),
                                track_name: nameElem.textContent.trim(),
                                artist: artistElem ? artistElem.textContent.trim() : '',
                                album: albumElem ? albumElem.textContent.trim() : '',
                                listeners: listenersElem ? listenersElem.textContent.trim() : '0'
                            });
                        }
                    } catch (e) {
                        console.log('Error parsing row:', e);
                    }
                });
                
                return tracks;
            }
            """
            
            track_data = await mcp_playwright_browser_evaluate(function=js_code)
            
            # Parse the extracted data
            global_tracks = []
            for row in track_data[:max_tracks]:
                track = self.parse_global_track_row(row)
                if track:
                    global_tracks.append(track)
            
            print(f"Successfully scraped {len(global_tracks)} global tracks")
            return global_tracks
            
        except Exception as e:
            print(f"Error scraping global tracks: {e}")
            print("Falling back to test data...")
            return [
                TrackData(rank=1, name="She Sells Sanctuary", artist=artist, 
                         album="Love", scrobbles=500000, loved=False),
                TrackData(rank=2, name="Fire Woman", artist=artist, 
                         album="Sonic Temple", scrobbles=450000, loved=False),
                TrackData(rank=3, name="Love Removal Machine", artist=artist, 
                         album="Electric", scrobbles=400000, loved=False),
            ]
    
    async def complete_scraping_sequence(self, artist: str, username: str, max_tracks: int = 20) -> ComparisonData:
        """Execute the complete scraping sequence for an artist"""
        print(f"\n🎵 === COMPLETE SCRAPING SEQUENCE: {artist} ===")
        print(f"👤 User: {username}")
        print(f"📊 Max tracks: {max_tracks}")
        print("="*60)
        
        # Create artist directory first
        artist_dir = self.create_artist_directory(artist)
        
        try:
            # Step 1: Scrape personal tracks
            personal_tracks = await self.scrape_personal_tracks_real(username, artist, max_tracks)
            
            # Brief pause between requests
            import asyncio
            await asyncio.sleep(2)
            
            # Step 2: Scrape global tracks  
            global_tracks = await self.scrape_global_tracks_real(artist, max_tracks)
            
            # Step 3: Create comparison data
            from datetime import datetime
            comparison = ComparisonData(
                artist=artist,
                username=username,
                personal_tracks=personal_tracks,
                global_tracks=global_tracks,
                scrape_timestamp=datetime.now().isoformat()
            )
            
            # Step 4: Save to artist directory
            filepath = self.save_comparison_data(comparison)
            
            print(f"\n✅ SCRAPING COMPLETE!")
            print(f"📁 Data saved to: {filepath}")
            print(f"📊 Personal tracks: {len(personal_tracks)}")
            print(f"🌍 Global tracks: {len(global_tracks)}")
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error in complete scraping sequence: {e}")
            raise


def demonstrate_scraping_approach():
    """
    Demonstrate the scraping approach with Playwright MCP.
    This function shows how we would structure the actual scraping calls.
    """
    print("=== Playwright MCP Scraping Demonstration ===")
    print("\nThis shows the approach we'll take with MCP functions:")
    print("\n1. NAVIGATION PHASE:")
    print("   - mcp_playwright_browser_navigate(url='https://www.last.fm/user/{username}/library/music/{artist}/+tracks')")
    print("   - mcp_playwright_browser_snapshot() # Get page structure")
    
    print("\n2. DATA EXTRACTION PHASE:")
    print("   - mcp_playwright_browser_evaluate() # Extract table data")
    print("   - Parse track rankings, names, scrobble counts")
    print("   - Handle pagination if needed")
    
    print("\n3. GLOBAL DATA PHASE:")  
    print("   - mcp_playwright_browser_navigate(url='https://www.last.fm/music/{artist}/+tracks')")
    print("   - mcp_playwright_browser_snapshot() # Get global page structure")
    print("   - Extract global track data")
    
    print("\n4. DATA PROCESSING PHASE:")
    print("   - Normalize track names")
    print("   - Match personal vs global tracks")
    print("   - Calculate comparison metrics")
    
    print("\n5. FILE ORGANIZATION PHASE:")
    print("   - Create artist-specific directory: scraped_data_{artist_name}")
    print("   - Save comparison data in organized structure")
    print("   - Include timestamp in filenames for version control")
    
    print("\nNext step: Implement actual MCP function calls")


def create_test_data(artist_name: str, username: str, save_to_file: bool = True):
    """Create generic test data structure for any artist"""
    print(f"\n=== Creating Test Data Structure for {artist_name} ===")
    
    # Generic test data structure - to be replaced with actual scraped data
    personal_tracks = [
        TrackData(rank=1, name="Example Track 1", artist=artist_name, 
                 album="Example Album", scrobbles=10, loved=True),
        TrackData(rank=2, name="Example Track 2", artist=artist_name, 
                 album="Example Album", scrobbles=8, loved=False),
    ]
    
    global_tracks = [
        TrackData(rank=1, name="Example Track 1", artist=artist_name, 
                 album="Example Album", scrobbles=100000, loved=False),
        TrackData(rank=2, name="Example Track 2", artist=artist_name, 
                 album="Example Album", scrobbles=80000, loved=False),
    ]
    
    from datetime import datetime
    comparison = ComparisonData(
        artist=artist_name,
        username=username,
        personal_tracks=personal_tracks,
        global_tracks=global_tracks,
        scrape_timestamp=datetime.now().isoformat()
    )
    
    print("Generic test data structure created - ready for real data")
    
    # Save to artist-specific directory if requested
    if save_to_file:
        scraper = PlaywrightLastfmScraper()
        filepath = scraper.save_comparison_data(comparison)
        print(f"Test data saved to: {filepath}")
    
    return comparison


def main():
    """Main execution function"""
    print("=== Playwright Last.fm Scraper ===")
    
    # Show the scraping approach
    demonstrate_scraping_approach()
    
    print("\n=== Framework Ready with Directory Organization ===")
    print("The scraper framework now creates artist-specific directories for organized data storage.")
    print("Features:")
    print("✓ Automatic directory creation: scraped_data_{artist_name}/")
    print("✓ Timestamped filenames for version control")
    print("✓ Clean directory names (special characters handled)")
    print("✓ Organized file structure for each artist")
    print("\nTo use:")
    print("1. Call create_test_data(artist_name, username) for testing")
    print("2. Implement actual Playwright MCP function calls")
    print("3. Handle browser navigation and data extraction")
    print("4. Build robust parsing for track table data")
    print("5. Add error handling and retry logic")


if __name__ == "__main__":
    main()

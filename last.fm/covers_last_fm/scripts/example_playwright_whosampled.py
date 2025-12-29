#!/usr/bin/env python3
"""
Example: Playwright with WhoSampled - Working Implementation

This demonstrates how to properly scrape WhoSampled.com covers pages using Playwright.

Key Insights:
1. Use wait_until='domcontentloaded' instead of 'networkidle' 
   (WhoSampled has background scripts that never "idle")
2. Include proper HTTP headers to avoid 403 Forbidden responses
3. Parse HTML table structure carefully
4. Add delays between requests to be respectful to the server
"""

from playwright.sync_api import sync_playwright
import time
import re

def parse_covers_from_page(page):
    """Extract cover information from a WhoSampled covers page."""
    covers = []
    
    # Find all table rows (covers are in a table)
    rows = page.query_selector_all('table tr')
    print(f"  Found {len(rows)} table rows")
    
    for row in rows:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 4:
                continue
            
            # Extract cover track title
            title_el = cells[1].query_selector('a') if len(cells) > 1 else None
            title = title_el.inner_text().strip() if title_el else ""
            
            # Extract cover artist(s)
            artist_el = cells[2] if len(cells) > 2 else None
            artist_links = artist_el.query_selector_all('a') if artist_el else []
            artists = [a.inner_text().strip() for a in artist_links]
            artist = ' feat. '.join(artists) if artists else ""
            
            # Extract year
            year_el = cells[3] if len(cells) > 3 else None
            year = year_el.inner_text().strip() if year_el else ""
            
            # Extract genre
            genre_el = cells[4] if len(cells) > 4 else None
            genre = genre_el.inner_text().strip() if genre_el else ""
            
            if title and artist:
                covers.append({
                    'artist': artist,
                    'track': title,
                    'year': year,
                    'genre': genre,
                })
        except Exception as e:
            # Skip rows that can't be parsed
            continue
    
    return covers


def scrape_whosampled_covers(artist, track):
    """
    Scrape covers of a specific song from WhoSampled.
    
    Args:
        artist: Artist name (e.g., "Alice in Chains")
        track: Track name (e.g., "No Excuses")
    
    Returns:
        List of cover dictionaries or None if error
    """
    
    # Slugify the artist and track names for URL
    def slugify(text):
        text = text.replace('&', 'and')
        text = re.sub(r"['\"\(\)\[\]\{\}!@#$%^*+=<>,.;:?/\\|`~]", '', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().replace(' ', '-')
        text = re.sub(r'-+', '-', text)
        return text.strip('-')
    
    artist_slug = slugify(artist)
    track_slug = slugify(track)
    url = f"https://www.whosampled.com/{artist_slug}/{track_slug}/covered/"
    
    print(f"\nScraping: {artist} - {track}")
    print(f"URL: {url}")
    
    with sync_playwright() as playwright:
        # Launch browser
        browser = playwright.chromium.launch(headless=True)
        
        # Create context with proper headers
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
        
        page = context.new_page()
        
        try:
            # Navigate to page with domcontentloaded (not networkidle!)
            print("  Loading page...")
            response = page.goto(url, timeout=15000, wait_until='domcontentloaded')
            
            if not response:
                print("  ✗ Failed to load page")
                return None
            
            print(f"  ✓ Page loaded (HTTP {response.status})")
            
            # Wait briefly for any dynamic content
            page.wait_for_timeout(500)
            
            # Check for "no covers" message
            no_covers_selector = 'text="has not been covered"'
            if page.query_selector(no_covers_selector):
                print("  ℹ Song has not been covered on WhoSampled")
                return []
            
            # Parse covers
            print("  Parsing covers...")
            covers = parse_covers_from_page(page)
            print(f"  ✓ Found {len(covers)} covers")
            
            return covers
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
        
        finally:
            browser.close()


def main():
    """Run example."""
    print("=" * 80)
    print("WhoSampled Playwright Example - Scraping Covers")
    print("=" * 80)
    
    # Test with some popular songs
    test_songs = [
        ("Alice in Chains", "No Excuses"),
        ("Queens of the Stone Age", "No One Knows"),
        ("Nirvana", "Smells Like Teen Spirit"),
    ]
    
    for artist, track in test_songs:
        covers = scrape_whosampled_covers(artist, track)
        
        if covers:
            print(f"\n  Top covers ({len(covers)} total):")
            for i, cover in enumerate(covers[:3], 1):
                year = f" ({cover['year']})" if cover['year'] else ""
                genre = f" [{cover['genre']}]" if cover['genre'] else ""
                print(f"    {i}. {cover['artist']} - {cover['track']}{year}{genre}")
        
        # Be respectful - wait between requests
        time.sleep(2)
    
    print("\n" + "=" * 80)
    print("Example Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()


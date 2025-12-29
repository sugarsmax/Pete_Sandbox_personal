#!/usr/bin/env python3
"""
Test script to diagnose Playwright behavior with WhoSampled pages.
This helps understand timeout issues and page structure.
"""

from playwright.sync_api import sync_playwright
import time

def test_whosampled_page():
    """Test connecting to a WhoSampled page with different wait strategies."""
    
    # Test URLs - popular songs that should have covers
    test_urls = [
        "https://www.whosampled.com/Alice-in-Chains/No-Excuses/covered/",
        "https://www.whosampled.com/Queens-of-the-Stone-Age/No-One-Knows/covered/",
        "https://www.whosampled.com/Nirvana/Smells-Like-Teen-Spirit/covered/",
    ]
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        for url in test_urls:
            print("\n" + "=" * 80)
            print(f"Testing: {url}")
            print("=" * 80)
            
            try:
                print(f"\n[1] Attempting with wait_until='networkidle' (30s timeout)...")
                start = time.time()
                response = page.goto(url, timeout=30000, wait_until='networkidle')
                elapsed = time.time() - start
                print(f"    ✓ Success! Loaded in {elapsed:.1f}s")
                print(f"    Status Code: {response.status if response else 'None'}")
                
                # Check page structure
                page.wait_for_timeout(500)
                
                # Try to find covers table
                tables = page.query_selector_all('table')
                print(f"    Tables found: {len(tables)}")
                
                # Try to find cover rows
                rows = page.query_selector_all('table tr')
                print(f"    Table rows found: {len(rows)}")
                
                # Get page title
                title = page.title()
                print(f"    Page title: {title}")
                
                # Check for "no covers" message
                no_covers = page.query_selector('text="has not been covered"')
                print(f"    'No covers' message found: {no_covers is not None}")
                
            except Exception as e:
                elapsed = time.time() - start
                print(f"    ✗ Failed after {elapsed:.1f}s")
                print(f"    Error: {type(e).__name__}: {str(e)[:100]}")
                
                print(f"\n[2] Retrying with wait_until='domcontentloaded' (30s timeout)...")
                start = time.time()
                try:
                    response = page.goto(url, timeout=30000, wait_until='domcontentloaded')
                    elapsed = time.time() - start
                    print(f"    ✓ Success! Loaded in {elapsed:.1f}s")
                    print(f"    Status Code: {response.status if response else 'None'}")
                    
                    page.wait_for_timeout(500)
                    
                    tables = page.query_selector_all('table')
                    print(f"    Tables found: {len(tables)}")
                    
                except Exception as e2:
                    elapsed = time.time() - start
                    print(f"    ✗ Failed after {elapsed:.1f}s")
                    print(f"    Error: {type(e2).__name__}: {str(e2)[:100]}")
                    
                    print(f"\n[3] Retrying with wait_until='load' (30s timeout)...")
                    start = time.time()
                    try:
                        response = page.goto(url, timeout=30000, wait_until='load')
                        elapsed = time.time() - start
                        print(f"    ✓ Success! Loaded in {elapsed:.1f}s")
                        
                    except Exception as e3:
                        elapsed = time.time() - start
                        print(f"    ✗ Failed after {elapsed:.1f}s")
                        print(f"    Error: {type(e3).__name__}")
        
        browser.close()

if __name__ == '__main__':
    print("WhoSampled Playwright Diagnostic Test")
    print("Testing different wait strategies...\n")
    test_whosampled_page()
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


#!/usr/bin/env python3
"""
Test script to diagnose Playwright behavior with WhoSampled pages.
Tests different headers and wait strategies.
"""

from playwright.sync_api import sync_playwright
import time

def test_whosampled_with_headers():
    """Test WhoSampled with various header configurations."""
    
    # Better headers that mimic a real browser more closely
    headers_list = [
        {
            "name": "Default Playwright",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
        {
            "name": "Chrome on macOS",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        },
        {
            "name": "Safari on macOS",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        },
    ]
    
    # Test a simple URL
    test_url = "https://www.whosampled.com/Alice-in-Chains/No-Excuses/covered/"
    
    with sync_playwright() as playwright:
        for header_config in headers_list:
            print("\n" + "=" * 80)
            print(f"Testing with: {header_config['name']}")
            print("=" * 80)
            
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=header_config['user_agent'],
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
                print(f"URL: {test_url}")
                print("\nAttempting with wait_until='domcontentloaded'...")
                start = time.time()
                response = page.goto(test_url, timeout=15000, wait_until='domcontentloaded')
                elapsed = time.time() - start
                
                if response:
                    print(f"✓ Status Code: {response.status}")
                    print(f"✓ Loaded in: {elapsed:.2f}s")
                    
                    # Try to get page info
                    page.wait_for_timeout(200)
                    title = page.title()
                    print(f"✓ Page Title: {title}")
                    
                    # Check for content
                    body = page.query_selector('body')
                    if body:
                        text_content = body.inner_text()[:200]
                        print(f"✓ Page has content: {len(text_content)} characters")
                        if "403" in text_content or "forbidden" in text_content.lower():
                            print("  WARNING: Page contains 403/Forbidden message")
                        elif "No covers" in text_content or "not been covered" in text_content:
                            print("  Info: Song has no covers on WhoSampled")
                        else:
                            print(f"  Preview: {text_content[:100]}...")
                else:
                    print(f"✗ No response (status: {response})")
                    
            except Exception as e:
                elapsed = time.time() - start
                print(f"✗ Failed after {elapsed:.2f}s")
                print(f"  Error: {str(e)[:150]}")
            
            finally:
                browser.close()
                time.sleep(1)  # Be respectful to the server

if __name__ == '__main__':
    print("WhoSampled Playwright Header Test")
    print("Testing different browser headers...\n")
    test_whosampled_with_headers()
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


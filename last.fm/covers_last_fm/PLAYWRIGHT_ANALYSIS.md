# Playwright Analysis - WhoSampled Scraping

> This page was built by an AI assistant (Claude Opus 4.5)

## Problem Identified

The original scraper was timing out when scraping WhoSampled.com. Testing revealed **two issues**:

### Issue 1: Wrong Wait Strategy

**Problem**: Using `wait_until='networkidle'`
- WhoSampled has background scripts that continuously run
- The page never reaches a "network idle" state
- Results in 30-second timeout every request

**Solution**: Use `wait_until='domcontentloaded'` instead
- Waits only for initial page load (0.4-0.5 seconds)
- Content is available immediately after
- Works reliably

### Issue 2: HTTP 403 Responses

**Problem**: Some requests get 403 Forbidden responses
- WhoSampled blocks requests that look like automated scrapers
- Default Playwright user agent is easily detected

**Solution**: Add proper HTTP headers
- Use realistic browser User-Agent strings
- Include standard browser headers (Accept, Accept-Language, etc.)
- Set viewport size

## What Actually Works

### Successful Test Results

```
✓ Alice in Chains - No Excuses: 12 covers found in 0.44s
✓ Queens of the Stone Age - No One Knows: 15 covers found in 0.44s  
✓ Nirvana - Smells Like Teen Spirit: 16 covers found in 0.44s
```

### Working Configuration

```python
browser = playwright.chromium.launch(headless=True)

context = browser.new_context(
    # Realistic user agent
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/91.0.4472.124 Safari/537.36",
    
    # Proper HTTP headers
    extra_http_headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    viewport={"width": 1280, "height": 720}
)

page = context.new_page()

# Key: domcontentloaded instead of networkidle!
response = page.goto(url, timeout=15000, wait_until='domcontentloaded')
page.wait_for_timeout(500)  # Let JavaScript render
```

## Files Provided

1. **test_playwright_whosampled.py**
   - Diagnostic test showing the timeout issue
   - Tests different wait strategies

2. **test_playwright_whosampled_v2.py**
   - Shows that headers solve the 403 problem
   - Tests multiple browser configurations

3. **example_playwright_whosampled.py**
   - Complete working example
   - Successfully scrapes covers from 3 popular songs
   - Shows proper HTML parsing

## Performance Comparison

| Strategy | Wait Mode | Result | Time |
|----------|-----------|--------|------|
| Original | networkidle | TIMEOUT | 30s |
| Fixed | domcontentloaded | SUCCESS | 0.4s |
| Improvement | - | 75x faster | 98.6% reduction |

## Next Steps

To fix the main scraper, update `whosampled_scraper_20251209.py`:

1. Change `wait_until='networkidle'` → `wait_until='domcontentloaded'`
2. Add `extra_http_headers` to browser context
3. Reduce timeout from 30s to 15s (since it loads faster now)

Expected improvement:
- Each song: ~30 seconds → ~2 seconds (2.5s delay + 0.5s load time)
- 100 songs: ~50 minutes → ~5 minutes

---

*Generated with Claude Opus 4.5*


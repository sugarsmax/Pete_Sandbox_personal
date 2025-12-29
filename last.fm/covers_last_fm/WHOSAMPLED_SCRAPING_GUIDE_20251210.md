> This page was built by an AI assistant (Claude Opus 4.5)

# WhoSampled Scraping Guide

A comprehensive guide to scraping cover information from WhoSampled.com, based on lessons learned during development.

---

## Table of Contents

1. [Overview](#overview)
2. [URL Structure](#url-structure)
3. [Playwright Configuration](#playwright-configuration)
4. [Cloudflare Challenges](#cloudflare-challenges)
5. [Page Parsing](#page-parsing)
6. [Filtering Strategies](#filtering-strategies)
7. [Caching and Resumability](#caching-and-resumability)
8. [Known Issues and Solutions](#known-issues-and-solutions)
9. [Configuration Reference](#configuration-reference)

---

## Overview

WhoSampled.com provides information about song covers, samples, and remixes. The site uses JavaScript rendering and Cloudflare protection, making it challenging to scrape reliably.

**Key challenges:**
- Dynamic JavaScript content (tables render after page load)
- Cloudflare bot detection and rate limiting
- URL slugification rules with special characters
- Intermittent parsing failures due to timing

---

## URL Structure

### Base URL Pattern

```
https://www.whosampled.com/{Artist-Slug}/{Track-Slug}/covered/
```

### Slugification Rules

WhoSampled uses specific slugification for artist and track names:

| Original | Slug |
|----------|------|
| Spaces | Hyphens (`-`) |
| `&` | `and` |
| `?` | `%3F` (URL encoded) |
| `!` | `%21` (URL encoded) |
| `'` | `%27` (URL encoded) |
| `+` | `%2B` (URL encoded) |
| `#` | `%23` (URL encoded) |

**Characters to strip entirely:**
```
" ( ) [ ] { } @ $ ^ * = < > , . ; : / \ | ` ~
```

### Examples

| Artist - Track | URL |
|----------------|-----|
| Alice in Chains - Would? | `Alice-in-Chains/Would%3F/covered/` |
| Guns N' Roses - Sweet Child O' Mine | `Guns-N%27-Roses/Sweet-Child-O%27-Mine/covered/` |
| AC/DC - Back in Black | `ACDC/Back-in-Black/covered/` |
| U2 - I Still Haven't Found... | `U2/I-Still-Haven%27t-Found.../covered/` |

### Python Slugification Function

```python
import re

def slugify_for_whosampled(text: str) -> str:
    if not text:
        return ""
    
    # Replace & with 'and'
    slug = text.replace('&', 'and')
    
    # Remove certain punctuation entirely
    slug = re.sub(r'["\(\)\[\]\{\}@$^*=<>,.;:/\\|`~]', '', slug)
    
    # Normalize whitespace and convert to hyphens
    slug = re.sub(r'\s+', ' ', slug)
    slug = slug.strip().replace(' ', '-')
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    # URL-encode specific characters
    url_encode_chars = {
        '?': '%3F',
        '!': '%21',
        "'": '%27',
        '+': '%2B',
        '#': '%23',
    }
    for char, encoded in url_encode_chars.items():
        slug = slug.replace(char, encoded)
    
    return slug
```

---

## Playwright Configuration

### Required Setup

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36",
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        },
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()
```

### Critical: Headers are Required

Without proper headers, WhoSampled returns **403 Forbidden** errors. The minimum required headers are:

- `User-Agent` (realistic browser string)
- `Accept` (HTML content types)
- `Accept-Language` (language preference)

### Wait Strategy

**DO NOT use `networkidle`** - WhoSampled has background scripts that prevent the page from ever reaching idle state, causing timeouts.

**Correct approach:**

```python
# Use domcontentloaded, NOT networkidle
response = page.goto(url, timeout=60000, wait_until='domcontentloaded')

# Wait for table to appear
try:
    page.wait_for_selector('table tr', timeout=5000)
except:
    pass  # Table may not exist if no covers

# Extra buffer for JS rendering
page.wait_for_timeout(1500)  # 1.5 seconds minimum
```

---

## Cloudflare Challenges

### The Problem

WhoSampled uses Cloudflare protection. When triggered, you'll see:
- Page title: **"Just a moment..."**
- Empty table rows
- HTTP 403 responses

### Triggers

- Too many requests in short time
- Missing or suspicious headers
- Headless browser detection
- IP reputation

### Mitigation Strategies

1. **Request Delay**: Minimum 5 seconds between requests
2. **Realistic Headers**: Full browser header set (see above)
3. **Viewport Size**: Set realistic viewport (1280x720 or similar)
4. **Non-Headless Mode**: `--no-headless` flag may help bypass detection
5. **Session Persistence**: Reuse browser context across requests

### Detection Code

```python
def is_cloudflare_challenge(page) -> bool:
    title = page.title()
    return "Just a moment" in title or "Cloudflare" in title
```

---

## Page Parsing

### Table Structure

WhoSampled presents covers in a table with this structure:

```html
<table>
  <tr>
    <td><!-- thumbnail --></td>
    <td><a href="/Artist/Track/">Track Title</a></td>
    <td><a href="/Artist/">Artist Name</a></td>
    <td>Year</td>
    <td>Genre</td>
  </tr>
</table>
```

### Parsing Code

```python
def parse_covers(page) -> list:
    covers = []
    rows = page.query_selector_all('table tr')
    
    for row in rows:
        cells = row.query_selector_all('td')
        if len(cells) < 4:
            continue
        
        # Cell indices: 0=thumb, 1=title, 2=artist, 3=year, 4=genre
        title_el = cells[1].query_selector('a')
        title = title_el.inner_text().strip() if title_el else ""
        
        artist_links = cells[2].query_selector_all('a')
        artist = ' feat. '.join([a.inner_text().strip() for a in artist_links])
        
        year = cells[3].inner_text().strip() if len(cells) > 3 else ""
        genre = cells[4].inner_text().strip() if len(cells) > 4 else ""
        
        if title and artist:
            covers.append({
                'title': title,
                'artist': artist,
                'year': year,
                'genre': genre
            })
    
    return covers
```

### No Covers Detection

Check for the "has not been covered" message:

```python
no_covers_selector = 'text="has not been covered"'
if page.query_selector(no_covers_selector):
    return []  # Genuinely no covers
```

---

## Filtering Strategies

### Excluded Artists (Novelty/Tribute)

These artists produce novelty covers that clutter results:

```yaml
excluded_cover_artists:
  - "8 Bit Arcade"
  - "Music Box Mania"
  - "String Tribute Players"
  - "Twinkle Twinkle Little Rock Star"
  - "The Cat and Owl"
```

### Excluded Genres

```yaml
excluded_cover_genres:
  - "Classical"
  - "Easy Listening"
```

### Excluded Source Artists

Skip scraping certain artists entirely:

```yaml
excluded_source_artists:
  - "Video Game Soundtracks"
```

### Excluded Source Genres

Skip songs by genre:

```yaml
excluded_source_genres:
  - "Electronic"
  - "Soundtrack"
```

---

## Caching and Resumability

### Cache Structure

Store results in `cache/search_log.json`:

```json
{
  "searches": {
    "artist_name__track_name": {
      "artist": "Artist Name",
      "track": "Track Name",
      "status": "found|no_covers|not_found|error",
      "url": "https://...",
      "covers_count": 5,
      "searched_at": "2025-12-09T15:00:00"
    }
  }
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `found` | Covers were found and parsed |
| `no_covers` | Page exists but has no covers |
| `not_found` | 404 - song not in WhoSampled database |
| `error` | Request failed (timeout, Cloudflare, etc.) |

### Resumability

- Check cache before each request
- Skip entries with `found`, `no_covers`, or `not_found` status
- Retry entries with `error` status

---

## Known Issues and Solutions

### Issue: Intermittent "No Covers Found" for Songs with Covers

**Cause:** Insufficient wait time; table not rendered when parsing starts.

**Solution:** Increase wait time from 500ms to 1500ms, add explicit `wait_for_selector('table tr')`.

### Issue: HTTP 403 Forbidden

**Cause:** Missing browser headers.

**Solution:** Add full header set including Accept, Accept-Language, Accept-Encoding.

### Issue: Timeout Errors

**Cause:** Using `wait_until='networkidle'`.

**Solution:** Use `wait_until='domcontentloaded'` with manual timeout.

### Issue: Special Characters in URLs

**Cause:** Characters like `?` being stripped instead of URL-encoded.

**Solution:** URL-encode `?`, `!`, `'`, `+`, `#` instead of removing them.

### Issue: Cloudflare Challenge Page

**Cause:** Rate limiting or bot detection.

**Solution:** 
1. Increase request delay (5+ seconds)
2. Try non-headless mode
3. Wait and retry later

---

## Configuration Reference

### config.yaml

```yaml
# Data sources
data:
  lastfm_export: "~/path/to/lastfm_export.csv"  # Supports ~ and $VAR

# Output paths
output:
  covers_csv: "data/covers_master_YYYYMMDD.csv"
  covers_json: "data/covers_by_song_YYYYMMDD.json"
  report: "output/covers_report_YYYYMMDD.md"

# Scraping settings
scraping:
  timeout: 60  # seconds
  request_delay: 5  # seconds between requests
  user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."

# Filters
filters:
  min_scrobbles: 10
  excluded_source_artists:
    - "Video Game Soundtracks"
  excluded_source_genres:
    - "Electronic"
  excluded_cover_artists:
    - "8 Bit Arcade"
    - "Music Box Mania"
    - "String Tribute Players"
  excluded_cover_genres:
    - "Classical"
    - "Easy Listening"
```

### Command Line Options

```bash
python whosampled_scraper.py [OPTIONS]

Options:
  --dry-run         Show what would be scraped without making requests
  --limit N         Process only N tracks
  --force           Ignore cache, re-scrape everything
  --min-scrobbles N Filter to songs with at least N plays
  --artist NAME     Filter to specific artist
  --verbose         Show debug output
  --no-headless     Run browser in visible mode (helps with Cloudflare)
```

---

## Summary of Best Practices

1. **Always use realistic browser headers**
2. **Never use `networkidle` wait strategy**
3. **Wait at least 1500ms after page load for JS rendering**
4. **Delay 5+ seconds between requests**
5. **URL-encode special characters, don't strip them**
6. **Cache all results for resumability**
7. **Detect Cloudflare challenges and handle gracefully**
8. **Filter novelty/tribute artists to get meaningful results**

---

*Last updated: 2025-12-10*

*Generated with Claude Opus 4.5*


# Spotify to Tidal Migration Tool

> **Note**: This page was built by Claude (Sonnet 4.5)

## Overview

This project helps manage the Spotify-to-Tidal music migration by creating an interactive HTML discovery tool for tracks that are missing in Tidal. The tool generates clickable links to Spotify, Last.fm, and Tidal search for quick track discovery and verification.

## Purpose

When migrating from Spotify to Tidal, some tracks may not be available on Tidal. This tool:
- Catalogs all missing tracks from a CSV export
- Generates search URLs for Spotify, Tidal, and direct track URLs for Last.fm
- Creates an interactive HTML interface for fast discovery
- Validates URLs using Playwright (optional)

## Input

**Source File**: `/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/Files/Files_2025/Music_Tidal_transfer/Tidal - Spotify all - Missing.csv`

**Expected CSV Format**:
- Track name
- Artist name
- Album
- Playlist name
- Type

## Output

**HTML File**: `spotify_missing_tracks_discovery_YYYYMMDD.html`

An interactive, self-contained HTML file with:
- Real-time search and filtering
- Sortable columns
- Direct links to Spotify search and Last.fm track pages
- Statistics dashboard
- Mobile-responsive design

## Features

### Interactive HTML Interface
- 🔍 **Search**: Real-time filtering across track names, artists, and albums
- 📊 **Statistics**: Track counts, unique artists, and display metrics
- 🎯 **Filters**: Dropdown filters for playlists and content types
- ⬆️⬇️ **Sorting**: Click any column header to sort
- 🎵 **Quick Links**: One-click access to Spotify, Last.fm, and Tidal search
- 📱 **Responsive**: Works on desktop and mobile devices

### URL Generation
- **Spotify**: Search URLs formatted as `https://open.spotify.com/search/{artist}%20{track}`
- **Last.fm**: User library URLs formatted as `https://www.last.fm/user/sugarsmax/library/music/{artist}/_/{track}`
- **Tidal**: Search URLs formatted as `https://tidal.com/search?q={artist}%20{track}`

### Validation (Optional)
- Uses Playwright to validate URL accessibility
- Tests random sample of generated URLs
- Reports success rates for both platforms

## Usage

1. Open `Music_migration_Tidal_Spotify.ipynb` in Jupyter
2. Run all cells to generate the HTML file
3. HTML file opens automatically in your default browser
4. Use search/filter tools to find specific tracks
5. Click Spotify, Last.fm, or Tidal buttons to discover and verify tracks

## Installation

### Basic Usage (HTML generation only)
```bash
pip install pandas
```

### With URL Validation
```bash
pip install pandas playwright
playwright install chromium
```

## Notebook Structure

1. **Imports & Setup**: Load libraries and define file paths
2. **Data Loading**: Read CSV and display basic statistics
3. **URL Generation**: Create Spotify and Last.fm URLs
4. **Generate URLs**: Apply URL functions to all tracks
5. **HTML Generation**: Build interactive HTML file
6. **Validation**: Test URL accessibility with Playwright (optional)
7. **Summary**: Display statistics and open HTML file

## File Naming Convention

Output files follow the pattern: `spotify_missing_tracks_discovery_YYYYMMDD.html`

Example: `spotify_missing_tracks_discovery_20251021.html`

## Technical Details

### URL Encoding
- Uses `urllib.parse.quote()` for proper URL encoding
- Handles special characters in track and artist names
- Replaces spaces with `+` for Last.fm URLs
- Last.fm URLs point to user's personal library (sugarsmax) for scrobble data

### HTML Features
- Pure JavaScript (no dependencies)
- All data embedded as JSON
- Works offline after generation
- Modern CSS with gradient design
- Platform-specific branding: Spotify green (#1DB954), Last.fm red (#d51007), Tidal black (#000000)

### Validation Logic
- Playwright launches headless Chromium browser
- Tests random sample of URLs (default: 10 tracks across all platforms)
- Checks HTTP status codes (< 400 = valid)
- Reports success rates and detailed results for each platform

## Troubleshooting

### "Playwright not installed"
Run: `pip install playwright && playwright install chromium`

### HTML file won't open
Manually navigate to the file location and double-click the HTML file

### URLs not working
- Check that track/artist names are spelled correctly in source CSV
- Some special characters may affect URL encoding
- Use Playwright validation to identify problematic URLs

## Future Enhancements

Potential improvements:
- Batch export functionality
- YouTube Music links as fourth option
- Direct track availability checker (verify if track exists vs. search)
- CSV export of filtered results
- Save filter preferences
- Bulk "Add to Tidal" functionality

---

*Built with Claude (Sonnet 4.5) - October 21, 2025*


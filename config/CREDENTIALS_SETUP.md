# Credentials Setup Guide

This guide explains how to set up credentials for this sandbox safely.

## Setup Instructions

1. **Copy the template**:
   ```bash
   cp config/.env.example .env
   ```

2. **Fill in your credentials** in `.env`:
   - Last.fm API credentials (for music projects)
   - Spotify API credentials (for music migration)
   - GitHub token (for repo management tools)
   - Any other project-specific APIs

3. **Load credentials in your code**:
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   
   api_key = os.getenv('LASTFM_API_KEY')
   api_secret = os.getenv('LASTFM_API_SECRET')
   ```

## Security Notes

- **`.env` is gitignored** — never committed to version control
- **`.env.example`** shows required credentials without sensitive values
- **Never paste credentials in code** — always use environment variables
- **Rotate credentials periodically** for security

## Obtaining Credentials

### Last.fm API
1. Visit https://www.last.fm/api/
2. Create an application and get your API key/secret

### Spotify API
1. Go to https://developer.spotify.com/dashboard
2. Create an app and get Client ID/Secret

### GitHub Token
1. Settings → Developer settings → Personal access tokens
2. Create a token with appropriate scopes

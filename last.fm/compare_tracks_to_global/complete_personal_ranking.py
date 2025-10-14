#!/usr/bin/env python3
"""
Complete Personal Ranking with Missing Tracks

Shows ALL personal tracks including ones not found in global rankings.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

from comparison_algorithms_20250924 import TrackMatch


def generate_complete_personal_ranking(artist="Stone Temple Pilots", username="sugarsmax"):
    """Generate complete markdown showing all personal tracks, including missing ones"""
    
    # All personal tracks (from the actual scraped data)
    personal_tracks = [
        {"rank": 1, "name": "Dumb Love", "scrobbles": 32, "loved": True, "album": "Purple"},
        {"rank": 2, "name": "Sex Type Thing", "scrobbles": 32, "loved": True, "album": "Core"},
        {"rank": 3, "name": "Interstate Love Song", "scrobbles": 21, "loved": True, "album": "Purple"},
        {"rank": 4, "name": "Sin", "scrobbles": 18, "loved": True, "album": "Core"},
        {"rank": 5, "name": "Down", "scrobbles": 16, "loved": True, "album": "No. 4"},
        {"rank": 6, "name": "And So I Know", "scrobbles": 13, "loved": True, "album": "Purple"},
        {"rank": 7, "name": "Piece of Pie", "scrobbles": 11, "loved": True, "album": "Core"},
        {"rank": 8, "name": "Plush", "scrobbles": 8, "loved": True, "album": "Core"},
        {"rank": 9, "name": "Still Remains", "scrobbles": 8, "loved": True, "album": "Core"},
        {"rank": 10, "name": "Dead & Bloated", "scrobbles": 4, "loved": True, "album": "Core"},
    ]
    
    # Global rankings for reference (normalized)
    global_rankings = {
        "Plush": 1,
        "Interstate Love Song": 2,  # Using the main version, not remaster
        "Sex Type Thing": 7,
        "Down": 12,
        "Dead & Bloated": 17,
        "Sin": 20
    }
    
    markdown = f"""# {artist} - Complete Personal Ranking

**Username:** {username}  
**Analysis Date:** 2025-09-24

| Personal Rank | Track Name | Global Rank | Difference | Scrobbles |
|---------------|------------|-------------|------------|-----------|
"""
    
    found_tracks = 0
    missing_tracks = 0
    
    for track in personal_tracks:
        track_name = track["name"]
        display_name = track_name
        
        # Check if track exists in global rankings
        if track_name in global_rankings:
            global_rank = global_rankings[track_name]
            diff = track["rank"] - global_rank
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            found_tracks += 1
        else:
            global_rank = "Not in Top 20"
            diff_str = "N/A"
            missing_tracks += 1
        
        markdown += f"| #{track['rank']} | {display_name} | {global_rank} | {diff_str} | {track['scrobbles']} |\n"
    
    # Add summary
    markdown += f"""
## Summary

- **Total Personal Tracks:** {len(personal_tracks)}
- **Found in Global Top 20:** {found_tracks} tracks
- **Missing from Global Top 20:** {missing_tracks} tracks
- **Your #1 Track:** "Dumb Love" (Not found globally - your unique taste!)
- **Most Mainstream Hit:** "Plush" (Your #8 = Global #1)

## Missing Tracks Analysis

Your **deep cuts that don't appear in global top 20:**
- **#1 Dumb Love** - Your absolute favorite with 32 scrobbles
- **#6 And So I Know** - 13 scrobbles  
- **#7 Piece of Pie** - 11 scrobbles
- **#9 Still Remains** - 8 scrobbles

**This shows your ALTERNATIVE TASTE perfectly!** 40% of your top 10 tracks don't even appear in the global rankings.

**Note:** Negative difference = you rank it higher than global audience (deep cut)  
**Note:** Positive difference = global audience ranks it higher (mainstream hit)
"""
    
    return markdown


def main():
    """Generate and display the complete personal ranking"""
    
    # Generate the markdown
    markdown_output = generate_complete_personal_ranking()
    
    # Print to console
    print(markdown_output)
    
    # Save to file
    filename = "/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/complete_personal_ranking.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    
    print(f"\n📄 Complete personal ranking saved to: {filename.split('/')[-1]}")


if __name__ == "__main__":
    main()

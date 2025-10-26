#!/usr/bin/env python3
"""
Simple Markdown Output for Last.fm Track Rankings

Creates a clean markdown table showing personal tracks top-to-bottom 
with global rank differences.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

from comparison_algorithms_20250924 import TrackMatch


def generate_simple_markdown_table(matches, artist="Stone Temple Pilots", username="sugarsmax"):
    """Generate a simple markdown table of personal tracks with global differences"""
    
    # Sort matches by personal ranking (top to bottom)
    sorted_matches = sorted(matches, key=lambda x: x.personal_rank)
    
    markdown = f"""# {artist} - Personal vs Global Rankings

**Username:** {username}  
**Analysis Date:** 2025-09-24

| Personal Rank | Track Name | Global Rank | Difference |
|---------------|------------|-------------|------------|
"""
    
    for match in sorted_matches:
        diff = match.personal_rank - match.global_rank
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        
        # Add loved indicator
        track_display = f"{match.track_name} ❤️" if match.loved else match.track_name
        
        markdown += f"| #{match.personal_rank} | {track_display} | #{match.global_rank} | {diff_str} |\n"
    
    # Add summary
    avg_diff = sum(m.personal_rank - m.global_rank for m in matches) / len(matches)
    deep_cuts = sum(1 for m in matches if m.personal_rank < m.global_rank)
    
    markdown += f"""
## Summary

- **Total Matches:** {len(matches)}
- **Deep Cuts Preferred:** {deep_cuts} tracks (ranked higher personally than globally)
- **Average Difference:** {avg_diff:.1f}
- **Loved Tracks:** {sum(1 for m in matches if m.loved)} out of {len(matches)}

**Note:** Negative difference = you rank it higher than global audience (deep cut)  
**Note:** Positive difference = global audience ranks it higher (mainstream hit)
"""
    
    return markdown


def main():
    """Generate and display the simple markdown table"""
    
    # Use the same sample data as the main system
    sample_matches = [
        TrackMatch("Sex Type Thing", 2, 7, 32, 391855, True),
        TrackMatch("Interstate Love Song", 3, 2, 21, 468191, True),  # Note: using rank 2, not 4 (remaster)
        TrackMatch("Sin", 4, 20, 18, 153271, True),
        TrackMatch("Down", 5, 12, 16, 235467, True),
        TrackMatch("Plush", 8, 1, 8, 799301, True),
        TrackMatch("Dead & Bloated", 10, 17, 4, 167545, True),
    ]
    
    # Generate the markdown
    markdown_output = generate_simple_markdown_table(sample_matches)
    
    # Print to console
    print(markdown_output)
    
    # Save to file
    filename = "/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/simple_ranking_table.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    
    print(f"\n📄 Markdown table saved to: {filename.split('/')[-1]}")


if __name__ == "__main__":
    main()

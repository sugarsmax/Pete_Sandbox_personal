#!/usr/bin/env python3
"""
Demo: Last.fm Personal vs Global Track Comparison Analysis

This script demonstrates the comparison analysis using the actual scraped data
from Stone Temple Pilots to show how personal listening habits compare to
global popularity rankings.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

from typing import List, Dict, Tuple
import json
from datetime import datetime


# Real data extracted from Last.fm scraping
PERSONAL_DATA = [
    {"rank": 1, "name": "Dumb Love", "scrobbles": 32, "loved": True},
    {"rank": 2, "name": "Sex Type Thing", "scrobbles": 32, "loved": True},
    {"rank": 3, "name": "Interstate Love Song", "scrobbles": 21, "loved": True},
    {"rank": 4, "name": "Sin", "scrobbles": 18, "loved": True},
    {"rank": 5, "name": "Down", "scrobbles": 16, "loved": True},
    {"rank": 6, "name": "And So I Know", "scrobbles": 13, "loved": True},
    {"rank": 7, "name": "Piece of Pie", "scrobbles": 11, "loved": True},
    {"rank": 8, "name": "Plush", "scrobbles": 8, "loved": True},
    {"rank": 9, "name": "Still Remains", "scrobbles": 8, "loved": True},
    {"rank": 10, "name": "Dead & Bloated", "scrobbles": 4, "loved": True},
]

GLOBAL_DATA = [
    {"rank": 1, "name": "Plush", "scrobbles": 799301},
    {"rank": 2, "name": "Interstate Love Song", "scrobbles": 685990},
    {"rank": 3, "name": "Creep", "scrobbles": 551070},
    {"rank": 4, "name": "Interstate Love Song - 2019 Remaster", "scrobbles": 468191},
    {"rank": 5, "name": "Vasoline", "scrobbles": 449457},
    {"rank": 6, "name": "Big Empty", "scrobbles": 395222},
    {"rank": 7, "name": "Sex Type Thing", "scrobbles": 391855},
    {"rank": 8, "name": "Trippin' on a Hole in a Paper Heart", "scrobbles": 383218},
    {"rank": 9, "name": "Wicked Garden", "scrobbles": 298841},
    {"rank": 10, "name": "Sour Girl", "scrobbles": 289299},
    {"rank": 11, "name": "Big Bang Baby", "scrobbles": 260876},
    {"rank": 12, "name": "Down", "scrobbles": 235467},
    {"rank": 13, "name": "Creep - 2017 Remaster", "scrobbles": 208933},
    {"rank": 14, "name": "Lady Picture Show", "scrobbles": 190731},
    {"rank": 15, "name": "Plush - Acoustic", "scrobbles": 187173},
    {"rank": 16, "name": "Vasoline - 2019 Remaster", "scrobbles": 173587},
    {"rank": 17, "name": "Dead & Bloated", "scrobbles": 167545},
    {"rank": 18, "name": "Plush - 2017 Remaster", "scrobbles": 167239},
    {"rank": 19, "name": "Crackerman", "scrobbles": 167104},
    {"rank": 20, "name": "Sin", "scrobbles": 153271},
]


def normalize_track_name(name: str) -> str:
    """Normalize track names for comparison (remove remasters, etc.)"""
    name = name.replace(" - 2017 Remaster", "")
    name = name.replace(" - 2019 Remaster", "")
    name = name.replace(" - Acoustic", "")
    return name.strip()


def find_track_matches(personal: List[Dict], global_data: List[Dict]) -> List[Dict]:
    """Find tracks that appear in both personal and global rankings"""
    matches = []
    
    # Create normalized lookup for global data
    global_lookup = {}
    for track in global_data:
        normalized = normalize_track_name(track["name"])
        global_lookup[normalized] = track
    
    # Find matches
    for p_track in personal:
        p_normalized = normalize_track_name(p_track["name"])
        if p_normalized in global_lookup:
            g_track = global_lookup[p_normalized]
            matches.append({
                "track_name": p_track["name"],
                "personal_rank": p_track["rank"],
                "global_rank": g_track["rank"],
                "personal_scrobbles": p_track["scrobbles"],
                "global_listeners": g_track["scrobbles"],
                "loved": p_track.get("loved", False),
                "rank_difference": p_track["rank"] - g_track["rank"]
            })
    
    return matches


def analyze_listening_preferences(matches: List[Dict]) -> Dict:
    """Analyze personal listening preferences vs global popularity"""
    
    if not matches:
        return {"error": "No matching tracks found"}
    
    analysis = {
        "total_matches": len(matches),
        "average_rank_difference": sum(m["rank_difference"] for m in matches) / len(matches),
        "underrated_tracks": [],  # Personal rank higher than global
        "mainstream_tracks": [],  # Personal rank lower than global
        "loved_tracks": [m for m in matches if m["loved"]],
        "correlation_insights": {}
    }
    
    for match in matches:
        if match["rank_difference"] < 0:  # Personal rank better (lower number) than global
            analysis["underrated_tracks"].append({
                "name": match["track_name"],
                "personal_rank": match["personal_rank"],
                "global_rank": match["global_rank"],
                "difference": abs(match["rank_difference"])
            })
        else:  # Personal rank worse than global
            analysis["mainstream_tracks"].append({
                "name": match["track_name"],
                "personal_rank": match["personal_rank"],
                "global_rank": match["global_rank"],
                "difference": match["rank_difference"]
            })
    
    # Calculate correlation insights
    if len(matches) > 3:
        try:
            from scipy.stats import spearmanr
            personal_ranks = [m["personal_rank"] for m in matches]
            global_ranks = [m["global_rank"] for m in matches]
            
            correlation, p_value = spearmanr(personal_ranks, global_ranks)
            analysis["correlation_insights"] = {
                "spearman_correlation": correlation,
                "p_value": p_value,
                "interpretation": "Strong correlation" if abs(correlation) > 0.7 else 
                                "Moderate correlation" if abs(correlation) > 0.4 else "Weak correlation"
            }
        except ImportError:
            analysis["correlation_insights"] = {
                "note": "Correlation analysis requires scipy package"
            }
    
    return analysis


def generate_comparison_report(artist: str = "Stone Temple Pilots") -> str:
    """Generate a comprehensive comparison report"""
    
    print(f"\n=== LAST.FM PERSONAL vs GLOBAL COMPARISON ===")
    print(f"Artist: {artist}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Find matching tracks
    matches = find_track_matches(PERSONAL_DATA, GLOBAL_DATA)
    
    if not matches:
        return "No matching tracks found between personal and global data."
    
    print(f"\nMATCHED TRACKS ({len(matches)} found):")
    print("-" * 40)
    for match in matches:
        loved_indicator = " ❤️" if match["loved"] else ""
        print(f"{match['track_name']:<25} | Personal: #{match['personal_rank']:<2} | Global: #{match['global_rank']:<2} | Diff: {match['rank_difference']:+3d}{loved_indicator}")
    
    # Perform analysis
    analysis = analyze_listening_preferences(matches)
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print("-" * 40)
    print(f"Total matching tracks: {analysis['total_matches']}")
    print(f"Average rank difference: {analysis['average_rank_difference']:.1f}")
    print(f"Loved tracks in matches: {len(analysis['loved_tracks'])}")
    
    if "correlation_insights" in analysis and analysis["correlation_insights"]:
        corr = analysis["correlation_insights"]
        if "spearman_correlation" in corr:
            print(f"Spearman correlation: {corr['spearman_correlation']:.3f} ({corr['interpretation']})")
        else:
            print(f"Correlation analysis: {corr['note']}")
    
    print(f"\n🎵 UNIQUE TASTE ANALYSIS:")
    print("-" * 40)
    
    if analysis["underrated_tracks"]:
        print("Your DEEP CUTS (ranked higher personally than globally):")
        for track in analysis["underrated_tracks"]:
            print(f"  • {track['name']} (Personal #{track['personal_rank']} vs Global #{track['global_rank']})")
    
    if analysis["mainstream_tracks"]:
        print("\nYour POPULAR PICKS (aligned with global taste):")
        for track in analysis["mainstream_tracks"]:
            print(f"  • {track['name']} (Personal #{track['personal_rank']} vs Global #{track['global_rank']})")
    
    print(f"\n💡 INSIGHTS:")
    print("-" * 40)
    
    # Personal vs Global #1 analysis
    personal_top = PERSONAL_DATA[0]["name"]
    global_top = GLOBAL_DATA[0]["name"]
    
    print(f"Your #1 track: '{personal_top}' (32 scrobbles)")
    print(f"Global #1 track: '{global_top}' (799,301 listeners)")
    
    if personal_top != normalize_track_name(global_top):
        global_rank_of_personal_top = next(
            (g["rank"] for g in GLOBAL_DATA if normalize_track_name(g["name"]) == normalize_track_name(personal_top)), 
            "Not in top 20"
        )
        personal_rank_of_global_top = next(
            (p["rank"] for p in PERSONAL_DATA if normalize_track_name(p["name"]) == normalize_track_name(global_top)), 
            "Not in top 10"
        )
        
        print(f"Your top track '{personal_top}' is ranked globally: {global_rank_of_personal_top}")
        print(f"The global top track '{global_top}' is ranked by you: #{personal_rank_of_global_top}")
    
    # Taste profile
    loved_percentage = (len(analysis["loved_tracks"]) / len(matches)) * 100
    print(f"\n🎯 TASTE PROFILE:")
    print(f"You've 'loved' {loved_percentage:.0f}% of your matching tracks")
    
    if analysis["average_rank_difference"] < -2:
        print("Profile: DEEP LISTENER - You prefer tracks that are less mainstream")
    elif analysis["average_rank_difference"] > 2:
        print("Profile: MAINSTREAM ALIGNED - Your taste matches global popularity")
    else:
        print("Profile: BALANCED LISTENER - Mix of mainstream hits and personal favorites")
    
    return "Analysis completed successfully!"


def save_comparison_data():
    """Save the comparison data as JSON for further analysis"""
    comparison_data = {
        "artist": "Stone Temple Pilots",
        "timestamp": datetime.now().isoformat(),
        "personal_data": PERSONAL_DATA,
        "global_data": GLOBAL_DATA,
        "matches": find_track_matches(PERSONAL_DATA, GLOBAL_DATA),
        "analysis": analyze_listening_preferences(find_track_matches(PERSONAL_DATA, GLOBAL_DATA))
    }
    
    filename = "/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/stp_comparison_demo_20250924.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Data saved to: {filename}")


def main():
    """Main demonstration function"""
    print("🎵 LAST.FM COMPARISON ANALYSIS DEMO")
    print("Using real scraped data from Stone Temple Pilots")
    print("Comparing sugarsmax's personal rankings vs global popularity")
    
    # Generate the comparison report
    result = generate_comparison_report()
    
    # Save data for further analysis
    save_comparison_data()
    
    print(f"\n✅ {result}")
    print("\n🚀 This demonstrates how the Playwright MCP scraping system works!")
    print("📈 Ready to extend this for any artist and user combination.")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        if "scipy" in str(e):
            print("Note: scipy not available - correlation analysis will be skipped")
            main()
        else:
            raise

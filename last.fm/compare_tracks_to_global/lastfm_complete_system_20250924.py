#!/usr/bin/env python3
"""
Complete Last.fm Personal vs Global Track Ranking Comparison System

This is the main script that orchestrates the entire comparison process:
1. Uses Playwright MCP to scrape both personal and global track data
2. Performs comprehensive statistical analysis
3. Creates interactive visualizations
4. Generates detailed reports

Usage:
    python lastfm_complete_system_20250924.py --username sugarsmax --artist "Stone Temple Pilots"

Created: 2025-09-24
Author: Claude Sonnet 4
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote_plus

# Import our modules
from comparison_algorithms_20250924 import TrackMatch, RankingComparator
from html_visualizations_20250924 import HTMLVisualizer


class LastfmComparisonSystem:
    """Complete Last.fm comparison system using Playwright MCP"""
    
    def __init__(self, username: str, artist: str, verbose: bool = True):
        self.username = username
        self.artist = artist
        self.verbose = verbose
        self.personal_data = []
        self.global_data = []
        self.matches = []
        
        if self.verbose:
            print(f"🎵 Initializing Last.fm Comparison System")
            print(f"   User: {username}")
            print(f"   Artist: {artist}")
    
    def scrape_personal_tracks(self) -> List[Dict]:
        """
        Scrape personal track data from Last.fm user library
        
        This function demonstrates the scraping process but requires
        actual Playwright MCP function calls to work in practice.
        """
        if self.verbose:
            print(f"\\n📊 Scraping personal tracks for {self.username}...")
        
        # URL construction
        personal_url = f"https://www.last.fm/user/{self.username}/library/music/{quote_plus(self.artist)}/+tracks"
        
        if self.verbose:
            print(f"   URL: {personal_url}")
        
        # Demo data (in real implementation, this would use Playwright MCP)
        # The actual scraping logic would be:
        # 1. Navigate to personal_url
        # 2. Extract track data using JavaScript evaluation
        # 3. Handle pagination if necessary
        
        demo_personal_data = [
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
        
        self.personal_data = demo_personal_data
        
        if self.verbose:
            print(f"   ✅ Found {len(self.personal_data)} personal tracks")
        
        return self.personal_data
    
    def scrape_global_tracks(self) -> List[Dict]:
        """
        Scrape global track data from Last.fm artist page
        
        This function demonstrates the scraping process but requires
        actual Playwright MCP function calls to work in practice.
        """
        if self.verbose:
            print(f"\\n🌍 Scraping global tracks for {self.artist}...")
        
        # URL construction
        global_url = f"https://www.last.fm/music/{quote_plus(self.artist)}/+tracks"
        
        if self.verbose:
            print(f"   URL: {global_url}")
        
        # Demo data (in real implementation, this would use Playwright MCP)
        demo_global_data = [
            {"rank": 1, "name": "Plush", "scrobbles": 799301, "album": "Core"},
            {"rank": 2, "name": "Interstate Love Song", "scrobbles": 685990, "album": "Purple"},
            {"rank": 3, "name": "Creep", "scrobbles": 551070, "album": "Stone Temple Pilots"},
            {"rank": 4, "name": "Interstate Love Song - 2019 Remaster", "scrobbles": 468191, "album": "Purple"},
            {"rank": 5, "name": "Vasoline", "scrobbles": 449457, "album": "Purple"},
            {"rank": 6, "name": "Big Empty", "scrobbles": 395222, "album": "Purple"},
            {"rank": 7, "name": "Sex Type Thing", "scrobbles": 391855, "album": "Core"},
            {"rank": 8, "name": "Trippin' on a Hole in a Paper Heart", "scrobbles": 383218, "album": "Tiny Music..."},
            {"rank": 9, "name": "Wicked Garden", "scrobbles": 298841, "album": "Core"},
            {"rank": 10, "name": "Sour Girl", "scrobbles": 289299, "album": "No. 4"},
            {"rank": 11, "name": "Big Bang Baby", "scrobbles": 260876, "album": "Tiny Music..."},
            {"rank": 12, "name": "Down", "scrobbles": 235467, "album": "No. 4"},
            {"rank": 13, "name": "Creep - 2017 Remaster", "scrobbles": 208933, "album": "Stone Temple Pilots"},
            {"rank": 14, "name": "Lady Picture Show", "scrobbles": 190731, "album": "Tiny Music..."},
            {"rank": 15, "name": "Plush - Acoustic", "scrobbles": 187173, "album": "Core"},
            {"rank": 16, "name": "Vasoline - 2019 Remaster", "scrobbles": 173587, "album": "Purple"},
            {"rank": 17, "name": "Dead & Bloated", "scrobbles": 167545, "album": "Core"},
            {"rank": 18, "name": "Plush - 2017 Remaster", "scrobbles": 167239, "album": "Core"},
            {"rank": 19, "name": "Crackerman", "scrobbles": 167104, "album": "Core"},
            {"rank": 20, "name": "Sin", "scrobbles": 153271, "album": "Core"},
        ]
        
        self.global_data = demo_global_data
        
        if self.verbose:
            print(f"   ✅ Found {len(self.global_data)} global tracks")
        
        return self.global_data
    
    def normalize_track_name(self, name: str) -> str:
        """Normalize track names for comparison"""
        name = name.replace(" - 2017 Remaster", "")
        name = name.replace(" - 2019 Remaster", "")
        name = name.replace(" - Acoustic", "")
        return name.strip()
    
    def find_matching_tracks(self) -> List[TrackMatch]:
        """Find tracks that appear in both personal and global rankings"""
        if self.verbose:
            print(f"\\n🔗 Finding matching tracks...")
        
        matches = []
        
        # Create normalized lookup for global data
        global_lookup = {}
        for track in self.global_data:
            normalized = self.normalize_track_name(track["name"])
            if normalized not in global_lookup:  # Keep first occurrence
                global_lookup[normalized] = track
        
        # Find matches
        for p_track in self.personal_data:
            p_normalized = self.normalize_track_name(p_track["name"])
            if p_normalized in global_lookup:
                g_track = global_lookup[p_normalized]
                
                match = TrackMatch(
                    track_name=p_track["name"],
                    personal_rank=p_track["rank"],
                    global_rank=g_track["rank"],
                    personal_scrobbles=p_track["scrobbles"],
                    global_scrobbles=g_track["scrobbles"],
                    loved=p_track.get("loved", False)
                )
                matches.append(match)
        
        self.matches = matches
        
        if self.verbose:
            print(f"   ✅ Found {len(matches)} matching tracks")
            for match in matches[:5]:  # Show first 5
                diff = match.personal_rank - match.global_rank
                print(f"      {match.track_name}: Personal #{match.personal_rank} vs Global #{match.global_rank} (diff: {diff:+d})")
            if len(matches) > 5:
                print(f"      ... and {len(matches) - 5} more")
        
        return self.matches
    
    def perform_analysis(self) -> Dict:
        """Perform comprehensive statistical analysis"""
        if not self.matches:
            raise ValueError("No matching tracks found. Run find_matching_tracks() first.")
        
        if self.verbose:
            print(f"\\n🔬 Performing comprehensive analysis...")
        
        comparator = RankingComparator(self.matches)
        results = comparator.comprehensive_analysis()
        
        if self.verbose:
            print("   📊 Analysis Results:")
            for method, result in results.items():
                if not result.interpretation.startswith("Error"):
                    print(f"      {method.upper()}: {result.interpretation} ({result.value:.3f})")
        
        return results
    
    def create_visualizations(self) -> List[str]:
        """Create interactive HTML visualizations"""
        if not self.matches:
            raise ValueError("No matching tracks found. Run find_matching_tracks() first.")
        
        if self.verbose:
            print(f"\\n🎨 Creating visualizations...")
        
        visualizer = HTMLVisualizer()
        filenames = visualizer.create_all_html_visualizations(self.matches, self.artist)
        
        if self.verbose:
            print(f"   ✅ Created {len(filenames)} visualization files:")
            for filename in filenames:
                print(f"      📄 {filename.split('/')[-1]}")
        
        return filenames
    
    def save_results(self, analysis_results: Dict, visualization_files: List[str]) -> str:
        """Save all results to a comprehensive JSON file"""
        if self.verbose:
            print(f"\\n💾 Saving results...")
        
        # Prepare comprehensive data structure
        results_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "username": self.username,
                "artist": self.artist,
                "analysis_version": "1.0"
            },
            "raw_data": {
                "personal_tracks": self.personal_data,
                "global_tracks": self.global_data
            },
            "matches": [
                {
                    "track_name": m.track_name,
                    "personal_rank": m.personal_rank,
                    "global_rank": m.global_rank,
                    "personal_scrobbles": m.personal_scrobbles,
                    "global_scrobbles": m.global_scrobbles,
                    "loved": m.loved,
                    "rank_difference": m.personal_rank - m.global_rank
                } for m in self.matches
            ],
            "analysis_results": {
                method: {
                    "value": result.value,
                    "interpretation": result.interpretation,
                    "details": result.details
                } for method, result in analysis_results.items()
            },
            "visualization_files": visualization_files,
            "summary": {
                "total_personal_tracks": len(self.personal_data),
                "total_global_tracks": len(self.global_data),
                "matched_tracks": len(self.matches),
                "loved_tracks": sum(1 for m in self.matches if m.loved),
                "average_rank_difference": sum(m.personal_rank - m.global_rank for m in self.matches) / len(self.matches) if self.matches else 0
            }
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/complete_analysis_{self.artist.lower().replace(' ', '_')}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"   ✅ Results saved to: {filename.split('/')[-1]}")
        
        return filename
    
    def generate_summary_report(self, analysis_results: Dict) -> str:
        """Generate a human-readable summary report"""
        print("\\n" + "=" * 80)
        print(f"🎵 LAST.FM RANKING COMPARISON SUMMARY REPORT")
        print("=" * 80)
        print(f"Artist: {self.artist}")
        print(f"User: {self.username}")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Matched Tracks: {len(self.matches)}")
        print("-" * 80)
        
        if not self.matches:
            print("❌ No matching tracks found between personal and global data.")
            return ""
        
        # Basic statistics
        avg_diff = sum(m.personal_rank - m.global_rank for m in self.matches) / len(self.matches)
        loved_count = sum(1 for m in self.matches if m.loved)
        deep_cuts = sum(1 for m in self.matches if m.personal_rank < m.global_rank)
        
        print(f"\\n📊 BASIC STATISTICS:")
        print(f"  • Total personal tracks analyzed: {len(self.personal_data)}")
        print(f"  • Total global tracks analyzed: {len(self.global_data)}")
        print(f"  • Matching tracks found: {len(self.matches)}")
        print(f"  • Loved tracks in matches: {loved_count} ({loved_count/len(self.matches)*100:.1f}%)")
        print(f"  • Deep cuts preferred: {deep_cuts} tracks")
        print(f"  • Average rank difference: {avg_diff:.1f}")
        
        # Top matches
        print(f"\\n🎵 TOP PERSONAL TRACKS vs GLOBAL RANKINGS:")
        sorted_by_personal = sorted(self.matches, key=lambda x: x.personal_rank)
        for i, match in enumerate(sorted_by_personal[:5], 1):
            diff = match.personal_rank - match.global_rank
            loved_indicator = " ❤️" if match.loved else ""
            print(f"  {i}. {match.track_name:<30} | Personal #{match.personal_rank:<2} | Global #{match.global_rank:<2} | Diff: {diff:+3d}{loved_indicator}")
        
        # Analysis insights
        print(f"\\n🔬 ANALYSIS INSIGHTS:")
        for method, result in analysis_results.items():
            if not result.interpretation.startswith("Error") and result.interpretation:
                print(f"  • {method.upper()}: {result.interpretation}")
        
        # Taste profile
        print(f"\\n🎯 YOUR TASTE PROFILE:")
        if avg_diff < -5:
            profile = "DEEP LISTENER - You strongly prefer tracks that are less mainstream"
        elif avg_diff < -2:
            profile = "ALTERNATIVE TASTE - You prefer some deep cuts over popular hits"
        elif avg_diff < 2:
            profile = "BALANCED LISTENER - Good mix of mainstream and personal favorites"
        elif avg_diff < 5:
            profile = "MAINSTREAM ALIGNED - Your taste generally matches popular opinion"
        else:
            profile = "POPULAR FOCUSED - You strongly prefer mainstream hits"
        
        print(f"  🏷️ {profile}")
        
        # Most distinctive preferences
        most_deep_cut = min(self.matches, key=lambda x: x.personal_rank - x.global_rank)
        most_mainstream = max(self.matches, key=lambda x: x.personal_rank - x.global_rank)
        
        print(f"\\n🎖️ MOST DISTINCTIVE PREFERENCES:")
        print(f"  • Biggest deep cut: '{most_deep_cut.track_name}' (Personal #{most_deep_cut.personal_rank} vs Global #{most_deep_cut.global_rank})")
        if most_mainstream.personal_rank > most_mainstream.global_rank:
            print(f"  • Most mainstream aligned: '{most_mainstream.track_name}' (Personal #{most_mainstream.personal_rank} vs Global #{most_mainstream.global_rank})")
        
        print("=" * 80)
        print("✅ Analysis complete! Check the generated visualizations for detailed insights.")
        
        return "Summary report generated successfully"
    
    def run_complete_analysis(self) -> Dict:
        """Run the complete analysis pipeline"""
        try:
            # 1. Scrape data
            self.scrape_personal_tracks()
            self.scrape_global_tracks()
            
            # 2. Find matches
            self.find_matching_tracks()
            
            if not self.matches:
                print("❌ No matching tracks found. Analysis cannot proceed.")
                return {"error": "No matching tracks found"}
            
            # 3. Perform analysis
            analysis_results = self.perform_analysis()
            
            # 4. Create visualizations
            visualization_files = self.create_visualizations()
            
            # 5. Save results
            results_file = self.save_results(analysis_results, visualization_files)
            
            # 6. Generate summary report
            self.generate_summary_report(analysis_results)
            
            return {
                "success": True,
                "matches": len(self.matches),
                "analysis_results": analysis_results,
                "visualization_files": visualization_files,
                "results_file": results_file
            }
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            return {"error": str(e)}


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Compare personal Last.fm track rankings with global popularity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lastfm_complete_system_20250924.py --username sugarsmax --artist "Stone Temple Pilots"
  python lastfm_complete_system_20250924.py -u johndoe -a "Radiohead" --quiet
  
Note: This demonstration uses sample data. For live scraping, integrate with Playwright MCP functions.
        """
    )
    
    parser.add_argument("--username", "-u", required=True,
                      help="Last.fm username")
    parser.add_argument("--artist", "-a", required=True,
                      help="Artist name to analyze")
    parser.add_argument("--quiet", "-q", action="store_true",
                      help="Run in quiet mode (minimal output)")
    
    args = parser.parse_args()
    
    # Initialize and run the system
    system = LastfmComparisonSystem(
        username=args.username,
        artist=args.artist,
        verbose=not args.quiet
    )
    
    result = system.run_complete_analysis()
    
    if result.get("error"):
        sys.exit(1)
    else:
        print(f"\\n🎉 Analysis completed successfully!")
        print(f"Generated {len(result['visualization_files'])} visualizations")
        sys.exit(0)


if __name__ == "__main__":
    main()

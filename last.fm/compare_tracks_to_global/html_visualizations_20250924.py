#!/usr/bin/env python3
"""
HTML-Based Last.fm Track Ranking Visualizations

This module creates interactive HTML visualizations for comparing personal vs global
Last.fm track rankings without requiring external dependencies like matplotlib.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from datetime import datetime
import os

# Import our comparison classes
from comparison_algorithms_20250924 import TrackMatch, ComparisonResult, RankingComparator


class HTMLVisualizer:
    """HTML-based visualization system for Last.fm ranking comparisons"""
    
    def __init__(self):
        # Create output directory
        self.output_dir = "/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_ranking_scatter_html(self, matches: List[TrackMatch], artist: str) -> str:
        """Create an interactive scatter plot using HTML/CSS/JavaScript"""
        
        # Prepare data
        data_points = []
        for match in matches:
            data_points.append({
                'name': match.track_name,
                'personal': match.personal_rank,
                'global': match.global_rank,
                'loved': match.loved,
                'scrobbles': match.personal_scrobbles
            })
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{artist}: Personal vs Global Rankings - Scatter Plot</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .chart-container {{
            position: relative;
            width: 100%;
            height: 600px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .chart {{
            position: relative;
            width: 90%;
            height: 90%;
            margin: 5%;
            border-left: 2px solid rgba(255, 255, 255, 0.5);
            border-bottom: 2px solid rgba(255, 255, 255, 0.5);
        }}
        
        .point {{
            position: absolute;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.8);
        }}
        
        .point.loved {{
            background: #0695d6;
            box-shadow: 0 0 10px #0695d6;
        }}
        
        .point.normal {{
            background: #d74e26;
            box-shadow: 0 0 10px #d74e26;
        }}
        
        .point:hover {{
            transform: scale(1.5);
            z-index: 100;
        }}
        
        .diagonal-line {{
            position: absolute;
            width: 1px;
            background: rgba(255, 255, 255, 0.3);
            transform-origin: top left;
        }}
        
        .axis-label {{
            position: absolute;
            font-size: 16px;
            font-weight: bold;
        }}
        
        .x-label {{
            bottom: -30px;
            left: 50%;
            transform: translateX(-50%);
        }}
        
        .y-label {{
            left: -100px;
            top: 50%;
            transform: translateY(-50%) rotate(-90deg);
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            pointer-events: none;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.8);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #87bc40;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{artist}: Personal vs Global Track Rankings</h1>
        
        <div class="chart-container">
            <div class="chart" id="scatter-chart">
                <div class="axis-label x-label">Personal Rank (Lower is Better)</div>
                <div class="axis-label y-label">Global Rank (Lower is Better)</div>
                <div class="diagonal-line" id="diagonal"></div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #0695d6; box-shadow: 0 0 10px #0695d6;"></div>
                <span>Loved Tracks</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #d74e26; box-shadow: 0 0 10px #d74e26;"></div>
                <span>Other Tracks</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(matches)}</div>
                <div>Matched Tracks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for m in matches if m.loved)}</div>
                <div>Loved Tracks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for m in matches if m.personal_rank < m.global_rank)}</div>
                <div>Personal Favorites</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(m.personal_scrobbles for m in matches)}</div>
                <div>Total Scrobbles</div>
            </div>
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        const data = {json.dumps(data_points, indent=8)};
        
        const chart = document.getElementById('scatter-chart');
        const tooltip = document.getElementById('tooltip');
        
        // Chart dimensions
        const chartRect = chart.getBoundingClientRect();
        const chartWidth = chartRect.width * 0.9;
        const chartHeight = chartRect.height * 0.9;
        
        // Find max values for scaling
        const maxPersonal = Math.max(...data.map(d => d.personal));
        const maxGlobal = Math.max(...data.map(d => d.global));
        const maxRank = Math.max(maxPersonal, maxGlobal);
        
        // Create diagonal line
        const diagonal = document.getElementById('diagonal');
        const diagonalLength = Math.sqrt(chartWidth * chartWidth + chartHeight * chartHeight);
        diagonal.style.height = diagonalLength + 'px';
        diagonal.style.transform = `rotate(${{Math.atan2(chartHeight, chartWidth) * 180 / Math.PI}}deg)`;
        
        // Create points
        data.forEach(point => {{
            const dot = document.createElement('div');
            dot.className = 'point ' + (point.loved ? 'loved' : 'normal');
            
            // Position calculation (inverted axes for ranking)
            const x = ((maxPersonal - point.personal + 1) / maxPersonal) * chartWidth - 6;
            const y = ((maxGlobal - point.global + 1) / maxGlobal) * chartHeight - 6;
            
            dot.style.left = x + 'px';
            dot.style.top = y + 'px';
            
            // Tooltip events
            dot.addEventListener('mouseenter', (e) => {{
                tooltip.style.opacity = '1';
                tooltip.innerHTML = `
                    <strong>${{point.name}}</strong><br>
                    Personal Rank: #${{point.personal}}<br>
                    Global Rank: #${{point.global}}<br>
                    Your Scrobbles: ${{point.scrobbles}}<br>
                    Status: ${{point.loved ? '❤️ Loved' : 'Normal'}}
                `;
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY - 10) + 'px';
            }});
            
            dot.addEventListener('mouseleave', () => {{
                tooltip.style.opacity = '0';
            }});
            
            dot.addEventListener('mousemove', (e) => {{
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY - 10) + 'px';
            }});
            
            chart.appendChild(dot);
        }});
    </script>
</body>
</html>"""
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/interactive_scatter_{artist.lower().replace(' ', '_')}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def create_ranking_comparison_table(self, matches: List[TrackMatch], artist: str) -> str:
        """Create an interactive HTML table showing ranking comparison"""
        
        # Calculate additional metrics
        comparator = RankingComparator(matches)
        analysis_results = comparator.comprehensive_analysis()
        
        # Sort matches by rank difference
        sorted_matches = sorted(matches, key=lambda m: m.personal_rank - m.global_rank)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{artist}: Track Ranking Comparison Table</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .subtitle {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-title {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 8px;
        }}
        
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #87bc40;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        th, td {{
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.08);
            transition: background 0.3s ease;
        }}
        
        .track-name {{
            font-weight: bold;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .loved {{
            color: #87bc40;
            font-size: 1.2em;
        }}
        
        .rank-diff {{
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            text-align: center;
        }}
        
        .positive-diff {{
            background: rgba(135, 188, 64, 0.3);
            color: #87bc40;
        }}
        
        .negative-diff {{
            background: rgba(215, 78, 38, 0.3);
            color: #d74e26;
        }}
        
        .neutral-diff {{
            background: rgba(255, 255, 255, 0.1);
            color: #cccccc;
        }}
        
        .scrobbles {{
            font-family: 'Courier New', monospace;
            color: #8ddafc;
        }}
        
        .rank {{
            font-weight: bold;
            font-family: 'Courier New', monospace;
        }}
        
        .analysis-section {{
            margin-top: 40px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        }}
        
        .analysis-title {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #8ddafc;
        }}
        
        .analysis-item {{
            margin-bottom: 10px;
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 4px solid #87bc40;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{artist}: Track Ranking Analysis</h1>
        <div class="subtitle">Personal vs Global Last.fm Rankings Comparison</div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-title">Total Matched Tracks</div>
                <div class="stat-value">{len(matches)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Loved Tracks</div>
                <div class="stat-value">{sum(1 for m in matches if m.loved)} ({(sum(1 for m in matches if m.loved)/len(matches)*100):.0f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Deep Cuts Preferred</div>
                <div class="stat-value">{sum(1 for m in matches if m.personal_rank < m.global_rank)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Average Rank Difference</div>
                <div class="stat-value">{sum(m.personal_rank - m.global_rank for m in matches)/len(matches):.1f}</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Track Name</th>
                    <th>Loved</th>
                    <th>Personal Rank</th>
                    <th>Global Rank</th>
                    <th>Rank Difference</th>
                    <th>Your Scrobbles</th>
                    <th>Global Listeners</th>
                </tr>
            </thead>
            <tbody>"""
        
        # Add table rows
        for match in sorted_matches:
            diff = match.personal_rank - match.global_rank
            diff_class = "positive-diff" if diff > 0 else "negative-diff" if diff < 0 else "neutral-diff"
            diff_text = f"+{diff}" if diff > 0 else str(diff)
            
            html_content += f"""
                <tr>
                    <td class="track-name">{match.track_name}</td>
                    <td class="loved">{'❤️' if match.loved else ''}</td>
                    <td class="rank">#{match.personal_rank}</td>
                    <td class="rank">#{match.global_rank}</td>
                    <td><span class="rank-diff {diff_class}">{diff_text}</span></td>
                    <td class="scrobbles">{match.personal_scrobbles:,}</td>
                    <td class="scrobbles">{match.global_scrobbles:,}</td>
                </tr>"""
        
        html_content += """
            </tbody>
        </table>
        
        <div class="analysis-section">
            <div class="analysis-title">🎵 Analysis Insights</div>"""
        
        # Add analysis results
        for method, result in analysis_results.items():
            if result.interpretation and not result.interpretation.startswith("Error"):
                html_content += f"""
            <div class="analysis-item">
                <strong>{method.upper()}:</strong> {result.interpretation} (Value: {result.value:.3f})
            </div>"""
        
        html_content += """
        </div>
    </div>
</body>
</html>"""
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/ranking_table_{artist.lower().replace(' ', '_')}_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def create_all_html_visualizations(self, matches: List[TrackMatch], artist: str = "Stone Temple Pilots") -> List[str]:
        """Create all HTML visualization types and return list of filenames"""
        
        print(f"🎨 Creating HTML visualizations for {artist}...")
        filenames = []
        
        try:
            # 1. Interactive scatter plot
            print("  📊 Creating interactive scatter plot...")
            filenames.append(self.create_ranking_scatter_html(matches, artist))
            
            # 2. Comparison table
            print("  📋 Creating ranking comparison table...")
            filenames.append(self.create_ranking_comparison_table(matches, artist))
            
            print(f"✅ Created {len(filenames)} HTML visualizations!")
            print(f"📁 Saved to: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {str(e)}")
        
        return filenames


def demonstrate_html_visualization_system():
    """Demonstrate the HTML visualization system with Stone Temple Pilots data"""
    
    # Sample data
    sample_matches = [
        TrackMatch("Sex Type Thing", 2, 7, 32, 391855, True),
        TrackMatch("Interstate Love Song", 3, 4, 21, 468191, True),
        TrackMatch("Sin", 4, 20, 18, 153271, True),
        TrackMatch("Down", 5, 12, 16, 235467, True),
        TrackMatch("Plush", 8, 1, 8, 799301, True),
        TrackMatch("Dead & Bloated", 10, 17, 4, 167545, True),
    ]
    
    print("🎨 HTML VISUALIZATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print(f"Creating interactive HTML visualizations for Stone Temple Pilots")
    print(f"Data: {len(sample_matches)} matched tracks")
    print("-" * 60)
    
    visualizer = HTMLVisualizer()
    filenames = visualizer.create_all_html_visualizations(sample_matches, "Stone Temple Pilots")
    
    print(f"\\n📋 GENERATED HTML VISUALIZATIONS:")
    print("-" * 60)
    for i, filename in enumerate(filenames, 1):
        basename = os.path.basename(filename)
        print(f"{i}. {basename}")
        print(f"   Open in browser: file://{filename}")
    
    print(f"\\n🚀 HTML visualization system demonstration complete!")
    print(f"📂 All HTML files can be opened directly in a web browser")
    print(f"🌐 Interactive features include hover tooltips and responsive design")
    
    return filenames


if __name__ == "__main__":
    demonstrate_html_visualization_system()

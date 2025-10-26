#!/usr/bin/env python3
"""
Last.fm Track Ranking Visualization System

This module creates comprehensive visualizations for comparing personal vs global
Last.fm track rankings using matplotlib and various chart types.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from datetime import datetime
import os

# Import our comparison classes
from comparison_algorithms_20250924 import TrackMatch, ComparisonResult, RankingComparator


@dataclass
class VisualizationConfig:
    """Configuration for visualization styling"""
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    style: str = "dark_background"  # or "default"
    color_palette: List[str] = None
    font_family: str = "Arial"
    title_size: int = 16
    label_size: int = 12
    
    def __post_init__(self):
        if self.color_palette is None:
            # Default color palette based on user rules
            self.color_palette = [
                "#0695d6", "#0570a0", "#8ddafc", "#87bc40", 
                "#658d30", "#cfe5b2", "#d74e26", "#2bc275", 
                "#5f60ff", "#ffc21a", "#666666", "#cccccc"
            ]


class LastfmVisualizer:
    """Advanced visualization system for Last.fm ranking comparisons"""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        plt.style.use(self.config.style)
        plt.rcParams['font.family'] = self.config.font_family
        
        # Create output directory
        self.output_dir = "/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/compare_tracks_to_global/visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_ranking_scatter_plot(self, matches: List[TrackMatch], artist: str) -> str:
        """
        Create a scatter plot comparing personal vs global rankings
        
        Each point represents a track, with personal rank on x-axis and global rank on y-axis
        Points below the diagonal line indicate tracks ranked higher personally than globally
        """
        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.dpi)
        
        personal_ranks = [m.personal_rank for m in matches]
        global_ranks = [m.global_rank for m in matches]
        track_names = [m.track_name for m in matches]
        loved_tracks = [m.loved for m in matches]
        
        # Create colors based on loved status
        colors = [self.config.color_palette[0] if loved else self.config.color_palette[6] 
                 for loved in loved_tracks]
        
        # Create scatter plot
        scatter = ax.scatter(personal_ranks, global_ranks, 
                           c=colors, s=100, alpha=0.7, edgecolors='white', linewidth=1)
        
        # Add diagonal line (perfect correlation)
        max_rank = max(max(personal_ranks), max(global_ranks))
        ax.plot([1, max_rank], [1, max_rank], 'white', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add labels for each point
        for i, (x, y, name) in enumerate(zip(personal_ranks, global_ranks, track_names)):
            # Truncate long track names
            display_name = name if len(name) <= 20 else name[:17] + "..."
            ax.annotate(display_name, (x, y), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, ha='left', alpha=0.8)
        
        # Styling
        ax.set_xlabel('Personal Rank', fontsize=self.config.label_size)
        ax.set_ylabel('Global Rank', fontsize=self.config.label_size)
        ax.set_title(f'{artist}: Personal vs Global Track Rankings\\nScatter Plot Comparison', 
                    fontsize=self.config.title_size, pad=20)
        
        # Invert both axes so #1 is at top-left
        ax.invert_xaxis()
        ax.invert_yaxis()
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add legend
        loved_patch = patches.Patch(color=self.config.color_palette[0], label='Loved Tracks')
        normal_patch = patches.Patch(color=self.config.color_palette[6], label='Other Tracks')
        ax.legend(handles=[loved_patch, normal_patch], loc='lower right')
        
        # Add interpretation text
        ax.text(0.02, 0.98, 'Points below diagonal:\\nRanked higher personally',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='gray', alpha=0.7))
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/ranking_scatter_{artist.lower().replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_rank_difference_bar_chart(self, matches: List[TrackMatch], artist: str) -> str:
        """
        Create a horizontal bar chart showing rank differences (personal - global)
        
        Positive values indicate tracks ranked higher personally than globally
        """
        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.dpi)
        
        # Calculate rank differences and sort by difference
        rank_diffs = [(m.track_name, m.personal_rank - m.global_rank, m.loved) for m in matches]
        rank_diffs.sort(key=lambda x: x[1], reverse=True)  # Sort by difference, highest first
        
        track_names = [rd[0] for rd in rank_diffs]
        differences = [rd[1] for rd in rank_diffs]
        loved_status = [rd[2] for rd in rank_diffs]
        
        # Truncate long track names
        display_names = [name if len(name) <= 25 else name[:22] + "..." for name in track_names]
        
        # Color bars based on whether difference is positive (deep cut) or negative (mainstream)
        colors = []
        for diff, loved in zip(differences, loved_status):
            if diff > 0:
                colors.append(self.config.color_palette[3])  # Green for deep cuts
            else:
                colors.append(self.config.color_palette[6])  # Red for mainstream
        
        # Create horizontal bar chart
        y_pos = np.arange(len(display_names))
        bars = ax.barh(y_pos, differences, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
        
        # Add value labels on bars
        for i, (bar, diff) in enumerate(zip(bars, differences)):
            width = bar.get_width()
            label_x = width + (0.5 if width > 0 else -0.5)
            ax.text(label_x, bar.get_y() + bar.get_height()/2, f'{diff:+d}',
                   ha='left' if width > 0 else 'right', va='center', fontsize=9)
        
        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(display_names, fontsize=10)
        ax.set_xlabel('Rank Difference (Personal - Global)', fontsize=self.config.label_size)
        ax.set_title(f'{artist}: Track Ranking Preferences\\n(Positive = Deep Cuts, Negative = Mainstream)', 
                    fontsize=self.config.title_size, pad=20)
        
        # Add vertical line at x=0
        ax.axvline(x=0, color='white', linestyle='-', alpha=0.5, linewidth=1)
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add legend
        deep_patch = patches.Patch(color=self.config.color_palette[3], label='Deep Cuts (Higher Personal Rank)')
        mainstream_patch = patches.Patch(color=self.config.color_palette[6], label='Mainstream Hits (Higher Global Rank)')
        ax.legend(handles=[deep_patch, mainstream_patch], loc='lower right')
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/rank_difference_bars_{artist.lower().replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_percentile_comparison_chart(self, matches: List[TrackMatch], artist: str) -> str:
        """
        Create a chart showing percentile comparison between personal and global rankings
        """
        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.dpi)
        
        # Calculate percentiles
        max_personal = max(m.personal_rank for m in matches)
        max_global = max(m.global_rank for m in matches)
        
        personal_percentiles = [((max_personal - m.personal_rank + 1) / max_personal) * 100 for m in matches]
        global_percentiles = [((max_global - m.global_rank + 1) / max_global) * 100 for m in matches]
        
        track_names = [m.track_name[:20] + "..." if len(m.track_name) > 20 else m.track_name for m in matches]
        
        x = np.arange(len(track_names))
        width = 0.35
        
        # Create grouped bar chart
        bars1 = ax.bar(x - width/2, personal_percentiles, width, 
                      label='Personal Percentile', color=self.config.color_palette[0], alpha=0.8)
        bars2 = ax.bar(x + width/2, global_percentiles, width, 
                      label='Global Percentile', color=self.config.color_palette[1], alpha=0.8)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.0f}%', ha='center', va='bottom', fontsize=8)
        
        # Styling
        ax.set_xlabel('Tracks', fontsize=self.config.label_size)
        ax.set_ylabel('Percentile Ranking', fontsize=self.config.label_size)
        ax.set_title(f'{artist}: Percentile Ranking Comparison\\n(Higher percentile = better ranking)', 
                    fontsize=self.config.title_size, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(track_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Set y-axis to 0-100
        ax.set_ylim(0, 105)
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/percentile_comparison_{artist.lower().replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_correlation_dashboard(self, matches: List[TrackMatch], artist: str) -> str:
        """
        Create a comprehensive dashboard showing multiple correlation metrics
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12), dpi=self.config.dpi)
        
        # Run comprehensive analysis
        comparator = RankingComparator(matches)
        results = comparator.comprehensive_analysis()
        
        # 1. Correlation Metrics Summary (Top Left)
        metrics = ['spearman', 'kendall', 'weighted']
        values = [results[m].value for m in metrics if m in results]
        labels = [m.capitalize() for m in metrics if m in results]
        
        colors_subset = self.config.color_palette[:len(values)]
        bars = ax1.bar(labels, values, color=colors_subset, alpha=0.8)
        ax1.set_title('Correlation Metrics', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Correlation Coefficient')
        ax1.set_ylim(-1, 1)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axhline(y=0, color='white', linestyle='-', alpha=0.5)
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height >= 0 else -0.08),
                    f'{value:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=10)
        
        # 2. Top-N Overlap Analysis (Top Right)
        if 'top_n' in results and results['top_n'].details:
            top_n_data = results['top_n'].details
            n_values = [3, 5, 10]
            overlaps = [top_n_data.get(f'top_{n}', {}).get('overlap_percentage', 0) for n in n_values]
            
            ax2.plot(n_values, overlaps, marker='o', linewidth=3, markersize=8, 
                    color=self.config.color_palette[2])
            ax2.fill_between(n_values, overlaps, alpha=0.3, color=self.config.color_palette[2])
            ax2.set_title('Top-N Overlap Analysis', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Top N Tracks')
            ax2.set_ylabel('Overlap Percentage (%)')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            
            # Add value labels
            for n, overlap in zip(n_values, overlaps):
                ax2.annotate(f'{overlap:.1f}%', (n, overlap), 
                           textcoords="offset points", xytext=(0,10), ha='center')
        
        # 3. Rank Difference Distribution (Bottom Left)
        rank_diffs = [m.personal_rank - m.global_rank for m in matches]
        ax3.hist(rank_diffs, bins=min(len(matches), 10), color=self.config.color_palette[4], 
                alpha=0.7, edgecolor='white')
        ax3.set_title('Rank Difference Distribution', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Personal Rank - Global Rank')
        ax3.set_ylabel('Number of Tracks')
        ax3.axvline(x=0, color='white', linestyle='--', alpha=0.7)
        ax3.grid(True, alpha=0.3)
        
        # Add mean line
        mean_diff = np.mean(rank_diffs)
        ax3.axvline(x=mean_diff, color=self.config.color_palette[6], linestyle='-', linewidth=2)
        ax3.text(mean_diff, ax3.get_ylim()[1] * 0.9, f'Mean: {mean_diff:.1f}', 
                rotation=90, ha='right', va='top')
        
        # 4. Percentile Analysis Summary (Bottom Right)
        if 'percentile' in results and results['percentile'].details:
            percentile_data = results['percentile'].details
            categories = ['Strongly\\nPreferred', 'Moderately\\nPreferred', 'Similar\\nPreference', 
                         'Moderately\\nMainstream', 'Strongly\\nMainstream']
            counts = [
                percentile_data['strongly_preferred'],
                percentile_data['moderately_preferred'],
                percentile_data['similar_preference'],
                percentile_data['moderately_mainstream'],
                percentile_data['strongly_mainstream']
            ]
            
            colors_pie = self.config.color_palette[7:12] if len(self.config.color_palette) >= 12 else self.config.color_palette[:5]
            wedges, texts, autotexts = ax4.pie(counts, labels=categories, autopct='%1.0f%%',
                                              colors=colors_pie, startangle=90)
            ax4.set_title('Taste Profile Distribution', fontsize=14, fontweight='bold')
        
        # Overall title
        fig.suptitle(f'{artist}: Comprehensive Ranking Analysis Dashboard', 
                    fontsize=18, fontweight='bold', y=0.95)
        
        plt.tight_layout()
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/correlation_dashboard_{artist.lower().replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def create_all_visualizations(self, matches: List[TrackMatch], artist: str = "Stone Temple Pilots") -> List[str]:
        """Create all visualization types and return list of filenames"""
        
        print(f"🎨 Creating visualizations for {artist}...")
        filenames = []
        
        try:
            # 1. Scatter plot
            print("  📊 Creating ranking scatter plot...")
            filenames.append(self.create_ranking_scatter_plot(matches, artist))
            
            # 2. Bar chart
            print("  📈 Creating rank difference bar chart...")
            filenames.append(self.create_rank_difference_bar_chart(matches, artist))
            
            # 3. Percentile comparison
            print("  📉 Creating percentile comparison chart...")
            filenames.append(self.create_percentile_comparison_chart(matches, artist))
            
            # 4. Correlation dashboard
            print("  🎛️ Creating correlation dashboard...")
            filenames.append(self.create_correlation_dashboard(matches, artist))
            
            print(f"✅ Created {len(filenames)} visualizations!")
            print(f"📁 Saved to: {self.output_dir}")
            
        except Exception as e:
            print(f"❌ Error creating visualizations: {str(e)}")
        
        return filenames


def demonstrate_visualization_system():
    """Demonstrate the visualization system with Stone Temple Pilots data"""
    
    # Sample data
    sample_matches = [
        TrackMatch("Sex Type Thing", 2, 7, 32, 391855, True),
        TrackMatch("Interstate Love Song", 3, 4, 21, 468191, True),
        TrackMatch("Sin", 4, 20, 18, 153271, True),
        TrackMatch("Down", 5, 12, 16, 235467, True),
        TrackMatch("Plush", 8, 1, 8, 799301, True),
        TrackMatch("Dead & Bloated", 10, 17, 4, 167545, True),
    ]
    
    print("🎨 VISUALIZATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print(f"Creating comprehensive visualizations for Stone Temple Pilots")
    print(f"Data: {len(sample_matches)} matched tracks")
    print("-" * 60)
    
    # Create visualizer with dark theme
    config = VisualizationConfig(
        figure_size=(14, 10),
        style="dark_background",
        dpi=300
    )
    
    visualizer = LastfmVisualizer(config)
    filenames = visualizer.create_all_visualizations(sample_matches, "Stone Temple Pilots")
    
    print(f"\\n📋 GENERATED VISUALIZATIONS:")
    print("-" * 60)
    for i, filename in enumerate(filenames, 1):
        basename = os.path.basename(filename)
        print(f"{i}. {basename}")
    
    print(f"\\n🚀 Visualization system demonstration complete!")
    print(f"📂 All files saved to visualizations directory")
    
    return filenames


if __name__ == "__main__":
    demonstrate_visualization_system()

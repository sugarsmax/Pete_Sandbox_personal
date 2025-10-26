#!/usr/bin/env python3
"""
Advanced Last.fm Track Ranking Comparison Algorithms

This module implements sophisticated statistical analysis methods for comparing
personal Last.fm listening patterns with global popularity rankings.

Created: 2025-09-24
Author: Claude Sonnet 4
"""

import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ComparisonMethod(Enum):
    """Available comparison methods"""
    SPEARMAN_CORRELATION = "spearman"
    KENDALL_TAU = "kendall"
    TOP_N_OVERLAP = "top_n"
    RANK_BIASED_OVERLAP = "rbo"
    WEIGHTED_RANK_CORRELATION = "weighted"
    PERCENTILE_ANALYSIS = "percentile"


@dataclass
class TrackMatch:
    """Structure for matched tracks between personal and global rankings"""
    track_name: str
    personal_rank: int
    global_rank: int
    personal_scrobbles: int
    global_scrobbles: int
    loved: bool = False


@dataclass
class ComparisonResult:
    """Structure for comparison analysis results"""
    method: ComparisonMethod
    value: float
    p_value: Optional[float] = None
    interpretation: str = ""
    details: Dict = None


class RankingComparator:
    """Advanced ranking comparison algorithms"""
    
    def __init__(self, matches: List[TrackMatch]):
        self.matches = matches
        self.personal_ranks = [m.personal_rank for m in matches]
        self.global_ranks = [m.global_rank for m in matches]
        
    def spearman_correlation(self) -> ComparisonResult:
        """
        Calculate Spearman rank correlation coefficient
        
        Measures monotonic relationship between rankings
        Range: -1 (perfect negative correlation) to +1 (perfect positive correlation)
        """
        n = len(self.matches)
        if n < 3:
            return ComparisonResult(
                method=ComparisonMethod.SPEARMAN_CORRELATION,
                value=0.0,
                interpretation="Insufficient data for correlation analysis"
            )
        
        # Calculate rank differences squared
        d_squared = [(p - g) ** 2 for p, g in zip(self.personal_ranks, self.global_ranks)]
        sum_d_squared = sum(d_squared)
        
        # Spearman's formula
        rho = 1 - (6 * sum_d_squared) / (n * (n**2 - 1))
        
        # Interpretation
        if abs(rho) > 0.8:
            interpretation = "Very strong correlation"
        elif abs(rho) > 0.6:
            interpretation = "Strong correlation"
        elif abs(rho) > 0.4:
            interpretation = "Moderate correlation"
        elif abs(rho) > 0.2:
            interpretation = "Weak correlation"
        else:
            interpretation = "Very weak or no correlation"
            
        if rho < 0:
            interpretation = f"Negative {interpretation.lower()}"
        else:
            interpretation = f"Positive {interpretation.lower()}"
        
        return ComparisonResult(
            method=ComparisonMethod.SPEARMAN_CORRELATION,
            value=rho,
            interpretation=interpretation,
            details={"sum_d_squared": sum_d_squared, "n": n}
        )
    
    def kendall_tau(self) -> ComparisonResult:
        """
        Calculate Kendall's Tau rank correlation
        
        Measures ordinal association between rankings based on concordant/discordant pairs
        More robust to outliers than Spearman
        """
        n = len(self.matches)
        if n < 3:
            return ComparisonResult(
                method=ComparisonMethod.KENDALL_TAU,
                value=0.0,
                interpretation="Insufficient data for correlation analysis"
            )
        
        concordant = 0
        discordant = 0
        
        # Compare all pairs
        for i in range(n):
            for j in range(i + 1, n):
                # Check if the ordering is the same in both rankings
                personal_order = (self.personal_ranks[i] - self.personal_ranks[j]) * \
                               (self.global_ranks[i] - self.global_ranks[j])
                
                if personal_order > 0:
                    concordant += 1
                elif personal_order < 0:
                    discordant += 1
                # Ties are ignored
        
        total_pairs = n * (n - 1) // 2
        tau = (concordant - discordant) / total_pairs
        
        # Interpretation
        if abs(tau) > 0.7:
            interpretation = "Very strong agreement"
        elif abs(tau) > 0.5:
            interpretation = "Strong agreement"
        elif abs(tau) > 0.3:
            interpretation = "Moderate agreement"
        elif abs(tau) > 0.1:
            interpretation = "Weak agreement"
        else:
            interpretation = "Very weak or no agreement"
            
        if tau < 0:
            interpretation = f"Negative {interpretation.lower()}"
        else:
            interpretation = f"Positive {interpretation.lower()}"
        
        return ComparisonResult(
            method=ComparisonMethod.KENDALL_TAU,
            value=tau,
            interpretation=interpretation,
            details={
                "concordant_pairs": concordant,
                "discordant_pairs": discordant,
                "total_pairs": total_pairs
            }
        )
    
    def top_n_overlap(self, n_values: List[int] = None) -> ComparisonResult:
        """
        Calculate overlap in top-N tracks between personal and global rankings
        
        Args:
            n_values: List of N values to check (default: [3, 5, 10])
        """
        if n_values is None:
            n_values = [3, 5, 10]
        
        # Get sets of top-N tracks for each ranking
        overlaps = {}
        interpretations = []
        
        for n in n_values:
            # Personal top-N tracks
            personal_top_n = set([m.track_name for m in self.matches if m.personal_rank <= n])
            # Global top-N tracks  
            global_top_n = set([m.track_name for m in self.matches if m.global_rank <= n])
            
            # Calculate overlap
            overlap = len(personal_top_n.intersection(global_top_n))
            overlap_percentage = (overlap / min(len(personal_top_n), len(global_top_n))) * 100 if personal_top_n and global_top_n else 0
            
            overlaps[f"top_{n}"] = {
                "overlap_count": overlap,
                "overlap_percentage": overlap_percentage,
                "personal_tracks": list(personal_top_n),
                "global_tracks": list(global_top_n)
            }
            
            if overlap_percentage > 70:
                interpretations.append(f"High overlap in top {n} ({overlap_percentage:.1f}%)")
            elif overlap_percentage > 40:
                interpretations.append(f"Moderate overlap in top {n} ({overlap_percentage:.1f}%)")
            else:
                interpretations.append(f"Low overlap in top {n} ({overlap_percentage:.1f}%)")
        
        # Overall score as average overlap percentage
        avg_overlap = sum([overlaps[f"top_{n}"]["overlap_percentage"] for n in n_values]) / len(n_values)
        
        return ComparisonResult(
            method=ComparisonMethod.TOP_N_OVERLAP,
            value=avg_overlap,
            interpretation=f"Average top-N overlap: {avg_overlap:.1f}%",
            details=overlaps
        )
    
    def rank_biased_overlap(self, p: float = 0.9) -> ComparisonResult:
        """
        Calculate Rank-Biased Overlap (RBO)
        
        A top-heavy ranking comparison metric that gives more weight to top-ranked items.
        Useful when differences at the top are more important than at the bottom.
        
        Args:
            p: Persistence parameter (0-1). Higher p gives more weight to lower ranks.
        """
        if not (0 < p < 1):
            raise ValueError("Persistence parameter p must be between 0 and 1")
        
        # Create rank mappings
        personal_to_rank = {m.track_name: m.personal_rank for m in self.matches}
        global_to_rank = {m.track_name: m.global_rank for m in self.matches}
        
        # Get all tracks
        all_tracks = set(personal_to_rank.keys()) | set(global_to_rank.keys())
        
        # Calculate RBO
        max_rank = max(max(personal_to_rank.values()), max(global_to_rank.values()))
        rbo_sum = 0.0
        
        for d in range(1, max_rank + 1):
            # Get top-d tracks from each ranking
            personal_top_d = {track for track, rank in personal_to_rank.items() if rank <= d}
            global_top_d = {track for track, rank in global_to_rank.items() if rank <= d}
            
            # Calculate overlap at depth d
            overlap_d = len(personal_top_d.intersection(global_top_d))
            agreement_d = (2 * overlap_d) / (len(personal_top_d) + len(global_top_d)) if personal_top_d or global_top_d else 0
            
            # Add to RBO sum with geometric weighting
            rbo_sum += agreement_d * (p ** (d - 1))
        
        rbo = (1 - p) * rbo_sum
        
        # Interpretation
        if rbo > 0.8:
            interpretation = "Very high top-weighted similarity"
        elif rbo > 0.6:
            interpretation = "High top-weighted similarity"
        elif rbo > 0.4:
            interpretation = "Moderate top-weighted similarity"
        elif rbo > 0.2:
            interpretation = "Low top-weighted similarity"
        else:
            interpretation = "Very low top-weighted similarity"
        
        return ComparisonResult(
            method=ComparisonMethod.RANK_BIASED_OVERLAP,
            value=rbo,
            interpretation=interpretation,
            details={"persistence_parameter": p, "max_rank": max_rank}
        )
    
    def weighted_rank_correlation(self, weight_function: str = "inverse") -> ComparisonResult:
        """
        Calculate weighted rank correlation giving more importance to top ranks
        
        Args:
            weight_function: "inverse" (1/rank) or "exponential" (exp(-rank))
        """
        n = len(self.matches)
        if n < 3:
            return ComparisonResult(
                method=ComparisonMethod.WEIGHTED_RANK_CORRELATION,
                value=0.0,
                interpretation="Insufficient data for correlation analysis"
            )
        
        # Calculate weights based on personal rankings (top ranks get higher weights)
        if weight_function == "inverse":
            weights = [1.0 / rank for rank in self.personal_ranks]
        elif weight_function == "exponential":
            weights = [math.exp(-rank / 10) for rank in self.personal_ranks]  # Normalized exponential
        else:
            raise ValueError("Weight function must be 'inverse' or 'exponential'")
        
        # Weighted Spearman calculation
        total_weight = sum(weights)
        weighted_mean_personal = sum(w * p for w, p in zip(weights, self.personal_ranks)) / total_weight
        weighted_mean_global = sum(w * g for w, g in zip(weights, self.global_ranks)) / total_weight
        
        # Weighted covariance and variances
        weighted_cov = sum(w * (p - weighted_mean_personal) * (g - weighted_mean_global) 
                          for w, p, g in zip(weights, self.personal_ranks, self.global_ranks)) / total_weight
        
        weighted_var_personal = sum(w * (p - weighted_mean_personal) ** 2 
                                   for w, p in zip(weights, self.personal_ranks)) / total_weight
        weighted_var_global = sum(w * (g - weighted_mean_global) ** 2 
                                 for w, g in zip(weights, self.global_ranks)) / total_weight
        
        # Weighted correlation
        if weighted_var_personal > 0 and weighted_var_global > 0:
            weighted_corr = weighted_cov / math.sqrt(weighted_var_personal * weighted_var_global)
        else:
            weighted_corr = 0.0
        
        # Interpretation
        if abs(weighted_corr) > 0.8:
            interpretation = "Very strong top-weighted correlation"
        elif abs(weighted_corr) > 0.6:
            interpretation = "Strong top-weighted correlation"
        elif abs(weighted_corr) > 0.4:
            interpretation = "Moderate top-weighted correlation"
        elif abs(weighted_corr) > 0.2:
            interpretation = "Weak top-weighted correlation"
        else:
            interpretation = "Very weak top-weighted correlation"
            
        if weighted_corr < 0:
            interpretation = f"Negative {interpretation.lower()}"
        else:
            interpretation = f"Positive {interpretation.lower()}"
        
        return ComparisonResult(
            method=ComparisonMethod.WEIGHTED_RANK_CORRELATION,
            value=weighted_corr,
            interpretation=interpretation,
            details={
                "weight_function": weight_function,
                "total_weight": total_weight,
                "top_3_weights": weights[:3] if len(weights) >= 3 else weights
            }
        )
    
    def percentile_analysis(self) -> ComparisonResult:
        """
        Analyze ranking differences using percentile conversion
        
        Normalizes ranks to percentiles to handle different catalog sizes fairly
        """
        # Convert ranks to percentiles (assuming full catalogs)
        # This requires knowing the total catalog size, but we'll estimate
        max_personal_rank = max(self.personal_ranks)
        max_global_rank = max(self.global_ranks)
        
        personal_percentiles = [((max_personal_rank - rank + 1) / max_personal_rank) * 100 
                               for rank in self.personal_ranks]
        global_percentiles = [((max_global_rank - rank + 1) / max_global_rank) * 100 
                             for rank in self.global_ranks]
        
        # Calculate percentile differences
        percentile_diffs = [p - g for p, g in zip(personal_percentiles, global_percentiles)]
        avg_percentile_diff = sum(percentile_diffs) / len(percentile_diffs)
        
        # Categorize tracks by percentile difference
        strongly_preferred = sum(1 for diff in percentile_diffs if diff > 20)  # >20 percentile points higher
        moderately_preferred = sum(1 for diff in percentile_diffs if 5 < diff <= 20)
        similar_preference = sum(1 for diff in percentile_diffs if -5 <= diff <= 5)
        moderately_mainstream = sum(1 for diff in percentile_diffs if -20 <= diff < -5)
        strongly_mainstream = sum(1 for diff in percentile_diffs if diff < -20)
        
        # Interpretation
        if avg_percentile_diff > 10:
            interpretation = "Strong preference for deep cuts over mainstream hits"
        elif avg_percentile_diff > 5:
            interpretation = "Moderate preference for deep cuts"
        elif avg_percentile_diff > -5:
            interpretation = "Balanced taste between mainstream and deep cuts"
        elif avg_percentile_diff > -10:
            interpretation = "Moderate preference for mainstream hits"
        else:
            interpretation = "Strong preference for mainstream hits over deep cuts"
        
        return ComparisonResult(
            method=ComparisonMethod.PERCENTILE_ANALYSIS,
            value=avg_percentile_diff,
            interpretation=interpretation,
            details={
                "strongly_preferred": strongly_preferred,
                "moderately_preferred": moderately_preferred,
                "similar_preference": similar_preference,
                "moderately_mainstream": moderately_mainstream,
                "strongly_mainstream": strongly_mainstream,
                "personal_percentiles": personal_percentiles,
                "global_percentiles": global_percentiles,
                "percentile_differences": percentile_diffs
            }
        )
    
    def comprehensive_analysis(self) -> Dict[str, ComparisonResult]:
        """Run all comparison methods and return comprehensive results"""
        results = {}
        
        try:
            results["spearman"] = self.spearman_correlation()
        except Exception as e:
            results["spearman"] = ComparisonResult(
                method=ComparisonMethod.SPEARMAN_CORRELATION,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        try:
            results["kendall"] = self.kendall_tau()
        except Exception as e:
            results["kendall"] = ComparisonResult(
                method=ComparisonMethod.KENDALL_TAU,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        try:
            results["top_n"] = self.top_n_overlap()
        except Exception as e:
            results["top_n"] = ComparisonResult(
                method=ComparisonMethod.TOP_N_OVERLAP,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        try:
            results["rbo"] = self.rank_biased_overlap()
        except Exception as e:
            results["rbo"] = ComparisonResult(
                method=ComparisonMethod.RANK_BIASED_OVERLAP,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        try:
            results["weighted"] = self.weighted_rank_correlation()
        except Exception as e:
            results["weighted"] = ComparisonResult(
                method=ComparisonMethod.WEIGHTED_RANK_CORRELATION,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        try:
            results["percentile"] = self.percentile_analysis()
        except Exception as e:
            results["percentile"] = ComparisonResult(
                method=ComparisonMethod.PERCENTILE_ANALYSIS,
                value=0.0,
                interpretation=f"Error: {str(e)}"
            )
        
        return results


def demonstrate_comparison_algorithms():
    """Demonstrate the comparison algorithms with Stone Temple Pilots data"""
    
    # Sample data from our previous scraping
    sample_matches = [
        TrackMatch("Sex Type Thing", 2, 7, 32, 391855, True),
        TrackMatch("Interstate Love Song", 3, 4, 21, 468191, True),  # Using remaster count
        TrackMatch("Sin", 4, 20, 18, 153271, True),
        TrackMatch("Down", 5, 12, 16, 235467, True),
        TrackMatch("Plush", 8, 1, 8, 799301, True),
        TrackMatch("Dead & Bloated", 10, 17, 4, 167545, True),
    ]
    
    print("🔬 ADVANCED COMPARISON ALGORITHMS DEMONSTRATION")
    print("=" * 60)
    print(f"Sample Data: Stone Temple Pilots (6 matched tracks)")
    print("-" * 60)
    
    comparator = RankingComparator(sample_matches)
    results = comparator.comprehensive_analysis()
    
    for method_name, result in results.items():
        print(f"\n📈 {method_name.upper()} ANALYSIS:")
        print(f"Value: {result.value:.3f}")
        print(f"Interpretation: {result.interpretation}")
        
        if result.details:
            print("Details:")
            for key, value in result.details.items():
                if isinstance(value, (list, dict)):
                    if key in ["personal_percentiles", "global_percentiles", "percentile_differences"] and len(value) > 3:
                        print(f"  {key}: {value[:3]}... (showing first 3)")
                    else:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
        print("-" * 40)
    
    print("\n✅ All comparison methods completed successfully!")
    return results


if __name__ == "__main__":
    demonstrate_comparison_algorithms()

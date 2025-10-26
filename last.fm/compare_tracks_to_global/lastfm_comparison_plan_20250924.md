# Last.fm Personal vs Global Track Ranking Comparison Plan

*This page was built by Claude Sonnet 4 AI assistant*

## Overview

This project aims to compare personal Last.fm listening data against global popularity rankings for any given artist, using Playwright MCP for automated data collection and analysis.

## Data Sources

### Personal Rankings
- **URL Pattern**: `https://www.last.fm/user/{username}/library/music/{artist}/+tracks`
- **Example**: https://www.last.fm/user/sugarsmax/library/music/Stone%20Temple%20Pilots/+tracks
- **Data Points**:
  - Track rank (1-N based on personal play count)
  - Track name
  - Personal scrobble count
  - Album information
  - Love status

### Global Rankings  
- **URL Pattern**: `https://www.last.fm/music/{artist}/+tracks`
- **Example**: https://www.last.fm/music/Stone%20Temple%20Pilots/+tracks
- **Data Points**:
  - Global rank (1-N based on worldwide popularity)
  - Track name
  - Global listener count
  - Global play count
  - Album information

## Technical Implementation

### 1. Playwright MCP Setup
```javascript
// Browser configuration for Last.fm scraping
- User-agent rotation to avoid detection
- Cookie handling for session persistence
- Rate limiting (2-3 seconds between requests)
- Error handling and retry logic
```

### 2. Data Extraction Functions

#### Personal Data Scraper
- Navigate to user library track page
- Extract track table data
- Handle pagination if >50 tracks
- Parse scrobble counts and metadata

#### Global Data Scraper  
- Navigate to artist global tracks page
- Extract global ranking table
- Handle "Show more" button clicks
- Parse listener/play count data

### 3. Data Normalization
- Standardize track names (handle remastered versions)
- Create unified track identifiers
- Handle duplicate entries
- Store in comparable data structures

## Comparison Methods

### 1. Rank Correlation Analysis
- **Spearman Rank Correlation**: Measure overall ranking similarity
- **Kendall's Tau**: Assess pairwise concordance
- **Top-N Agreement**: Compare overlap in top 10, 20, 50 tracks

### 2. Positional Analysis
- **Rank Difference**: `personal_rank - global_rank` for each track
- **Percentile Mapping**: Convert ranks to percentiles for fair comparison
- **Quintile Analysis**: Group tracks into 5 popularity bands

### 3. Outlier Detection
- **Personal Favorites**: High personal rank, low global rank
- **Mainstream Hits**: High global rank, low personal rank  
- **Hidden Gems**: Tracks only in personal top but not global top
- **Missed Classics**: Tracks only in global top but not personal

### 4. Statistical Metrics
```python
metrics = {
    'jaccard_similarity': len(intersection) / len(union),
    'overlap_coefficient': len(intersection) / min(len(personal), len(global)),
    'rank_biased_overlap': weighted_overlap_measure,
    'discounted_cumulative_gain': dcg_score
}
```

## Visualization Options

### 1. Ranking Comparison Charts
- **Slope Graph**: Connect personal to global ranks (like existing QOTSA work)
- **Dot Plot**: Personal vs global positions
- **Scatter Plot**: Rank correlation with trend line

### 2. Agreement Visualizations
- **Sankey Diagram**: Flow from personal to global rank groups
- **Ladder Chart**: Side-by-side ranking comparison
- **Heat Map**: Rank difference intensity

### 3. Category Analysis
- **Radar Chart**: Performance across different metrics
- **Bar Charts**: Top outliers in each category
- **Treemap**: Track popularity by album/era

## Output Formats

### 1. Interactive HTML Reports
- Sortable/filterable track comparison tables
- Interactive charts with hover details
- Embedded album artwork and track previews

### 2. Static Visualizations  
- High-resolution PNG exports for sharing
- Mermaid diagram source files
- PDF summary reports

### 3. Data Exports
- CSV files with full comparison data
- JSON format for API consumption
- Markdown summaries for documentation

## Implementation Strategy

### Phase 1: Core Scraping System
1. Set up Playwright with Last.fm compatibility
2. Build robust scraping functions
3. Implement data cleaning and normalization
4. Create basic comparison metrics

### Phase 2: Analysis Engine
1. Implement all comparison methods
2. Add statistical significance testing
3. Build outlier detection algorithms
4. Create summary statistics

### Phase 3: Visualization System
1. Generate static charts (PNG/SVG)
2. Build interactive HTML reports
3. Create Mermaid diagram exports
4. Add customizable styling options

### Phase 4: Automation & Enhancement
1. Support for multiple artists at once
2. Historical trend analysis over time
3. Genre-based comparisons
4. Social sharing features

## Error Handling & Edge Cases

- **Rate Limiting**: Implement exponential backoff
- **Missing Data**: Handle artists with limited catalogs  
- **Network Errors**: Retry logic with circuit breaker
- **Data Quality**: Validate scraped data integrity
- **Privacy**: Respect user privacy settings
- **Album Variations**: Handle remastered/deluxe editions

## Success Metrics

- Successfully scrape 95%+ of available track data
- Generate meaningful insights for 100+ artists
- Create publication-ready visualizations
- Runtime under 2 minutes per artist comparison
- Zero false positives in track matching

---

*Built using Claude Sonnet 4 AI assistant*

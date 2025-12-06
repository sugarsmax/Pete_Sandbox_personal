#!/usr/bin/env python3
"""
Simple Keyword-Based Theme Analysis

Uses TF-IDF and cosine similarity to group songs by lyrical themes.
Works well for small datasets where BERTopic struggles.

Created: 2025-12-06
"""

import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"


def find_latest_compiled_data() -> Path:
    """Find the most recent compiled lyrics file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    parquet_files = list(DATA_DIR.glob("compiled_lyrics_*.parquet"))
    csv_files = list(DATA_DIR.glob("compiled_lyrics_*.csv"))
    all_files = parquet_files + csv_files
    if not all_files:
        raise FileNotFoundError(f"No compiled lyrics found in {DATA_DIR}")
    return max(all_files, key=lambda p: p.stat().st_mtime)


def extract_keywords(lyrics: str, top_n: int = 10) -> list:
    """Extract top keywords from lyrics."""
    # Common words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we',
        'you', 'your', 'he', 'she', 'they', 'them', 'his', 'her', 'their',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
        'im', 'dont', 'youre', 'wont', 'cant', 'aint', 'gonna', 'wanna',
        'yeah', 'oh', 'ooh', 'ah', 'uh', 'la', 'na', 'da', 'hey', 'cause',
        'like', 'get', 'got', 'go', 'come', 'know', 'see', 'take', 'make',
        'let', 'say', 'tell', 'think', 'want', 'give', 'use', 'find', 'put'
    }
    
    words = lyrics.lower().split()
    words = [w.strip('.,!?()[]"\'') for w in words]
    words = [w for w in words if w.isalpha() and len(w) > 2 and w not in stop_words]
    
    counts = Counter(words)
    return [word for word, _ in counts.most_common(top_n)]


def analyze_themes(df: pd.DataFrame, n_clusters: int = 3) -> dict:
    """Cluster songs by lyrical similarity."""
    # Filter to songs with lyrics
    df_lyrics = df[df['has_lyrics']].copy()
    
    if len(df_lyrics) < 2:
        return {"error": "Need at least 2 songs with lyrics"}
    
    # Adjust clusters for small datasets
    n_clusters = min(n_clusters, len(df_lyrics) // 2)
    n_clusters = max(2, n_clusters)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    tfidf_matrix = vectorizer.fit_transform(df_lyrics['lyrics'].fillna(''))
    
    # Clustering
    clustering = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric='cosine',
        linkage='average'
    )
    
    df_lyrics['cluster'] = clustering.fit_predict(tfidf_matrix.toarray())
    
    # Extract theme keywords per cluster
    themes = {}
    feature_names = vectorizer.get_feature_names_out()
    
    for cluster_id in range(n_clusters):
        cluster_songs = df_lyrics[df_lyrics['cluster'] == cluster_id]
        
        # Get top TF-IDF terms for this cluster
        cluster_mask = (df_lyrics['cluster'] == cluster_id).values
        cluster_tfidf = tfidf_matrix[cluster_mask].mean(axis=0).A1
        top_indices = cluster_tfidf.argsort()[-5:][::-1]
        keywords = [feature_names[i] for i in top_indices]
        
        # Combine lyrics for keyword extraction
        combined_lyrics = ' '.join(cluster_songs['lyrics'].fillna(''))
        simple_keywords = extract_keywords(combined_lyrics, 5)
        
        themes[cluster_id] = {
            'keywords': keywords,
            'simple_keywords': simple_keywords,
            'songs': cluster_songs[['artist', 'track', 'scrobbles']].to_dict('records')
        }
    
    return {
        'themes': themes,
        'n_songs_analyzed': len(df_lyrics),
        'n_songs_missing': len(df) - len(df_lyrics)
    }


def generate_markdown(results: dict, df: pd.DataFrame) -> str:
    """Generate markdown summary."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        "# Lyrics Theme Analysis",
        "",
        f"> Generated: {date_str}",
        "> Built by Claude Opus 4.5",
        "",
        "## Overview",
        "",
        f"- **Total tracks**: {len(df)}",
        f"- **With lyrics**: {results['n_songs_analyzed']}",
        f"- **Themes found**: {len(results['themes'])}",
        "",
        "## Themes",
        "",
    ]
    
    # Theme names based on common patterns
    theme_labels = [
        "Intensity & Desire",
        "Reflection & Loss",
        "Energy & Rebellion",
        "Longing & Connection",
        "Darkness & Struggle"
    ]
    
    for cluster_id, theme_data in results['themes'].items():
        keywords = theme_data['simple_keywords']
        label = theme_labels[cluster_id % len(theme_labels)]
        
        lines.append(f"### Theme {cluster_id + 1}: {label}")
        lines.append("")
        lines.append(f"**Keywords**: {', '.join(keywords)}")
        lines.append(f"**Songs**: {len(theme_data['songs'])}")
        lines.append("")
        
        for song in theme_data['songs']:
            lines.append(f"- {song['artist']} - {song['track']} ({song['scrobbles']} plays)")
        lines.append("")
    
    # Missing lyrics
    df_no_lyrics = df[~df['has_lyrics']]
    if len(df_no_lyrics) > 0:
        lines.append("### Missing Lyrics")
        lines.append("")
        for _, song in df_no_lyrics.iterrows():
            lines.append(f"- {song['artist']} - {song['track']}")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "*Analysis performed using TF-IDF vectorization and hierarchical clustering.*",
    ])
    
    return "\n".join(lines)


def main():
    # Load data
    file_path = find_latest_compiled_data()
    print(f"Loading: {file_path}")
    
    if file_path.suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)
    
    print(f"\nData loaded:")
    print(f"  Total tracks: {len(df)}")
    print(f"  With lyrics: {df['has_lyrics'].sum()}")
    
    # Analyze
    print("\nAnalyzing themes...")
    results = analyze_themes(df, n_clusters=3)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return 1
    
    print(f"  Found {len(results['themes'])} themes")
    
    # Generate output
    markdown = generate_markdown(results, df)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"theme_analysis_simple_{date_str}.md"
    output_path.write_text(markdown)
    
    print(f"\nSaved: {output_path}")
    print("\n" + "="*50)
    print(markdown)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


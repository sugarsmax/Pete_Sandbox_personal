#!/usr/bin/env python3
"""
Theme Analysis using NMF (Non-negative Matrix Factorization)

Discovers themes from lyrics without predefined categories.
Uses TF-IDF vectorization + NMF topic modeling.

Created: 2025-12-07
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"

# Custom stop words for lyrics (vocal sounds, filler, common non-content words)
LYRICS_STOP_WORDS = [
    # Vocal sounds
    "oh", "ah", "ooh", "yeah", "hey", "uh", "na", "la", "da", "ba",
    "whoa", "woah", "ay", "aye", "mm", "hmm", "hm", "ohhh", "ohh",
    "aah", "ahh", "oooh", "yeahh", "huh", "woo", "wo", "sha",
    # Repetition markers
    "oh oh", "ah ah", "ooh ooh", "na na", "la la", "da da", "hey hey",
    "yeah yeah", "ba ba",
    # Common filler
    "gonna", "gotta", "wanna", "cause", "cuz", "em", "ya", "yo",
    "aint", "dont", "cant", "wont", "didnt", "doesnt", "isnt",
    "ll", "ve", "re",  # Contractions without apostrophes
    # Non-content
    "like", "just", "got", "get", "let", "know", "say", "said",
    "come", "came", "go", "went", "gone", "make", "made",
    "think", "thought", "see", "saw", "take", "took",
]


def clean_lyrics(text: str) -> str:
    """Clean lyrics text for analysis."""
    if not text or pd.isna(text):
        return ""
    
    # Remove common Genius artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove [Verse], [Chorus], etc.
    text = re.sub(r'\d+Embed$', '', text)  # Remove "123Embed" at end
    text = re.sub(r'Embed$', '', text)
    text = re.sub(r"You might also like", '', text, flags=re.IGNORECASE)
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Lowercase
    text = text.lower()
    
    return text


def get_top_words(model, feature_names, n_top_words: int = 15) -> list:
    """Extract top words for each topic."""
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_indices]
        topics.append(top_words)
    return topics


def assign_topics(doc_topic_matrix, threshold: float = 0.05) -> list:
    """Assign each document to its dominant topic."""
    assignments = []
    for doc_idx, doc_topics in enumerate(doc_topic_matrix):
        max_score = doc_topics.max()
        if max_score < threshold:
            assignments.append(-1)  # No clear topic
        else:
            assignments.append(doc_topics.argmax())
    return assignments


def generate_topic_name(words: list) -> str:
    """Generate a readable topic name from top words."""
    # Use first 3-4 distinctive words
    return ", ".join(words[:4]).title()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze lyrics themes using NMF topic modeling"
    )
    parser.add_argument(
        "--input", "-i",
        help="Input CSV file (default: latest compiled_lyrics_*.csv)"
    )
    parser.add_argument(
        "--topics", "-n",
        type=int,
        default=8,
        help="Number of topics to discover (default: 8)"
    )
    parser.add_argument(
        "--words", "-w",
        type=int,
        default=15,
        help="Number of top words per topic (default: 15)"
    )
    parser.add_argument(
        "--min-df",
        type=int,
        default=3,
        help="Minimum document frequency for words (default: 3)"
    )
    parser.add_argument(
        "--max-df",
        type=float,
        default=0.7,
        help="Maximum document frequency for words (default: 0.7)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - use smaller dataset"
    )
    
    args = parser.parse_args()
    
    # Find input file
    if args.input:
        input_path = Path(args.input)
    else:
        # Find latest compiled lyrics CSV
        csv_files = sorted(DATA_DIR.glob("compiled_lyrics_*.csv"), reverse=True)
        if not csv_files:
            print("Error: No compiled_lyrics_*.csv found in data/")
            print("Run compile_lyrics script first.")
            return 1
        input_path = csv_files[0]
    
    print(f"Loading: {input_path}")
    df = pd.read_csv(input_path)
    
    # Filter to rows with lyrics
    df_with_lyrics = df[df['lyrics'].notna() & (df['lyrics'] != '')].copy()
    
    print(f"\nData loaded:")
    print(f"  Total tracks: {len(df)}")
    print(f"  With lyrics: {len(df_with_lyrics)}")
    
    if len(df_with_lyrics) < args.topics:
        print(f"Error: Not enough songs with lyrics for {args.topics} topics")
        return 1
    
    # Test mode - use subset
    if args.test:
        df_with_lyrics = df_with_lyrics.head(50)
        print(f"  Test mode: using {len(df_with_lyrics)} songs")
    
    # Clean lyrics
    print("\nCleaning lyrics...")
    df_with_lyrics['lyrics_clean'] = df_with_lyrics['lyrics'].apply(clean_lyrics)
    
    # Remove songs with very short cleaned lyrics
    df_with_lyrics = df_with_lyrics[df_with_lyrics['lyrics_clean'].str.len() > 50]
    print(f"  After cleaning: {len(df_with_lyrics)} songs")
    
    # TF-IDF Vectorization
    print("\nBuilding TF-IDF matrix...")
    
    # Combine English stop words with custom lyrics stop words
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    all_stop_words = list(ENGLISH_STOP_WORDS) + LYRICS_STOP_WORDS
    
    vectorizer = TfidfVectorizer(
        max_df=args.max_df,      # Ignore words in >70% of docs
        min_df=args.min_df,      # Ignore words in <3 docs
        stop_words=all_stop_words,
        ngram_range=(1, 2),      # Include bigrams
        max_features=5000        # Limit vocabulary size
    )
    
    tfidf_matrix = vectorizer.fit_transform(df_with_lyrics['lyrics_clean'])
    feature_names = vectorizer.get_feature_names_out()
    
    print(f"  Vocabulary size: {len(feature_names)}")
    print(f"  Matrix shape: {tfidf_matrix.shape}")
    
    # NMF Topic Modeling
    print(f"\nRunning NMF with {args.topics} topics...")
    nmf_model = NMF(
        n_components=args.topics,
        random_state=42,
        max_iter=500,
        init='nndsvda'  # Better initialization
    )
    
    doc_topic_matrix = nmf_model.fit_transform(tfidf_matrix)
    
    # Get top words per topic
    topic_words = get_top_words(nmf_model, feature_names, args.words)
    
    # Assign songs to topics
    assignments = assign_topics(doc_topic_matrix)
    df_with_lyrics['topic'] = assignments
    
    # Count songs per topic
    topic_counts = df_with_lyrics['topic'].value_counts().sort_index()
    
    print(f"\nTopics discovered:")
    for topic_idx, words in enumerate(topic_words):
        count = topic_counts.get(topic_idx, 0)
        print(f"  Topic {topic_idx + 1}: {', '.join(words[:5])}... ({count} songs)")
    
    uncategorized = (df_with_lyrics['topic'] == -1).sum()
    print(f"  Uncategorized: {uncategorized} songs")
    
    # Save assignments
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    
    assignments_path = DATA_DIR / f"theme_assignments_nmf_{date_str}.csv"
    df_assignments = df_with_lyrics[['rank', 'artist', 'track', 'topic']].copy()
    df_assignments['topic_name'] = df_assignments['topic'].apply(
        lambda t: generate_topic_name(topic_words[t]) if t >= 0 else "Uncategorized"
    )
    df_assignments.to_csv(assignments_path, index=False)
    print(f"\nSaved assignments: {assignments_path}")
    
    # Generate markdown report
    md_path = OUTPUT_DIR / f"theme_analysis_nmf_{date_str}.md"
    
    lines = [
        "# Lyrics Theme Analysis (NMF)",
        "",
        "> **Disclaimer**: This analysis was generated by Claude Opus 4.5",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d')}",
        f"> Method: NMF (Non-negative Matrix Factorization) with TF-IDF",
        "",
        "## Overview",
        "",
        f"- **Total tracks**: {len(df)}",
        f"- **With lyrics**: {len(df_with_lyrics)}",
        f"- **Topics discovered**: {args.topics}",
        f"- **Vocabulary size**: {len(feature_names)}",
        "",
        "## Topics",
        ""
    ]
    
    # Add each topic
    for topic_idx, words in enumerate(topic_words):
        topic_name = generate_topic_name(words)
        count = topic_counts.get(topic_idx, 0)
        
        lines.append(f"### Topic {topic_idx + 1}: {topic_name}")
        lines.append("")
        lines.append(f"**Top words**: {', '.join(words)}")
        lines.append(f"**Songs**: {count}")
        lines.append("")
        
        # List songs in this topic (limit to 20)
        topic_songs = df_with_lyrics[df_with_lyrics['topic'] == topic_idx]
        for _, row in topic_songs.head(20).iterrows():
            lines.append(f"- {row['artist']} - {row['track']}")
        
        if len(topic_songs) > 20:
            lines.append(f"- *...and {len(topic_songs) - 20} more*")
        
        lines.append("")
    
    # Uncategorized
    uncategorized_songs = df_with_lyrics[df_with_lyrics['topic'] == -1]
    if len(uncategorized_songs) > 0:
        lines.append("### Uncategorized")
        lines.append("")
        lines.append(f"**Songs**: {len(uncategorized_songs)}")
        lines.append("")
        for _, row in uncategorized_songs.head(20).iterrows():
            lines.append(f"- {row['artist']} - {row['track']}")
        if len(uncategorized_songs) > 20:
            lines.append(f"- *...and {len(uncategorized_songs) - 20} more*")
        lines.append("")
    
    # Missing lyrics
    missing = df[df['lyrics'].isna() | (df['lyrics'] == '')]
    if len(missing) > 0:
        lines.append("### Missing Lyrics")
        lines.append("")
        lines.append(f"**Tracks without lyrics**: {len(missing)}")
        lines.append("")
        for _, row in missing.head(20).iterrows():
            lines.append(f"- {row['artist']} - {row['track']}")
        if len(missing) > 20:
            lines.append(f"- *...and {len(missing) - 20} more*")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "*Analysis performed using scikit-learn NMF with TF-IDF vectorization.*",
        ""
    ])
    
    md_content = "\n".join(lines)
    md_path.write_text(md_content)
    print(f"Saved: {md_path}")
    
    # Print summary to console
    print(f"\n{'='*50}")
    print(md_content[:2000])
    if len(md_content) > 2000:
        print("...[truncated]...")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


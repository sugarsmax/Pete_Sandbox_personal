#!/usr/bin/env python3
"""
Analyze Lyrics Themes using BERTopic

Clusters lyrics into themes and generates a concise markdown summary.

Created: 2025-12-06
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

CONFIG_PATH = PROJECT_DIR / "config.yaml"
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def find_latest_compiled_data() -> Path:
    """Find the most recent compiled lyrics file (parquet or csv)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Try parquet first, then csv
    parquet_files = list(DATA_DIR.glob("compiled_lyrics_*.parquet"))
    csv_files = list(DATA_DIR.glob("compiled_lyrics_*.csv"))
    
    all_files = parquet_files + csv_files
    if not all_files:
        raise FileNotFoundError(
            f"No compiled lyrics found in {DATA_DIR}. "
            "Run compile_lyrics first."
        )
    
    # Return most recent by modification time
    return max(all_files, key=lambda p: p.stat().st_mtime)


def load_compiled_data(file_path: Path | None = None) -> pd.DataFrame:
    """Load compiled lyrics data (parquet or csv)."""
    if file_path is None:
        file_path = find_latest_compiled_data()
    
    print(f"Loading: {file_path}")
    
    if file_path.suffix == ".parquet":
        return pd.read_parquet(file_path)
    else:
        return pd.read_csv(file_path)


def run_bertopic_analysis(df: pd.DataFrame, config: dict) -> tuple:
    """
    Run BERTopic clustering on lyrics.
    
    Returns:
        (topic_model, topics, probabilities)
    """
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    
    # Get lyrics with content
    df_with_lyrics = df[df["has_lyrics"]].copy()
    
    if len(df_with_lyrics) < 2:
        raise ValueError("Need at least 2 songs with lyrics for topic modeling")
    
    lyrics_list = df_with_lyrics["lyrics"].tolist()
    
    # Config
    analysis_config = config.get("analysis", {})
    nr_topics = analysis_config.get("nr_topics", "auto")
    min_topic_size = analysis_config.get("min_topic_size", 2)
    embedding_model_name = analysis_config.get("embedding_model", "all-MiniLM-L6-v2")
    
    if nr_topics == "auto":
        nr_topics = None
    
    print(f"  Embedding model: {embedding_model_name}")
    print(f"  Nr topics: {nr_topics or 'auto'}")
    print(f"  Min topic size: {min_topic_size}")
    
    # Initialize embedding model
    embedding_model = SentenceTransformer(embedding_model_name)
    
    # Initialize BERTopic
    topic_model = BERTopic(
        embedding_model=embedding_model,
        nr_topics=nr_topics,
        min_topic_size=min_topic_size,
        verbose=False
    )
    
    # Fit model
    topics, probs = topic_model.fit_transform(lyrics_list)
    
    return topic_model, topics, probs, df_with_lyrics


def generate_markdown_summary(
    df: pd.DataFrame,
    df_with_lyrics: pd.DataFrame,
    topic_model,
    topics: list,
    config: dict
) -> str:
    """Generate concise markdown summary of theme analysis."""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Get topic info
    topic_info = topic_model.get_topic_info()
    
    # Build summary
    lines = [
        "# Lyrics Theme Analysis",
        "",
        f"> Generated: {date_str}",
        "> Built by Claude Opus 4.5",
        "",
        "## Overview",
        "",
        f"- **Total tracks**: {len(df)}",
        f"- **With lyrics**: {len(df_with_lyrics)}",
        f"- **Themes found**: {len(topic_info) - 1}",  # -1 for outlier topic
        "",
        "## Themes",
        "",
    ]
    
    # Add track-topic mapping to dataframe
    df_with_lyrics = df_with_lyrics.copy()
    df_with_lyrics["topic"] = topics
    
    # Process each topic (skip -1 which is outliers)
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        
        if topic_id == -1:
            continue  # Skip outliers for main summary
        
        topic_name = row.get("Name", f"Topic {topic_id}")
        count = row["Count"]
        
        # Get top words for this topic
        topic_words = topic_model.get_topic(topic_id)
        if topic_words:
            keywords = ", ".join([word for word, _ in topic_words[:5]])
        else:
            keywords = "N/A"
        
        # Get songs in this topic
        topic_songs = df_with_lyrics[df_with_lyrics["topic"] == topic_id]
        
        lines.append(f"### Theme {topic_id + 1}: {topic_name}")
        lines.append("")
        lines.append(f"**Keywords**: {keywords}")
        lines.append(f"**Songs**: {count}")
        lines.append("")
        
        # List songs
        for _, song in topic_songs.iterrows():
            lines.append(f"- {song['artist']} - {song['track']}")
        
        lines.append("")
    
    # Handle outliers
    outliers = df_with_lyrics[df_with_lyrics["topic"] == -1]
    if len(outliers) > 0:
        lines.append("### Uncategorized")
        lines.append("")
        lines.append(f"**Songs**: {len(outliers)}")
        lines.append("")
        for _, song in outliers.iterrows():
            lines.append(f"- {song['artist']} - {song['track']}")
        lines.append("")
    
    # Songs without lyrics
    df_no_lyrics = df[~df["has_lyrics"]]
    if len(df_no_lyrics) > 0:
        lines.append("### Missing Lyrics")
        lines.append("")
        for _, song in df_no_lyrics.iterrows():
            lines.append(f"- {song['artist']} - {song['track']}")
        lines.append("")
    
    # Footer
    lines.extend([
        "---",
        "",
        "*Analysis performed using BERTopic with sentence-transformers embeddings.*",
        f"*Model: {config.get('analysis', {}).get('embedding_model', 'all-MiniLM-L6-v2')}*",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze lyrics themes using BERTopic"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run in test mode with mock analysis"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be analyzed without running"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Specific compiled lyrics file to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Custom output filename (without extension)"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config()
    
    # Load data
    try:
        input_path = Path(args.input) if args.input else None
        df = load_compiled_data(input_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Filter to songs with lyrics
    df_with_lyrics = df[df["has_lyrics"]].copy()
    
    print(f"\nData loaded:")
    print(f"  Total tracks: {len(df)}")
    print(f"  With lyrics: {len(df_with_lyrics)}")
    
    if len(df_with_lyrics) < 2:
        print("\nError: Need at least 2 songs with lyrics for theme analysis.")
        print("Run fetch_lyrics to get more lyrics first.")
        return 1
    
    if args.dry_run:
        print("\n[DRY RUN] Would analyze themes for:")
        for _, row in df_with_lyrics.iterrows():
            print(f"  - {row['artist']} - {row['track']} ({row['lyrics_word_count']} words)")
        return 0
    
    # Test mode - generate mock output
    if args.test:
        print("\n[TEST MODE] Generating mock theme analysis...")
        
        # Mock summary for test mode
        markdown = f"""# Lyrics Theme Analysis

> Generated: {datetime.now().strftime("%Y-%m-%d")}
> Built by Claude Opus 4.5

## Overview

- **Total tracks**: {len(df)}
- **With lyrics**: {len(df_with_lyrics)}
- **Themes found**: 3 (test)

## Themes

### Theme 1: Existential & Introspection

**Keywords**: feel, know, time, life, inside
**Songs**: 4

- Queens of the Stone Age - No One Knows
- Stone Temple Pilots - Plush
- Soundgarden - Black Hole Sun
- Alice in Chains - Man in the Box

### Theme 2: Energy & Movement

**Keywords**: run, drive, jump, alive, high
**Songs**: 3

- Van Halen - Jump
- Pearl Jam - Alive
- Red Hot Chili Peppers - Under the Bridge

### Theme 3: Sanctuary & Escape

**Keywords**: shelter, sanctuary, angels, friend, bridge
**Songs**: 3

- The Cult - She Sells Sanctuary
- Nirvana - Smells Like Teen Spirit
- Foo Fighters - Everlong

---

*[TEST MODE] This is mock output. Run without --test for real BERTopic analysis.*
"""
    else:
        # Real BERTopic analysis
        print("\nRunning BERTopic analysis...")
        
        try:
            topic_model, topics, probs, df_analyzed = run_bertopic_analysis(
                df, config
            )
            
            topic_info = topic_model.get_topic_info()
            n_topics = len(topic_info) - 1  # Exclude outliers
            print(f"  Found {n_topics} themes")
            
            # Generate markdown
            markdown = generate_markdown_summary(
                df, df_analyzed, topic_model, topics, config
            )
            
            # Save topic assignments
            df_analyzed["topic"] = topics
            date_str = datetime.now().strftime("%Y%m%d")
            assignments_path = DATA_DIR / f"theme_assignments_{date_str}.csv"
            df_analyzed[["rank", "artist", "track", "topic"]].to_csv(
                assignments_path, index=False
            )
            print(f"  Saved assignments: {assignments_path}")
            
        except ImportError as e:
            print(f"\nError: Missing required library: {e}")
            print("Install with: pip install bertopic sentence-transformers")
            return 1
        except Exception as e:
            print(f"\nError during analysis: {e}")
            return 1
    
    # Save output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    base_name = args.output or f"theme_analysis_{date_str}"
    output_path = OUTPUT_DIR / f"{base_name}.md"
    
    output_path.write_text(markdown, encoding="utf-8")
    print(f"\nSaved: {output_path}")
    
    # Print summary to console
    print("\n" + "="*50)
    print(markdown)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


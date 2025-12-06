#!/usr/bin/env python3
"""Parse Last.fm snapshot files to extract track data."""

import re
import json
import unicodedata
from pathlib import Path
from datetime import datetime


# Classical composers/performers to filter out
CLASSICAL_FILTER = [
    # Major composers
    "bach", "mozart", "beethoven", "chopin", "brahms", "handel", "händel", "haydn",
    "schubert", "tchaikovsky", "vivaldi", "debussy", "liszt", "mendelssohn",
    "rachmaninoff", "ravel", "schumann", "strauss", "wagner", "dvorak", "dvořák",
    "mahler", "verdi", "puccini", "stravinsky", "prokofiev", "shostakovich",
    "grieg", "sibelius", "elgar", "holst", "bernstein", "copland", "barber",
    "gershwin", "satie", "fauré", "faure", "saint-saëns", "saint-saens",
    "rimsky-korsakov", "mussorgsky", "borodin", "paganini", "telemann",
    # Baroque/early music
    "corelli", "scarlatti", "monteverdi", "purcell", "couperin", "rameau",
    "albinoni", "boccherini", "pergolesi", "lully",
    # Classical performers (harpsichordists, etc)
    "sebestyén", "sebestyen", "gould", "horowitz", "rubinstein", "heifetz",
    # BWV/opus indicators (Bach catalog)
    "bwv ",
]


def normalize_for_filter(text: str) -> str:
    """Normalize text for classical filter matching (handle accents)."""
    normalized = unicodedata.normalize('NFD', text.lower())
    ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_text


def is_classical(artist: str, track: str = "") -> bool:
    """Check if artist/track matches classical composers or catalog numbers."""
    combined = normalize_for_filter(f"{artist} {track}")
    for term in CLASSICAL_FILTER:
        if normalize_for_filter(term) in combined:
            return True
    return False

def fix_lastfm_text(text):
    """Fix Last.fm's 's' character rendering issue and common patterns."""
    replacements = {
        "Queen  of the Stone Age": "Queens of the Stone Age",
        "Alice in Chain ": "Alice in Chains",
        "Alice in Chain": "Alice in Chains",
        "Johann Seba tian Bach": "Johann Sebastian Bach",
        "Jano  Sebe tyen": "János Sebestyén", 
        "Jáno  Sebe tyén": "János Sebestyén",
        "Dave Grohl, Jo h Homme, Trent Reznor": "Dave Grohl, Josh Homme, Trent Reznor",
        "Jo h Homme": "Josh Homme",
        "Them Crooked Vulture ": "Them Crooked Vultures",
        "Them Crooked Vulture": "Them Crooked Vultures",
        "Mad Sea on": "Mad Season",
        "Kin ki": "Kinki",
        "De ert Se ion ": "Desert Sessions",
        "De ert Se ion": "Desert Sessions",
        "Ludwig Göran on": "Ludwig Göransson",
        "Eagle  of Death Metal": "Eagles of Death Metal",
        "Nine Inch Nail ": "Nine Inch Nails",
        "Nine Inch Nail": "Nine Inch Nails",
        "Ian A tbury": "Ian Astbury",
        "Screaming Tree ": "Screaming Trees",
        "Screaming Tree": "Screaming Trees",
        "The Black Angel ": "The Black Angels",
        "The Black Angel": "The Black Angels",
        "The White Stripe ": "The White Stripes",
        "The White Stripe": "The White Stripes",
        "Jane'  Addiction": "Jane's Addiction",
        "Ozzy O bourne": "Ozzy Osbourne",
        "Bea tie Boy ": "Beastie Boys",
        "Bea tie Boy": "Beastie Boys",
        "Primu ": "Primus",
        "Primu": "Primus",
        "Re ult ": "Results",
        "Re ult": "Results",
        "Mi fit": "Misfit",
        "Me age  from": "Messages from",
        "Excu e ": "Excuses",
        "Excu e": "Excuses",
        "Hypocritical Ki ": "Hypocritical Kiss",
        "Hypocritical Ki": "Hypocritical Kiss",
        "Sea on": "Season",
        "Whi per": "Whisper",
        "Lo t": "Lost",
        "Ye ": "Yes",
        "Ye": "Yes",
        " crobble": " scrobbles",
        "Sexy Re ult": "Sexy Results",
        "Romantic Right ": "Romantic Rights",
        "Romantic Right": "Romantic Rights",
        "White I  Red": "White Is Red",
        "Engli h Suite": "English Suite",
        "Da  Wohltemperierte": "Das Wohltemperierte",
        "Goldberg Variation ": "Goldberg Variations",
        "French Suite": "French Suite",
        "Organ Sonata": "Organ Sonata",
        "Prelude In": "Prelude In",
        " i ": "is",
        "Doe  I ": "Does Is",
        "Lead  To": "Leads To",
        "Break ": "Breaks",
        "thi  track": "this track",
        "The Blood I  Love": "The Blood Is Love",
        "in trumental": "instrumental",
        "Spinning in Daffodil ": "Spinning in Daffodils",
        "Spinning in Daffodil": "Spinning in Daffodils",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def parse_snapshot_files(file_paths):
    """Parse Last.fm snapshot files and extract track data."""
    tracks = []
    classical_filtered = 0
    
    for file_path in file_paths:
        text = Path(file_path).read_text()
        # DON'T fix text before regex - it changes patterns we're matching
        
        # Pattern for track rows (using raw/unfixed text patterns)
        # Format: "N Play track ... track_name artist_name Buy Loading..."
        # Page 1: "ugar max love  thi  track" (sugarsmax loves this track - with missing 's')  
        # Page 2: "Unlove thi  track"
        pattern = r'name: "?(\d+) (?:Play track )?(?:Unlove this track |Unlove thi  track |ugar max love  thi  track |sugarsmax loves this track )(.+?) Buy Loading'
        
        matches = re.findall(pattern, text)
        for rank_str, content in matches:
            rank = int(rank_str)
            if rank > 100:
                continue
            
            # Apply text fixes AFTER regex matching
            content = fix_lastfm_text(content.strip())
            
            # Known artists to look for at end of content (AFTER fix_lastfm_text applied)
            known_artists = [
                "Queens of the Stone Age", "Death from Above 1979", "Alice in Chains",
                "Johann Sebastian Bach", "János Sebestyén", 
                "Dave Grohl, Josh Homme, Trent Reznor", "Dave Grohl", "Josh Homme",
                "Them Crooked Vultures", "Jack White", "The Cult", "Mad Season",
                "deadmau5", "Niteppl", "Kinki", "Jamiroquai", "Tool", "Reignwolf",
                "The Heavy Eyes", "INXS", "U2", "Desert Sessions", "Ludwig Göransson",
                "Eagles of Death Metal", "Led Zeppelin", "Depeche Mode", "The Police",
                "Interpol", "Beastie Boys", "Nine Inch Nails", "Van Halen", "Duran Duran",
                "Daft Punk", "The Dining Rooms", "The Fixx", "Ian Astbury", "Operatica",
                "The Prodigy", "Beck", "Domenico Scarlatti", "Screaming Trees",
                "The Black Angels", "The Dead Weather", "Primus", "The White Stripes",
                "UNKLE", "Jane's Addiction", "Ozzy Osbourne",
                # Also include some still-broken variants that fix_lastfm_text might miss
                "Queen  of the Stone Age", "Alice in Chain", "Johann Seba tian Bach",
                "Dave Grohl, Jo h Homme, Trent Reznor", "Jáno  Sebe tyén",
                "Eagle  of Death Metal", "Nine Inch Nail", "Bea tie Boy", "The White Stripe",
                "Screaming Tree", "The Black Angel", "Ozzy O bourne", "Jane'  Addiction"
            ]
            
            artist = "Unknown"
            track_name = content
            
            for a in known_artists:
                if content.endswith(a):
                    artist = a
                    track_name = content[:-len(a)].strip()
                    break
                # Also try without trailing 's'
                if content.endswith(a.rstrip('s')):
                    artist = a
                    track_name = content[:-len(a.rstrip('s'))].strip()
                    break
            
            # Clean up track name
            track_name = track_name.strip()
            
            # Skip if already have this rank
            if any(t["rank"] == rank for t in tracks):
                continue
            
            # Skip classical music
            if is_classical(artist, track_name):
                classical_filtered += 1
                continue
                
            tracks.append({
                "rank": rank,
                "artist": artist,
                "track": track_name,
                "scrobbles": 0
            })
    
    # Sort by rank
    tracks.sort(key=lambda x: x["rank"])
    
    # Extract scrobble counts
    for file_path in file_paths:
        text = Path(file_path).read_text()
        # Scrobbles appear as "name: NNN scrobbles" or "name: NNN"
        scrobble_matches = re.findall(r'name: (\d+)\n', text)
        # Filter to reasonable scrobble values (between 30 and 200)
        scrobbles = [int(s) for s in scrobble_matches if 30 <= int(s) <= 200]
    
    # Assign scrobbles based on descending order
    scrobbles_sorted = sorted(set(scrobbles), reverse=True)
    for i, track in enumerate(tracks):
        if i < len(scrobbles_sorted):
            track["scrobbles"] = scrobbles_sorted[i]
    
    # Re-number ranks after filtering
    for i, track in enumerate(tracks, 1):
        track["rank"] = i
    
    return tracks, classical_filtered


def main():
    # Snapshot files from browser
    snapshot_dir = Path("/Users/maxfiep/.cursor/browser-logs")
    
    # Find the most recent snapshots for pages 1 and 2
    page1_file = snapshot_dir / "snapshot-2025-12-06T01-20-03-297Z.log"
    page2_file = snapshot_dir / "snapshot-2025-12-06T01-21-01-258Z.log"
    
    if not page1_file.exists() or not page2_file.exists():
        print("Snapshot files not found!")
        return 1
    
    print("Parsing Last.fm snapshots...")
    tracks, filtered_count = parse_snapshot_files([page1_file, page2_file])
    
    print(f"\nFiltered {filtered_count} classical tracks.")
    print(f"Parsed {len(tracks)} tracks:")
    for t in tracks[:10]:
        print(f"  {t['rank']:3}. {t['artist']} - {t['track']} ({t['scrobbles']})")
    print("  ...")
    for t in tracks[-5:]:
        print(f"  {t['rank']:3}. {t['artist']} - {t['track']} ({t['scrobbles']})")
    
    # Save to cache
    cache_path = Path("/Users/maxfiep/Library/CloudStorage/GoogleDrive-pmaxfield@gmail.com/My Drive/git_personal/Pete_Sandbox_personal/last.fm/Lyrics_top_songs/cache/top_tracks.json")
    
    cache_data = {
        "fetched_at": datetime.now().isoformat(),
        "track_count": len(tracks),
        "tracks": tracks
    }
    
    cache_path.write_text(json.dumps(cache_data, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(tracks)} tracks to: {cache_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())


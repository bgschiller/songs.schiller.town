#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["lyricsgenius>=3.0.1"]
# ///
"""Download song lyrics from Genius using lyricsgenius."""

import argparse
import os
import subprocess
import sys

import lyricsgenius


def get_genius_client():
    """Create a Genius API client."""
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if not token:
        print("Error: GENIUS_ACCESS_TOKEN environment variable not set.")
        print()
        print("To get a token:")
        print("1. Go to https://genius.com/api-clients")
        print("2. Create a new API client")
        print("3. Generate an access token")
        print("4. Export it: export GENIUS_ACCESS_TOKEN='your_token_here'")
        sys.exit(1)

    genius = lyricsgenius.Genius(token, verbose=False)
    genius.remove_section_headers = True  # Remove [Chorus], [Verse], etc.
    return genius


def search_songs(genius, query, num_results=10):
    """Search for songs and return a list of hits."""
    response = genius.search_songs(query)
    hits = response.get("hits", [])[:num_results]
    return hits


def select_with_fzf(hits):
    """Let user select a song using fzf."""
    # Format options for fzf: "index\ttitle - artist"
    options = []
    for i, hit in enumerate(hits):
        song_info = hit["result"]
        title = song_info["title"]
        artist = song_info["primary_artist"]["name"]
        options.append(f"{i}\t{title} - {artist}")

    fzf_input = "\n".join(options)

    try:
        # Use Popen so stderr goes to terminal (fzf needs it for UI)
        # and fzf can read from /dev/tty for interactive input
        process = subprocess.Popen(
            ["fzf", "--with-nth=2..", "--delimiter=\t",
             "--height=~15", "--layout=reverse", "--border",
             "--prompt=Select song: "],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, _ = process.communicate(fzf_input)
    except FileNotFoundError:
        print("Error: fzf not found. Please install fzf or use --first flag.")
        sys.exit(1)

    if process.returncode != 0:
        # User cancelled
        return None

    selected = stdout.strip()
    if not selected:
        return None

    index = int(selected.split("\t")[0])
    return hits[index]


def fetch_song_lyrics(genius, song_id):
    """Fetch full song details including lyrics."""
    return genius.search_song(song_id=song_id)


def save_lyrics(song, output_dir="src/content/songs"):
    """Save lyrics to a markdown file."""
    # Create a slug from the song title
    slug = song.title.lower()
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = slug.strip().replace(" ", "-")
    slug = "-".join(filter(None, slug.split("-")))  # Remove duplicate dashes
    
    filename = f"{slug}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Create frontmatter and content
    content = f"""---
title: "{song.title}"
artist: "{song.artist}"
source: "https://genius.com"
---

{song.lyrics}
"""
    
    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Download song lyrics from Genius")
    parser.add_argument("song", nargs="+", help="Song name to search for")
    parser.add_argument("-a", "--artist", help="Artist name (included in search query)")
    parser.add_argument("-o", "--output", default="src/content/songs",
                        help="Output directory (default: src/content/songs)")
    parser.add_argument("--print-only", action="store_true",
                        help="Print lyrics instead of saving to file")
    parser.add_argument("--first", action="store_true",
                        help="Skip selection and use first result")
    parser.add_argument("-n", "--num-results", type=int, default=10,
                        help="Number of search results to show (default: 10)")

    args = parser.parse_args()

    genius = get_genius_client()

    # Build search query
    song = " ".join(args.song)
    query = f"{song} {args.artist}" if args.artist else song
    print(f"Searching for: {query}")

    hits = search_songs(genius, query, args.num_results)

    if not hits:
        print("No songs found.")
        sys.exit(1)

    # Select song
    if args.first:
        selected = hits[0]
    else:
        selected = select_with_fzf(hits)
        if not selected:
            print("No song selected.")
            sys.exit(0)

    song_info = selected["result"]
    print(f"Fetching: {song_info['title']} by {song_info['primary_artist']['name']}")

    # Fetch full lyrics
    song = fetch_song_lyrics(genius, song_info["id"])

    if not song:
        print("Failed to fetch lyrics.")
        sys.exit(1)

    if args.print_only:
        print()
        print(song.lyrics)
    else:
        filepath = save_lyrics(song, args.output)
        print(f"Saved to: {filepath}")


if __name__ == "__main__":
    main()

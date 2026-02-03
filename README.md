# Bedtime Songs

A simple site to hold lyrics for bedtime songs, hosted at [songs.schiller.town](https://songs.schiller.town).

## Adding a Song

Create a markdown file in `src/content/songs/`. The filename becomes the URL slug.

```markdown
---
title: "Song Title"
artist: "Artist Name"
tags: ["lullaby", "animals"]
---

Lyrics go here...
```

- `title` - Required
- `artist` - Optional
- `tags` - Optional, used for filtering ("Dad, can you sing a train song?")

## Features

- Dark mode for reading in low light
- Instant client-side search by title and artist
- Filter by category tags
- Minimal styling to avoid distraction

## Commands

| Command        | Action                                      |
| :------------- | :------------------------------------------ |
| `pnpm install` | Install dependencies                        |
| `pnpm dev`     | Start local dev server at `localhost:4321`  |
| `pnpm build`   | Build production site to `./dist/`          |
| `pnpm preview` | Preview build locally before deploying      |

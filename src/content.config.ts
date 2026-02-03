import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const songs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/songs' }),
  schema: z.object({
    title: z.string(),
    artist: z.string().optional(),
    tags: z.array(z.string()).optional(),
  }),
});

export const collections = { songs };

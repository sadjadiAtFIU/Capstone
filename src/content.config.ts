import { defineCollection, z } from "astro:content";

const semesters = defineCollection({
  type: "data",
  schema: z.object({
    code: z.string(),
    season: z.string(),
    year: z.number(),
    title: z.string(),
    eventMode: z.enum(["in-person", "virtual"]),
    showcaseDate: z.string().optional(),
    location: z.string().optional(),
    judgesPublic: z.boolean().default(true),
    assignmentsPublic: z.boolean().default(true),
    judgesFormUrl: z.string().optional(),
    projectsFormUrl: z.string().optional(),
    notes: z.string().optional(),
    stats: z.object({
      projects: z.number(),
      judges: z.number().optional(),
      capstone1Students: z.number().optional()
    }),
    featuredProjects: z.array(z.string()).default([])
  })
});

export const collections = { semesters };

import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';

const publicationState = z.enum(['draft', 'published']);

// Visible copy uses hyphens only: em and en dashes are a style violation on this site.
const copy = z.string().refine((value) => !/[\u2013\u2014]/.test(value), 'Use a hyphen, comma or period instead of an em/en dash');

const evidence = z.object({
  source: z.enum(['cv', 'legacy-cv', 'specification', 'document', 'presentation', 'photo-folder']),
  reference: copy,
  verified: z.boolean(),
});

// Products get their own case page; practice tools are CV-backed entries shown on the home page only.
const appsSchema = z
  .object({
    kind: z.enum(['product', 'practice']),
    slug: z.string().regex(/^[a-z0-9-]+$/).optional(),
    order: z.number().int(),
    stage: copy.optional(),
    title: copy,
    area: copy,
    summary: copy,
    problem: copy.optional(),
    workflow: z.array(copy).default([]),
    highlights: z.array(copy).default([]),
    capabilities: z.array(z.object({ group: copy, items: z.array(copy).min(1) })).default([]),
    stack: copy.optional(),
    specVersion: copy.optional(),
    diagram: z.enum(['field-flow', 'stereonet']).optional(),
    pending: z.array(copy).default([]),
    publicationState,
    productStatus: z.enum(['concept', 'prototype', 'pilot', 'in-use', 'released', 'unverified']),
    evidence,
  })
  .refine((app) => app.kind === 'practice' || (app.slug && app.problem && app.workflow.length >= 2), {
    message: 'Products need slug, problem and at least two workflow steps',
  });

const apps = defineCollection({
  loader: file('src/content/apps.json'),
  schema: appsSchema,
});

const apps_en = defineCollection({
  loader: file('src/content/apps.en.json'),
  schema: appsSchema,
});

const photo = z.object({
  slug: z.string().regex(/^[a-z0-9-]+$/),
  // Galleries show the author's own photos from photo/ only. Presentations are published whole as PDFs
  // (see credentials.json "file"), never cut into gallery images.
  source: z.string().regex(/^photo\//, 'Gallery photos come from photo/ only, not from presentations'),
  // Every photo is shown whole in its own proportions; maps, documents and charts get a paper mat.
  kind: z.enum(['photo', 'map', 'document', 'chart', 'thin-section']).default('photo'),
  // Capture date from EXIF or the file name: "2011-11" or "2019". Omitted when unknown (e.g. messenger copies).
  date: z.string().regex(/^\d{4}(-(0[1-9]|1[0-2]))?$/).optional(),
  alt: copy.pipe(z.string().min(8)),
  caption: copy,
});

// "2012 - сейчас" -> [2012, current year], "2025 - present" -> [2025, current year], "2010-2011" -> [2010, 2011], "2008" -> [2008, 2008].
export function periodYears(period: string): [number, number] {
  const years = (period.match(/\d{4}/g) ?? []).map(Number);
  const start = years[0] ?? 0;
  const end = /сейчас|present/i.test(period) ? new Date().getFullYear() : (years[1] ?? start);
  return [start, end];
}

const experienceSchema = z.object({
  order: z.number().int(),
  period: copy,
  place: copy,
  short: copy,
  pattern: z.enum(['granite', 'shale', 'sand', 'basalt', 'quartz', 'gabbro', 'gneiss']),
  title: copy,
  organization: copy,
  role: copy.optional(),
  summary: copy,
  highlights: z.array(copy).min(1),
  materials: z.array(copy).default([]),
  pending: z.array(copy).default([]),
  photoNote: copy.optional(),
  photos: z.array(photo).default([]),
  publicationState,
  evidence: z.array(evidence).min(1),
}).superRefine((stage, ctx) => {
  // Photos are synced to stages by year: a dated photo outside the stage period fails the build.
  const [start, end] = periodYears(stage.period);
  stage.photos.forEach((item, index) => {
    if (!item.date) return;
    const year = Number(item.date.slice(0, 4));
    if (year < start || year > end) {
      ctx.addIssue({
        code: 'custom',
        path: ['photos', index, 'date'],
        message: `${item.slug}: снимок ${item.date} не входит в годы этапа «${stage.period}»`,
      });
    }
  });
});

const experience = defineCollection({
  loader: file('src/content/experience.json'),
  schema: experienceSchema,
});

const experience_en = defineCollection({
  loader: file('src/content/experience.en.json'),
  schema: experienceSchema,
});

const credentialsSchema = z.object({
  kind: z.enum(['award', 'certificate', 'education', 'publication', 'talk']),
  title: copy,
  authors: copy.optional(),
  organization: copy,
  place: copy.optional(),
  year: copy,
  detail: copy.optional(),
  url: z.url().optional(),
  // Standalone PDF of the presentation in public/talks/, exported by scripts/export_talks.py.
  file: z.string().regex(/^\/talks\/[a-z0-9-]+\.pdf$/).optional(),
  publicationState,
  evidence,
});

const credentials = defineCollection({
  loader: file('src/content/credentials.json'),
  schema: credentialsSchema,
});

const credentials_en = defineCollection({
  loader: file('src/content/credentials.en.json'),
  schema: credentialsSchema,
});

export const collections = { apps, experience, credentials, apps_en, experience_en, credentials_en };

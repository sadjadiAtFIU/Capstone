# FIU Capstone Showcase

This project replaces the existing semester-by-semester manually assembled showcase pages with a maintainable static site and a repeatable publishing workflow.

## Goals

- provide a polished homepage at `/Capstone/`
- publish one subsite per semester such as `/Capstone/FA25/`
- archive historical semesters in a consistent format
- stop depending on Word mail merge and manual HTML assembly
- deploy static files directly to FIU hosting

## Project structure

- `src/`: Astro pages, layouts, and site code
- `src/content/semesters/`: lightweight metadata for each semester
- `data/semesters/<code>/`: normalized semester data used for generated pages
- `scripts/`: deployment and future import scripts

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Deploy to FIU

```bash
npm run deploy:fiu
```

By default deployment targets:

- host: `sadjadi@ocelot.aul.fiu.edu`
- directory: `~/public_html/Capstone/`

Override with:

```bash
CAPSTONE_DEPLOY_HOST=... CAPSTONE_DEPLOY_DIR=... npm run deploy:fiu
```

## Semester intake going forward

For each semester, keep a folder under `data/semesters/<code>/` and provide:

- project records
- judge records
- Capstone I student assignment records
- semester metadata

Going forward, the preferred source is Google Sheets URLs or exported CSVs from the semester forms.

### Importing from Google Sheets

If a sheet tab is shared broadly enough to allow CSV export, fetch it into the project with:

```bash
npm run fetch:sheet -- "https://docs.google.com/spreadsheets/d/<DOC_ID>/export?format=csv&gid=<GID>" "data/semesters/FA25/raw/projects.csv"
```

If Google returns an HTML sign-in page instead of CSV, the sheet is not accessible for automated export yet. In that case either:

- change the sheet sharing so anyone with the link can view, or
- export the sheet to CSV manually and place it under `data/semesters/<code>/raw/`

## Historical migration plan

1. finish the `FA25` migration as the reference implementation
2. define import scripts for historical semester data
3. backfill `SP25`, `SU25`, `FA24`, and earlier terms
4. redesign detail pages and assignment pages once the data model is stable

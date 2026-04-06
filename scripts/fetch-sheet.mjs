import fs from "node:fs/promises";
import path from "node:path";

function usage() {
  console.error(
    "Usage: node scripts/fetch-sheet.mjs <google-sheet-export-url> <output-file>\n" +
      "Example: node scripts/fetch-sheet.mjs 'https://docs.google.com/.../export?format=csv&gid=123' data/semesters/FA25/raw/projects.csv"
  );
}

const [, , inputUrl, outputFile] = process.argv;

if (!inputUrl || !outputFile) {
  usage();
  process.exit(1);
}

const response = await fetch(inputUrl, {
  headers: {
    "user-agent": "capstone-showcase-import/0.1"
  },
  redirect: "follow"
});

if (!response.ok) {
  console.error(`Request failed with status ${response.status}`);
  process.exit(1);
}

const body = await response.text();
const lower = body.toLowerCase();

if (lower.includes("<!doctype html") || lower.includes("sign in to your google account")) {
  console.error("The provided URL did not return CSV data.");
  console.error("Google likely requires sign-in or the sheet is not shared publicly enough for automated export.");
  console.error("Required sharing setting: anyone with the link can view, or provide a manually exported CSV file.");
  process.exit(2);
}

await fs.mkdir(path.dirname(outputFile), { recursive: true });
await fs.writeFile(outputFile, body, "utf8");

console.log(`Saved ${outputFile}`);

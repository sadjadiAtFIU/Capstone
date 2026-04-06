# Migration Notes

## Current findings

- semester source materials are archived under the Google Drive course directory
- recent semesters include Google Forms and response sheet links
- Fall 2025 includes a manually generated publish directory at `253 - Fall 2025/FA25`
- the legacy workflow appears to rely on Word mail merge templates plus spreadsheet exports

## Open design decisions

- whether judge and Capstone I assignments remain fully public
- whether future semester imports read from direct Google Sheets export URLs or manually exported CSV files
- how much historical material should be recreated exactly versus modernized during migration

## Google Sheets access note

The two Fall 2025 sheet URLs currently return a Google sign-in page rather than CSV data when fetched non-interactively. That means automated imports will not work until those sheets are either:

- shared so anyone with the link can view, or
- exported to CSV manually and dropped into the semester `raw/` folder

## Recommended publication model

- public homepage for the entire Capstone program
- semester landing pages at `/FA25/`, `/SP26/`, and so on
- generated project pages and assignment pages from normalized source data
- optional private-by-link or tokenized assignment views later if public exposure becomes a concern

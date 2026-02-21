# Palette's Journal - Critical Learnings

This journal records CRITICAL UX/accessibility learnings.
Format: `## YYYY-MM-DD - [Title]`
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]

## 2026-02-20 - [Smart Folder Browsing]
**Learning:** Users often correct path typos by browsing, but standard dialogs reset to root (Desktop), causing frustration. Pre-selecting the current path in `FolderBrowserDialog` significantly reduces this friction.
**Action:** Always check if a text input contains a valid path and pre-select it when opening a browse dialog.

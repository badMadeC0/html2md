#!/bin/bash
# Script to close invalid/redundant PRs on badMadeC0/html2md
# Run locally where you have `gh auth login` configured
# Usage: bash close-invalid-prs.sh

REPO="badMadeC0/html2md"

# Group 1: Exception handling refactors - ALL REDUNDANT
# cli.py already has RequestException, OSError, and generic Exception handling
EXCEPTION_PRS=(196 197 198 199 200 201 202 203 205 206 207 208 209 210 239 240 242)
for pr in "${EXCEPTION_PRS[@]}"; do
  echo "Closing PR #$pr (exception handling - already implemented)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: cli.py already implements specific exception handling for \`RequestException\`, \`OSError\`, and generic \`Exception\`. This PR is redundant."
done

# Group 2: csv.writer / log_export optimizations - ALL REDUNDANT
# log_export.py already uses csv.writer with sanitization
LOG_EXPORT_PRS=(190 192 230 234 236 245 247 249 255 257 260 262 266 269 271 274 275 278 280 296 303)
for pr in "${LOG_EXPORT_PRS[@]}"; do
  echo "Closing PR #$pr (log_export optimization - already implemented)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: \`log_export.py\` already uses \`csv.writer\` (not \`DictWriter\`) with sanitization. This optimization is already in the codebase."
done

# Group 3: GUI accessibility / layout - ALL REDUNDANT
# gui-url-convert.ps1 already has Grid layout, AutomationProperties, Clear button, labels
GUI_PRS=(227 231 235 237 244 246 250 252 253 254 256 258 264 268 270 273 276 279 282 304 306)
for pr in "${GUI_PRS[@]}"; do
  echo "Closing PR #$pr (GUI accessibility - already implemented)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: \`gui-url-convert.ps1\` already has Grid layout, \`AutomationProperties.Name\`, Clear button, and accessible labels. This PR is redundant."
done

# Group 4: Self-healing CI workflow duplicates (keep none - not merged, all duplicates)
CI_PRS=(232 243 248 261 267 272 277 283 302)
for pr in "${CI_PRS[@]}"; do
  echo "Closing PR #$pr (self-healing CI - duplicate)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: Multiple duplicate PRs for the same self-healing CI feature. None have been merged; consolidate into a single PR if still desired."
done

# Group 5: Security fixes already implemented
SECURITY_PRS=(191 229 251 281)
for pr in "${SECURITY_PRS[@]}"; do
  echo "Closing PR #$pr (security fix - already implemented)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: The security fix in this PR is already implemented in the current codebase (command injection prevention, URL scheme validation)."
done

# Group 6: Test PRs overlapping with existing tests
TEST_PRS=(195 204 211 213 284 286 289 290)
for pr in "${TEST_PRS[@]}"; do
  echo "Closing PR #$pr (tests - already covered)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: The test coverage in this PR overlaps with existing tests (\`test_cli_exceptions.py\`, \`test_cli_error.py\`, \`test_log_export.py\`, \`test_csv_security.py\`)."
done

# Group 7: Orphaned follow-up PRs targeting non-main branches
FOLLOWUP_PRS=(225 226 228 233 259 301)
for pr in "${FOLLOWUP_PRS[@]}"; do
  echo "Closing PR #$pr (orphaned follow-up PR)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: This follow-up PR targets a non-main branch that is no longer active."
done

# Group 8: Other redundant PRs
OTHER_PRS=(193 194 214)
for pr in "${OTHER_PRS[@]}"; do
  echo "Closing PR #$pr (redundant/superseded)"
  gh pr close "$pr" --repo "$REPO" --comment "Closing: This change is either already implemented or superseded by other work in the codebase."
done

echo ""
echo "=== KEPT OPEN (potentially valid) ==="
echo "PR #238 - XSS fix in markdown conversion (may add value)"
echo "PR #241 - Test for process_url error (may cover uncovered edge case)"
echo "PR #265 - Path traversal fix (CLI-level, worth reviewing)"
echo "PR #287 - Terminal injection fix (worth reviewing)"
echo "PR #288 - ThreadPoolExecutor for batch (not implemented, could be useful)"
echo "PR #291 - Path traversal fix (CLI-level, worth reviewing)"
echo "PR #293 - Split long main function (refactoring, could be useful)"
echo "PR #307 - Path traversal + scheme validation (worth reviewing)"
echo ""
echo "Done! Closed $(( ${#EXCEPTION_PRS[@]} + ${#LOG_EXPORT_PRS[@]} + ${#GUI_PRS[@]} + ${#CI_PRS[@]} + ${#SECURITY_PRS[@]} + ${#TEST_PRS[@]} + ${#FOLLOWUP_PRS[@]} + ${#OTHER_PRS[@]} )) PRs, kept 8 open for review."

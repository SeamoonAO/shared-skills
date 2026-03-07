---
name: md-reformat
description: Reformat and reorganize Markdown documents for clarity and consistency with conservative editing. Use when you need to reorder sections by importance, fix heading numbering, normalize unordered lists and indentation, merge duplicate content, restructure paragraphs, resolve obvious logical conflicts, and correct clear typos, while preserving original meaning, detail, and citation links as much as possible.
---

# Markdown Reformat

Rework Markdown content into a cleaner, coherent structure while preserving the original intent.

Default to a conservative rewrite style: prioritize structure and readability improvements over content deletion.

## Goals

1. Reorganize heading hierarchy and section numbering, including priority-based reordering.
2. Normalize unordered list style and indentation.
3. Merge duplicate or near-duplicate content.
4. Restructure paragraph flow for better readability.
5. Resolve obvious logical conflicts.
6. Fix clear typos and obvious language errors.
7. Preserve original references and citation links unless removal is clearly justified.

## Workflow

1. Read the full document and map structure blocks: headings, topic clusters, duplicates, conflicts, and all citation/reference links.
2. Build a new outline using this order: core points first, summary before details, conclusion before expansion.
3. Standardize format:
   - Keep heading levels continuous (`#` to `####`) unless the source requires a specific structure.
   - Normalize numbering (for example `1.`, `1.1`, `1.1.1`) or repair the existing scheme.
   - Use `-` for unordered lists and fix nested indentation.
4. Consolidate content:
   - Merge repeated paragraphs; keep the clearer and more complete version.
   - For near-duplicates, keep one main statement and fold extras into concise supporting bullets.
   - Prefer content relocation over deletion.
   - If deleting text is unavoidable, only remove redundant wording, not unique facts/examples.
5. Repair logic:
   - Detect contradictions, claim-evidence mismatch, and timeline inconsistency.
   - If the correct fix is clear, apply it directly.
   - If uncertain, keep minimal edits and insert `<!-- TODO: author confirmation needed -->`.
6. Improve language: fix obvious typos, punctuation mistakes, and clear sentence-level issues.
7. Preserve references:
   - Keep all original links whenever possible, including inline and footnote-style links.
   - Do not drop links just because the linked sentence is moved.
   - Only remove links when they are exact duplicates with identical anchor context, and keep at least one surviving instance.
   - If link placement becomes ambiguous after merging, keep the link nearest to the original claim and add `<!-- TODO: verify citation placement -->` if needed.
8. Final check: numbering continuity, list indentation, transition quality, terminology consistency, and link retention integrity.

## Editing Rules

- Preserve core meaning and factual intent. Do not invent unsupported claims.
- Preserve original content coverage: do not remove unique claims, examples, or evidence unless the user explicitly requests heavy trimming.
- Prefer reordering and tightening over unnecessary full rewrites.
- Apply minimal-change edits to ambiguous logic points and leave explicit TODO notes.
- If the user provides a style guide or numbering convention, follow it first.
- Preserve citation/reference links by default; if any are removed, mention exactly why in `Change Summary`.

## Output Format

Return output in this order:

1. `## Reformatted Document`
2. Full Markdown body ready to replace the source
3. `## Change Summary`
4. 3-10 concise bullets covering reordering, deduplication, conflict handling, typo/language fixes, and citation/link handling
5. Optional `## Open Questions` when unresolved conflicts remain

## Quick Prompt Template

Use this execution prompt when the user request is brief:

```text
Please reformat the following Markdown document:
1) Reorder sections by importance and fix heading numbering;
2) Normalize unordered lists and indentation;
3) Merge duplicate content and restructure paragraphs;
4) Resolve obvious logical conflicts and correct clear typos;
5) Output: Reformatted Document + Change Summary + Open Questions (if any).
```

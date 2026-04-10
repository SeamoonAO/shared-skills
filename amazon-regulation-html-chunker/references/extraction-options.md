# Extraction Options

## Default Choice

Use the local parser in `scripts/chunk_amazon_help_html.py` as the default path.

Why:

- the files are already downloaded locally
- Amazon help pages use repeatable wrappers such as `help-content`
- local parsing removes the need for a hosted API
- this project now separates extraction from semantic chunking

Recommended workflow:

1. local script extracts a clean Markdown draft
2. script resolves `source_url` from `*_index.txt`
3. Codex reads the cleaned draft and performs semantic chunking manually in conversation

## Decision Guide

### 1. Local Amazon-specific parsing

Use when:

- the file is a downloaded Seller Central help page
- the DOM still contains `help-content`, `full-help-page`, or similar wrappers
- the goal is to remove Seller Central chrome and keep the policy body

Pros:

- best fit for the current dataset
- deterministic and local
- easy to debug with selectors
- works naturally with `us_index.txt`, `de_index.txt`, and future `*_index.txt`

Cons:

- tuned to Amazon help-page structure
- may need selector updates if Amazon changes the page template

### 2. Mozilla Readability

Use when:

- the page looks like one long article
- the Amazon-specific wrappers are missing
- you need a lightweight local fallback

Pros:

- strong article extraction heuristic
- simple local dependency

Cons:

- can over-prune list-heavy policy pages
- not ideal when you need to preserve structured subsections exactly

### 3. Trafilatura

Use when:

- you need a generic local extractor
- you want optional Markdown output from raw HTML

Pros:

- local library
- accepts HTML strings directly
- useful as a fallback when selector rules fail

Cons:

- generic extraction may flatten or drop policy structure
- often still needs post-processing for navigation-heavy layouts

### 4. Unstructured

Use when:

- you want typed document elements
- you may expand beyond Amazon pages later
- you want a richer intermediate representation

Pros:

- stronger partitioning model
- useful future path for broader document handling

Cons:

- heavier dependency footprint
- unnecessary for the current Amazon-specific extraction problem

### 5. Firecrawl

Use when:

- you are scraping live URLs instead of local HTML files
- you need a hosted remote fetch-and-clean service

Pros:

- convenient for live web capture
- can return Markdown, cleaned HTML, and raw HTML

Cons:

- network dependency
- cost trade-offs
- not the natural default for already-downloaded files

### 6. Diffbot

Use when:

- you explicitly want a managed extraction API
- you need hosted content extraction at scale

Pros:

- mature hosted extraction option
- can accept HTML directly

Cons:

- network dependency and cost
- generic managed extraction is not automatically better than local rules for this Amazon dataset

## Recommended Strategy

For this project:

1. use the local Amazon-specific parser first
2. generate a clean Markdown draft with `source_file` and `source_url`
3. let Codex perform the final semantic chunking manually
4. use generic extractors only if the Amazon-specific parser stops being reliable
5. consider hosted APIs only when the source format or acquisition model changes significantly

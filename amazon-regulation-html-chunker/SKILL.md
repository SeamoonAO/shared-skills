---
name: amazon-regulation-html-chunker
description: Use when building a two-stage Amazon regulation pipeline: LLM semantic chunking first, then per-chunk inverted-index final_terms generation.
---

# Amazon Regulation HTML Chunker

## Overview

This skill now uses a strict two-stage workflow:

1. Stage A: semantic chunking (doc-level subagents).
2. Stage B: inverted-index terms extraction (chunk-level subagents).

Regulation flow output keeps only `final_terms` per chunk. Do not output `final_title`.

## Required Contracts

### Stage A input (doc-level subagent)

- `page_profile`
- `chunk_packet`
- `seed_terms`
- `orchestration.prompt_template_path`
- `orchestration.subagent_model`

### Stage A output

```json
{
  "doc_id": "us_G200164370",
  "semantic_chunks": [
    {
      "chunk_id": "us_G200164370_c001",
      "heading": "Restricted Items",
      "heading_path": "Policy Title > Restricted Items",
      "chunk_text": "string",
      "chunk_source_url": "string",
      "prev_context": "string",
      "next_context": "string",
      "screening_relevance_score": 8,
      "screening_relevance_reason": "sale gating condition"
    }
  ]
}
```

`screening_relevance_score` is a `0-10` score for whether the chunk is worth inclusion in a vector store focused on prohibited-sale screening:

- `10`: explicit prohibition or direct screen-out rule
- `8-9`: hard sellability gate such as permit, approval, age limit, import requirement, or FBA restriction
- `6-7`: material compliance requirement that often affects listing eligibility
- `4-5`: supporting regulatory context
- `2-3`: generic labeling, packaging, logistics, or formatting detail
- `0-1`: resources, navigation, or boilerplate

### Stage B input (chunk-level subagent)

- `page_profile`
- `chunk_packet` (single chunk)
- `seed_terms` (for this chunk)
- `orchestration.prompt_template_path`
- `orchestration.subagent_model`

### Stage B output

```json
{
  "doc_id": "us_G200164370",
  "chunk_id": "us_G200164370_c001",
  "final_terms": ["动物相关禁售", "animal-related restricted product"]
}
```

## CLI Modes

Script: [chunk_amazon_help_html.py](/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py)

- `draft`: clean markdown draft
- `chunks`: rule chunk preview (debug only)
- `index-seed`: deterministic snapshot (legacy/reference)
- `llm-doc-packets`: generate Stage A doc-level packets
- `llm-task-manifest`: generate task manifest from Stage A or Stage B JSONL packets
- `llm-prompt-preview`: render markdown-first subagent input previews from Stage A or Stage B JSONL packets
- `llm-runner-inputs`: build final subagent runner inputs as `system template + --- + markdown input context`
- `llm-semantic-merge`: merge Stage A subagent outputs
- `semantic-excel-export`: export Stage A semantic chunks for review
- `llm-index-packets`: generate Stage B chunk-level packets from Stage A merged output
- `llm-results-merge`: merge Stage B `final_terms` outputs
- `excel-export`: export Stage B final terms to review XLSX
- `combined-review-export`: export one review XLSX with chunk, score, source_url, and final_terms

Default output root:  
`/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/output`

## Subagent Model Selection

The CLI now supports selecting the model intended for Stage A and Stage B subagents:

- flag: `--subagent-model`
- default: `GPT-5.3-Codex-Spark`

Supported values:

- `GPT-5.3-Codex-Spark`
- `GPT-5.4-Mini`
- `GPT-5.4`
- `GPT-5.3-Codex`
- `GPT-5.2`

The script normalizes these values into canonical model IDs inside packet `orchestration.subagent_model`, so manifests and runners can consume a stable value such as `gpt-5.4-mini`.

Capacity fallback is also supported:

- flag: `--fallback-subagent-models`
- default behavior:
  - if primary is `GPT-5.3-Codex-Spark`, fallback defaults to `GPT-5.4-Mini`
  - otherwise no fallback is added by default
- disable fallback explicitly with: `--fallback-subagent-models none`

The fallback chain is written into:

- `orchestration.fallback_subagent_models`
- `llm-task-manifest`
- `llm-runner-inputs` under `## Runner Hints`

## Stage B Threshold

Stage B now skips low-value chunks by default:

- flag: `--min-index-score`
- default: `5`

Meaning:

- chunks with `screening_relevance_score < 5` are not turned into Stage B index packets
- this keeps low-value packaging, labeling, logistics, disclaimer, and navigation chunks out of the vector-store pipeline by default

## End-to-End Commands

### 1) Build Stage A packets

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/tests/fixtures/amazon-drafts-us" \
  --input-format markdown \
  --mode llm-doc-packets \
  --subagent-model GPT-5.3-Codex-Spark
```

### 1.1) Build Stage A task manifest

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-task-manifest
```

### 1.2) Render markdown-first subagent previews

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-prompt-preview
```

### 1.3) Build final runner inputs

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-runner-inputs
```

### 2) Merge Stage A semantic chunk outputs

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.jsonl" \
  --mode llm-semantic-merge
```

### 3) Export Stage A semantic review Excel

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.jsonl" \
  --mode semantic-excel-export
```

The Stage A review Excel includes `screening_relevance_score` and `screening_relevance_reason` so we can judge chunk quality and vector-store necessity together.

## Execution Note

`llm-doc-packets` and `llm-index-packets` remain JSONL transport contracts for storage, merge, and task manifests.
For actual subagent execution, prefer markdown-first prompt previews generated by `--mode llm-prompt-preview`.
For final execution handoff, prefer `--mode llm-runner-inputs`, which writes one file per task containing:

- `## System Prompt Template`
- `---`
- `## Input Context`
- `## Execution Packet`

These previews intentionally omit transport-only noise such as:

- `chunk_source_url`
- `prev_context`
- `next_context`

For Stage A semantic chunking, the model should primarily read compact metadata plus regulation source markdown, not raw JSON.
For Stage B inverted-index generation, the model should primarily read compact metadata plus one semantic chunk, and use these Stage A carry-over hints only to calibrate density and noise:

- `bucket_hints`
- `screening_relevance_score`
- `screening_relevance_reason`

Task manifests now also expose:

- `prompt_template_path`
- `preview_markdown_path`
- `runner_input_path`
- `subagent_model`

Backlog entry point:

- [amazon-regulation-backlog.md](/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/docs/amazon-regulation-backlog.md)

### 4) Build Stage B per-chunk packets

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.semantic-merged.json" \
  --mode llm-index-packets \
  --min-index-score 5
```

### 4.1) Build Stage B task manifest

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-index-packets.jsonl" \
  --mode llm-task-manifest
```

### 5) Merge Stage B final_terms outputs

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-final-terms-results.jsonl" \
  --mode llm-results-merge
```

### 6) Export Stage B final_terms review Excel

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-final-terms-results.jsonl" \
  --mode excel-export
```

### 6.1) Export combined chunk + score + final_terms review Excel

```bash
python3 /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.semantic-merged.json" \
  --terms-input "/path/to/stage-b-final-terms-results.llm-merged.json" \
  --mode combined-review-export
```

The combined review Excel includes:

- `source_url`
- `chunk_text`
- `screening_relevance_score`
- `screening_relevance_reason`
- `final_terms`
- `final_terms_count`

If `--excel-output` is omitted, the default filename is `*.combined-review.xlsx`.

## Dependencies

See [requirements.txt](/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/requirements.txt):

- `beautifulsoup4`
- `lxml`
- `openpyxl`

## Prompt Templates

- Stage A semantic chunking:
  [subagent-stage-a-semantic-chunk-prompt.md](/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/references/subagent-stage-a-semantic-chunk-prompt.md)
- Stage B inverted-index terms:
  [subagent-stage-b-inverted-index-prompt.md](/Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/references/subagent-stage-b-inverted-index-prompt.md)

## Verification

```bash
python3 -m unittest discover -s /Users/aoshi/code/shared-skills/amazon-regulation-html-chunker/tests -p "test_*.py" -v
```

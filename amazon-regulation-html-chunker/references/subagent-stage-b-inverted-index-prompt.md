# Subagent Prompt Template - Stage B Inverted-Index Term Generation (Recall-Optimized)

You process exactly one chunk execution packet.

## Objective

Generate a high-recall, low-noise term list for regulation retrieval.
Primary goal: maximize downstream RAG recall quality for regulatory queries.

## Input

You will receive exactly one markdown-first execution packet containing:

- `## Minimal Metadata`
- `## Semantic Chunk`
- `## Seed Terms`

Use only this execution packet. Do not use external context.

Within `## Minimal Metadata`, treat these fields as calibration hints when present:

- `heading` / `heading_path`
- `bucket_hints`
- `screening_relevance_score`
- `screening_relevance_reason`

## Output Contract (Strict)

Return exactly one valid JSON object with exactly these keys:

```json
{
  "doc_id": "string",
  "chunk_id": "string",
  "final_terms": ["string", "string"]
}
```

Hard rules:

1. Output must be raw JSON only (no markdown fences, no commentary, no extra text).
2. `doc_id` and `chunk_id` must be copied exactly from canonical input paths:
   - `doc_id = Minimal Metadata.doc_id`
   - `chunk_id = Minimal Metadata.chunk_id`
3. `final_terms` must be an array of unique, non-empty strings.
4. No extra keys (forbidden: `final_title`, `notes`, `reasoning`, etc.).

## Term Generation Rules

### 1) Coverage-first taxonomy (include categories that appear in chunk/context)

Generate terms across all relevant categories present:

1. Regulatory anchors: regulation names, article/section/citation IDs, program names.
2. Scope and actors: regulated entities, roles, jurisdictions, marketplaces, product scopes.
3. Obligations and prohibitions: required actions, forbidden actions, compliance duties.
4. Objects and evidence: documents, certificates, forms, declarations, reports, records.
5. Conditions and thresholds: limits, units, dates, deadlines, frequency, triggers.
6. Exceptions and enforcement: exemptions, penalties, sanctions, removal/suspension conditions.
7. Domain entities: product classes, hazard classes, controlled substances/materials.

### 2) Bilingual recall

For each high-value concept:

1. Include source-language canonical term.
2. Include English equivalent term only when supported by chunk evidence or seed-term evidence.
3. If source is English and non-English term is explicitly present in chunk/seed/context, include both.
4. Do not invent unsupported multilingual terms.

### 3) Variant and synonym expansion (controlled)

For high-value terms, add safe variants when useful:

1. Acronym <-> expanded form.
2. Hyphen/space/concatenation variants.
3. Singular/plural variants for count nouns.
4. Common citation variants (for example: `Article 5`, `Art. 5`).
5. Spelling variants with clear regulatory equivalence (US/UK only when meaningful).

Limits:

1. Max 3 variants per concept.
2. Prefer precise multi-word phrases over broad single words.

### 4) Seed terms handling

1. Treat `seed_terms` as recall anchors.
2. Include relevant seed terms and useful normalized variants.
3. Exclude seed terms that are clearly generic noise.
4. Treat page-level or global seed terms as weak hints only. If a seed term is not supported by the chunk text, heading, or a concrete rule mentioned in the chunk, drop it.
5. Do not keep seed terms merely because they are top-level page entities, marketplaces, or broad domain categories.

### 5) Normalization and dedup (mandatory)

Normalize each candidate using this dedup key:

1. Unicode NFKC.
2. Trim leading/trailing punctuation and spaces.
3. Collapse repeated internal whitespace to one space.
4. Lowercase for comparison only.

Dedup by normalized key.
Keep both terms if they are cross-lingual equivalents (source + English), even if semantically similar.

### 6) Anti-noise constraints (mandatory)

Exclude:

1. Generic legal filler without specificity (for example standalone `policy`, `requirement`, `regulation`, `section`, `article`, `compliance`).
2. Layout/OCR artifacts, navigation text, boilerplate UI strings.
3. Orphan numbers/dates/units without regulatory context.
4. Terms shorter than 2 characters (except valid IDs/acronyms).
5. Extremely long low-signal phrases (>10 tokens) unless official regulation/program names.
6. Duplicates and near-duplicates that add no recall value.
7. Generic section labels or page titles that are not official regulatory names (for example `禁售商品示例`, `准售商品示例`, `食品和饮料`, `武器`).
8. Broad seed-only domain phrases without direct chunk evidence (for example `weapon-related product`, `firearm accessory`, `restricted weapon component` when the chunk does not itself express those phrases or a concrete equivalent).
9. Terms that merely restate structural headings or heading-path labels without adding retrieval specificity. If a candidate term is just the chunk heading, a heading-path component, or a generic wrapper around the real rule, drop it unless it is itself an official rule/program/citation name.
10. Exact generic selling-status section labels, even when they appear in the chunk text. Always delete these exact labels if they appear as standalone terms:
    - `禁售商品示例`
    - `禁止出售的商品示例`
    - `准售商品示例`
    - `条件性准售商品示例`
    - `我们的政策`
    - `我们的通用灯具政策`
    - `相关的亚马逊帮助页面`
    - `其他信息`
    - `其他资源`
    - `资源`
    - `不得在亚马逊上销售以下商品`
    - `不得销售以下商品`
    - `禁止销售以下商品`
    - `示例包括但不限于`
    - `亚马逊明确禁止使用以下成分`
    - `明确禁止使用以下成分`
    - `以下成分`
    - `亚马逊商城`
    - `违反本政策`
    - `销售此类商品`
    - `不提供赔偿`
    - `所采购和销售的商品`
    - `承诺辅助`
    - `child safety policy`
    - `toy compliance`
11. If a section label contains the real legal object, keep only the legal object. For example:
    - Bad: `禁售商品示例`
    - Good: `酒精饮料`
    - Bad: `准售商品示例`
    - Good: `硬币收藏品`
    - Bad: `不得在亚马逊上销售以下商品`
    - Good: `纸币`
    - Bad: `亚马逊明确禁止使用以下成分`
    - Good: `比马前列素`
12. For product-screening retrieval, exclude standalone enforcement-consequence terms unless they are necessary to express the regulated product/status itself. For example, drop standalone terms like `销售权限`, `销售权限被暂停`, `销售权限永久撤销`, `暂停`, `永久撤销`, `销毁库存`, `扣留汇款`, and `没收付款`; keep product/status terms like `召回商品`, `市场撤出`, `停止销售的商品`, or `被召回的商品`.

### 7) Cardinality and ordering

1. Target 24 to 72 terms when chunk evidence is rich.
2. If chunk evidence is sparse, return fewer terms and never pad with unsupported terms.
3. Order by retrieval utility:
   - exact regulatory anchors and named entities first,
   - then obligations/objects/threshold phrases,
   - then bilingual equivalents,
   - then controlled variants/synonyms.

### 8) Relevance-aware density calibration (mandatory)

Use `screening_relevance_score` only as an internal density and noise-control hint:

1. `8-10`: high sellability impact chunk. Expand more aggressively across relevant taxonomy buckets.
2. `5-7`: medium-value chunk. Keep good coverage, but prefer precision over broad variant dumping.
3. `3-4`: low-value supporting chunk. Stay conservative and keep mostly exact phrases plus a few strong variants.
4. `0-2`: navigation/disclaimer/background-style chunk. Return only a small set of exact regulatory anchors if clearly useful; otherwise stay very sparse.
4.1. For `0-2` chunks with no concrete regulatory anchor, exception, threshold, document, or named rule, returning `[]` is allowed and preferred over padding.
5. If `screening_relevance_reason` explains a concrete gate (for example license, age threshold, import approval, FBA restriction), prioritize terms around that gate.
6. If `bucket_hints` are present, use them to prioritize which taxonomy buckets deserve expansion first.

### 9) Recall enhancement progression (mandatory internal heuristic)

Build `final_terms` progressively instead of dumping all candidates at once.

1. Start with the highest-value anchors:
   - regulation names, policy names, article/section identifiers,
   - product or substance class names,
   - core prohibition/obligation phrases.
2. Then add terms from adjacent dimensions only when they contribute new retrieval coverage:
   - actors/scope,
   - conditions/thresholds,
   - exceptions/exemptions,
   - evidence/documents,
   - enforcement/consequences,
   - safe variants and bilingual equivalents.
3. For each added term or small term group, estimate its marginal recall enhancement on a 0%-100% scale.
4. Prefer terms with clearly additive recall value over near-duplicates.
5. Stop adding terms when marginal recall enhancement becomes low or repetitive, even if more candidate terms remain.
6. Do not output recall scores; use them only as an internal stopping heuristic.

## Final validation before output

1. JSON-only, single object, exact keys.
2. No `final_title`.
3. `final_terms` unique after normalization.
4. Terms are specific, bilingual where applicable, and recall-oriented with noise controlled.
5. The final list should reflect progressive recall gain, not exhaustive term dumping.
6. Low-relevance chunks should stay intentionally sparse rather than padded.
7. Do not leak generic page scope, section labels, or seed-only broad domain terms into `final_terms`.
8. If a term would still make sense after removing the current page title and section label, keep it; otherwise drop it.
9. Perform a final deletion pass over `final_terms`: remove any term that exactly equals a generic heading label listed in Anti-noise rule 10.
10. For chunks under `禁售商品示例` / `禁止出售的商品示例`, the useful terms are the prohibited product classes, materials, conditions, documents, and legal anchors, not the label itself.
11. For chunks introduced by lead-in text such as `不得在亚马逊上销售以下商品`, keep the listed prohibited items and conditions; delete the lead-in itself.
12. For chunks introduced by lead-in text such as `亚马逊明确禁止使用以下成分`, keep the actual banned ingredients or substances; delete the lead-in itself.

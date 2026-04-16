## System Prompt Template

# Subagent Prompt Template - Stage A Semantic Chunking (Recall-Optimized, Deterministic)

You process exactly one document execution packet.

## Objective

Maximize downstream RAG recall quality for regulation retrieval while preserving legal boundaries.
Coverage of enforceable meaning is higher priority than compression.

## Input

You will receive one markdown-first execution packet containing:

- `## Minimal Metadata`
- `## Regulation Source Markdown`

Closed-world rule:

- Use only this execution packet.
- Do not use external knowledge, web context, or assumptions.

## Non-negotiable invariants

1. Coverage completeness:
- Every non-empty retrieval-relevant statement in the regulation source markdown must appear in `chunk_text` of at least one semantic chunk.
- Retrieval-relevant includes: normative rules, definitions, scope notes, enforcement references, thresholds, dates, and exceptions.
- Do not silently omit clauses, definitions, scope constraints, thresholds, dates, or penalties.

2. Legal-boundary integrity:
- Do not merge text across different legal scopes when any boundary changes (see boundary rules below).

3. Source fidelity:
- `chunk_text` must stay faithful to source wording.
- Allowed edits: whitespace cleanup and harmless line-join normalization only.
- Forbidden: paraphrase, interpretation, inferred obligations, invented examples, invented headings.

4. Determinism:
- Traverse source in original order.
- Apply the same split/merge rules consistently.
- Output chunks in source order.
- `chunk_id` must be stable sequential IDs in this format: `<doc_id>#sc-0001`, `<doc_id>#sc-0002`, ...

5. Output discipline:
- Output semantic chunks only.
- Never output final terms or final titles.
- For each semantic chunk, output a `screening_relevance_score` from 0 to 10 and a short `screening_relevance_reason`.

## Legal boundary rules (split when any boundary changes)

Split into a new chunk when there is a change in any of:

- actor or subject (who must/may/must not do something)
- deontic force (obligation, prohibition, permission)
- condition or trigger (`if`, `when`, `unless`, etc.)
- exception/exemption/safe harbor
- jurisdiction, marketplace, region, or policy scope
- effective date, sunset date, version, or temporal applicability
- quantitative threshold, limit, fee, or required metric
- enforcement consequence, penalty, escalation, or reporting duty
- source URL (never mix multiple source URLs in one chunk)

## Regulation information buckets

Before splitting, scan the document using these buckets and use them as semantic anchors:

- regulatory anchors: regulation names, policy names, article/section/citation identifiers
- scope and actors: regulated entities, roles, jurisdictions, marketplaces, product scopes
- obligations and prohibitions: what must be done, what is forbidden, what is allowed
- conditions and thresholds: dates, limits, quantities, frequencies, triggers
- exceptions and exemptions: carve-outs, exclusions, safe-harbor conditions
- evidence and documents: certificates, reports, declarations, forms, records
- enforcement and consequences: penalties, suspension, removal, reporting, escalation
- domain entities: product classes, materials, substances, hazard types, logistics modes

If multiple buckets are tightly coupled in one legal unit, keep them together.
If bucket membership changes in a way that changes retrieval meaning, split into a new chunk.

## Granularity rules

- Default unit: one retrievable legal unit with its required qualifiers.
- Include directly attached condition/exception text needed for standalone retrieval.
- If a parent sentence scopes multiple child rules and children are split, duplicate only minimal parent scope text needed for each child to remain interpretable.
- Do not default to 1:1 packet replay. If a child rule would lose screening meaning without parent scope, inject the minimal parent scope text into that child chunk.
- Never emit a semantic chunk whose `chunk_text` is only a bare child bullet item when section scope changes sellability interpretation.
- Under headings such as `准售商品示例`, `禁售商品示例`, or other sellability example sections, default to the minimal retrievable form `section label + item text` unless a tighter parent sentence is required.
- Avoid dangling lead-ins such as `如下：`, `例如：`, `下列内容：` without the scoped content that follows.
- If a lead-in sentence introduces one semantic family but the following bullets shift to a different family, split before the shift and do not drag the lead-in sentence forward.
- If a lead-in sentence does not truthfully scope a child item, remove the lead-in from that chunk rather than copying it forward.
- Disclaimer, boilerplate, and generic compliance reminder text should remain separate from concrete sellability rules unless they are inseparable in source.
- When a disclaimer or generic compliance reminder appears immediately before a scoped example section, keep it as its own low-value chunk instead of prepending it to the first example item.
- If a draft chunk would mix low-value generic labeling details with high-value sellability gates, split them into separate chunks.
- Target `chunk_text` size: 500 to 1400 characters.
- Hard max: 2000 characters (split at nearest sentence/list boundary).
- Soft min: 180 characters; shorter is allowed only for atomic legal rules.
- Precedence rule: legal-boundary split rules always override size heuristics.
- Short chunks are acceptable when boundary constraints prevent safe merge.

## Deterministic procedure

1. Read all `chunk_packet` entries in input order.
2. Tag each entry with one or more regulation information buckets.
3. Identify candidate legal units using bucket shifts and legal boundary rules.
4. Split/merge with granularity rules.
5. Assign stable IDs in order: `<doc_id>#sc-0001`, `<doc_id>#sc-0002`, ...
6. Score each chunk for restricted-sale screening relevance using the rubric below.
7. Build fields per rules below.
8. Run internal validation checklist before output.

## Restricted-sale screening relevance rubric

Score each chunk for whether it should be included in a vector store focused on prohibited-sale or restricted-sale screening.

- `10`: explicit prohibition, ban, disallow rule, or direct screen-out outcome
- `8-9`: hard gating rule that often decides sellability, such as permits, certificates, approvals, age restrictions, import requirements, FBA prohibition, or decisive thresholds
- `6-7`: compliance requirement that materially affects listing eligibility or enforcement, such as registration, reporting, recordkeeping, mandatory inspections, or mandatory declarations
- `4-5`: useful regulatory context, scope, or anchors that may help screening but are not decisive on their own
- `2-3`: generic packaging, labeling, formatting, logistics, or operational detail with low direct screening value
- `0-1`: resources, navigation links, boilerplate disclaimers, or content with near-zero screening value

Calibration rule:

- Be conservative. Do not inflate scores.
- A regulation-applicability statement or general duty to comply should usually score `4-7`, not `8-9`, unless the text itself states a concrete permit, certificate, approval, or hard threshold.
- Generic labeling fields like product name, net weight, ingredient order, operator info, language requirement, and similar packaging details should usually score `0-3`, not `6+`.
- Generic shipping, delivery, packing, or labeling requirement summaries without a decisive threshold or gate should usually score `2-4`, not `5+`.
- Chunks like `商品配送和贴标要求`, cargo label field lists, sender/recipient identification fields, or general state/local labeling reminders should usually stay below `5` unless the text itself contains a hard sellability gate.
- Treat basic sender/recipient/address/origin/declaration field lists as low-value operational compliance by default. Even if the wording uses `必须`, score these chunks `2-4` unless the same chunk also contains a decisive import gate, certification requirement, inspection requirement, explicit prohibition, or concrete enforcement consequence.
- Do not treat generic `配送和贴标要求` or `强制性配送和贴标要求` headings as high-value by themselves. Score must follow the legal consequence in the body, not the apparent strength of the heading label.
- Disclaimer, policy-reminder, and general-compliance text should usually score `0-2`, unless it directly contains a prohibition or hard sellability gate.
- If uncertain between two bands, choose the lower band unless the chunk clearly determines allowed vs disallowed sale.

## Few-shot calibration

Bad example:

- Source:
  - `所有食品包装都必须包括下列内容：`
  - `- 批次控制的商品保质期需大于 90 天。`
  - `- 食用燕窝，并附有联邦要求的进口许可或证书。`
- Bad chunk:
  - `所有食品包装都必须包括下列内容： 批次控制的商品保质期需大于 90 天。 食用燕窝，并附有联邦要求的进口许可或证书。`
- Why bad:
  - The lead-in sentence does not actually scope all following bullets; it creates a false legal unit.

Good example:

- Good chunks:
  - `准售商品示例：批次控制的商品保质期需大于 90 天。`
  - `准售商品示例：食用燕窝，并附有联邦要求的进口许可或证书。`

Bad example:

- Source:
  - `配送和贴标要求：每个商品货件必须具有：发货人或所有人的名称和地址；货件收货人的姓名；内含物产地国家、州或地区的名称；内含物声明。`
- Bad score:
  - `7`
- Why bad:
  - This is still a generic label-and-shipping field list. It matters operationally, but by itself it does not create a decisive prohibited-sale or restricted-sale gate.

Good example:

- Good score:
  - `3` or `4`
- Why good:
  - The chunk is retained for context, but it stays below the vector-store threshold unless paired with a concrete inspection, permit, approval, or prohibition rule.

Bad example:

- Source child bullet:
  - `- 软气枪的 BB 或子弹`
- Bad chunk:
  - `- 软气枪的 BB 或子弹`
- Why bad:
  - Bare child item loses whether it is allowed, prohibited, or conditional.

Good example:

- Good chunk:
  - `准售商品示例：软气枪的 BB 或子弹`

Bad example:

- Source:
  - `以下信息仅作为指南参考。`
  - `提醒：所有商品信息和商品均须遵守所有适用法律法规。`
  - `## 准售商品示例`
  - `- 软气枪的 BB 或子弹`
- Bad chunk:
  - `以下信息仅作为指南参考。提醒：所有商品信息和商品均须遵守所有适用法律法规。准售商品示例：软气枪的 BB 或子弹`
- Why bad:
  - Low-value disclaimer text is incorrectly fused into a sellability example chunk.

Good example:

- Good chunks:
  - `以下信息仅作为指南参考。`
  - `提醒：所有商品信息和商品均须遵守所有适用法律法规。`
  - `准售商品示例：软气枪的 BB 或子弹`

Bad example:

- Source:
  - `## 禁售商品示例`
  - `- 炸药`
- Bad chunk:
  - `- 炸药`
- Why bad:
  - The item loses the minimal sellability frame that makes it directly retrievable as a prohibition.

Good example:

- Good chunk:
  - `禁售商品示例：炸药`

Bad example:

- Mixed chunk:
  - `商品名称... 净重... 成分声明... 进口商品必须接受二次检验...`
- Why bad:
  - Generic label fields and high-value import gate are mixed into one score band.

Good example:

- Good chunks:
  - `强制性配送和贴标要求：商品名称... 净重... 成分声明...`
  - `配送和贴标要求示例：入境货件...必须...二次检验`

## Field construction rules

- `doc_id`: copy from `## Minimal Metadata` `doc_id`; if absent, use empty string.
- `heading`: nearest specific heading for the chunk; if missing, inherit nearest ancestor heading; if none, use empty string.
- `heading_path`: heading hierarchy joined with ` > `; if unavailable, use empty string.
- `chunk_text`: faithful source text for the semantic unit.
- `chunk_source_url`: use empty string when execution packet does not include a source URL.
- `prev_context`: last 200 characters of previous chunk `chunk_text` (or empty string for first chunk).
- `next_context`: first 200 characters of next chunk `chunk_text` (or empty string for last chunk).
- `screening_relevance_score`: integer `0-10` using the rubric above.
- `screening_relevance_reason`: short phrase explaining why the score was assigned.

## Internal validation checklist (do not output this checklist)

- No retrieval-relevant statement omitted.
- No chunk crosses forbidden legal boundaries.
- No mixed source URLs in a chunk.
- Chunk order matches source order.
- No chunk is a bare child item when parent scope is required for screening interpretation.
- No chunk in a sellability-example section starts as a naked list item when `section label + item text` is needed for standalone retrieval.
- No generic labeling or resource chunk is scored too high.
- No disclaimer or boilerplate chunk is scored above `2` unless it contains a concrete prohibition or gate.
- No disclaimer or generic compliance reminder is fused into the first item of a following sellability-example section.
- No chunk keeps a dangling lead-in sentence with unrelated following bullets.
- JSON is valid and strict.

## Output JSON (strict)

Return one raw JSON object only. No markdown fences. No commentary.

Required shape (exact keys, no extras):

```json
{
  "doc_id": "string",
  "semantic_chunks": [
    {
      "chunk_id": "string",
      "heading": "string",
      "heading_path": "string",
      "chunk_text": "string",
      "chunk_source_url": "string",
      "prev_context": "string",
      "next_context": "string",
      "screening_relevance_score": 0,
      "screening_relevance_reason": "string"
    }
  ]
}
```

JSON rules:

- Use double-quoted keys and strings.
- No trailing commas.
- No additional top-level or item-level fields.
- If no retrieval-relevant text exists, output `"semantic_chunks": []`.

---

## Input Context

The content below is the markdown-first execution packet. Apply the system prompt template above to this input context only.

## Execution Packet

# 管件和卫生设备

## Minimal Metadata
- doc_id: us_GFVTL7E262KFAAXC
- marketplace: us
- source_file: us_管件和卫生设备_GFVTL7E262KFAAXC.html

## Regulation Source Markdown

如果您要在亚马逊商城发布商品，则必须遵守与这些商品和商品信息发布相关的所有适用法律、法规、标准以及我们的政策。

## 管件

管件是用于连接管道或管道系统各部分的组件。它们在管道系统的布局和功能中起着至关重要的作用，可以控制液体流向，调节或终止液体流动。管件示例包括但不限于阀门、管道适配器、套管和管帽。

## 卫生设备

卫生设备是管道系统的端点设备，一端连接供水系统，一端连接排水系统。卫生设备示例包括但不限于水槽、马桶、淋浴头、水龙头、热水器和垃圾处理器。

## 州级要求

某些州（如加利福尼亚州）对某些管件和卫生设备（如淋浴头和水龙头）规定了更严格的水效率和能效标准。销售伙伴必须确保商品符合这些本地要求。 有关更多信息，请参阅 加利福尼亚州法规 。

## 联邦标准

美国能源部 (DOE) 为某些管件和卫生设备（如淋浴头和水龙头）设定了效率标准。请确保您的商品符合这些标准。

## 测试和认证要求

针对需要满足节能标准的商品或设备，联邦法律要求生产商向美国能源部提交每种商品或设备的每个基本型号的认证报告和合规声明。必须使用美国能源部的在线认证工具 - 合规性认证管理系统 (CCMS) ，以电子方式向美国能源部提交所需报告。

通过合规性认证管理系统，美国制造商、进口商和第三方代表可以创建、提交和追踪他们的认证报告。同时，通过合规性认证管理系统，美国能源部能够快速有效地审核和评估合规性和认证信息。

您可以在 美国能源部的“标准和测试程序”页面 找到商品分类清单。

## 在美国能源部数据库中注册涵盖的商品

美国能源部在 合规性认证管理系统用户指南 （仅提供英文版）中，提供了有关在美国能源部数据库中注册商品的分步说明。

## 贴标和包装要求

- 准确的商品描述： 确保所有包装和营销材料准确描述商品功能，包括流速。

- 安装说明： 每件商品必须包含清晰全面的安装说明。

## 其他资源

- 标准和测试程序

- 实施、认证和执行

- 合规性认证管理系统 (CCMS)

- 合规性认证数据库

- 受限商品

## Notes
- This preview is markdown-first for subagent execution.
- Transport-only URL and adjacency metadata are intentionally omitted.

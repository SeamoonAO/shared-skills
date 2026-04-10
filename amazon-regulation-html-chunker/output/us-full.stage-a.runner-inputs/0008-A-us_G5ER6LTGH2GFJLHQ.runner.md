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

# 制冷剂： 臭氧消耗物质和替代品

## Minimal Metadata
- doc_id: us_G5ER6LTGH2GFJLHQ
- marketplace: us
- source_file: us_制冷剂：臭氧消耗物质和替代品_G5ER6LTGH2GFJLHQ.html

## Regulation Source Markdown

如果您要在亚马逊商城发布商品，则必须遵守与这些商品和商品信息相关的所有适用法律、法规、标准以及我们的政策。

在美国，破坏地球臭氧层的制冷剂（通常称为“臭氧消耗物质”）受美国国家环境保护局和美国一些州的监管。受监管的制冷剂包括美国国家环境保护局归为“I 类”或“II 类”臭氧消耗物质的物质、任何包含 I 类或 II 类臭氧消耗物质的物质，以及臭氧消耗物质的“替代品”，包括某些氢氟碳化合物。

详细说明：

- I 类和 II 类臭氧消耗物质： 美国国家环境保护局发布了 I 类和 II 类臭氧消耗物质的完整清单。

- 制冷剂替代品： 美国国家环境保护局发布了可接受、在使用限制下可接受或不可接受的臭氧消耗物质 制冷剂替代品 清单。制冷剂替代品分类广泛，通常包括用于冷却和传热的化学品和用作 I 类和 II 类臭氧消耗物质替代品的商品。

- 氢氟碳化合物： 美国国家环境保护局正在根据行业和最终用途（如家用冰箱和冰柜、住宅和轻型商业空调商品以及自动售货机）逐步减少消费和生产（包括进口） 清单中的氢氟碳化合物 ，并限制使用某些氢氟碳化合物（包括这些氢氟碳化合物的混合物）。氢氟碳化合物是一种以全球增温潜势值较高而为人所知的臭氧消耗物质制冷剂替代品。

除少数非常有限的例外情况外，仅可向经美国国家环境保护局批准的认证计划认证为技术人员的买家销售、分销或者供应销售或分销 I 类臭氧消耗物质、II 类臭氧消耗物质和制冷剂替代品。仅可在美国国家环境保护局“许可”与氢氟碳化合物法规以及其他要求保持一致的情况下，才可以销售、分销或者供应销售或分销清单中的散装氢氟碳化合物，即储存在运输或储存专用容器（如缸或罐）中的氢氟碳化合物。这些商品均不可在亚马逊商城销售。

销售和分销限制不适用于可用于冷却和传热的少数豁免物质。联邦法规规定的豁免制冷剂示例包括：

- 用作制冷剂的二氧化碳 (R-744)

- 用作制冷剂的氮气 (R-728)

- 装在容量不超过 2 磅（32 盎司）的带有自密封阀的容器中用于机动车空调的某些制冷剂替代品（不包括清单中的氢氟碳化合物）

州和当地法律也可能会禁止或限制在某些司法管辖区销售、分销或者供应销售或分销制冷剂。例如，华盛顿州颁布了《氢氟碳化合物 - 减排法》（《华盛顿州修订法典》第 70A.60 章），禁止销售和购买某些全球增温潜势值较高的氢氟碳化合物制冷剂，以及含有全球增温潜势值较高的制冷剂的非必要消费品（如气喇叭和噪声制造器）。加利福尼亚和纽约也颁布了法律，要求通过州级制冷剂法规来减少氢氟碳化合物排放。其他州也可能会有限制销售、分销或者供应销售或分销制冷剂的法律。

某些州已经发布了有关这些限制的法规和指导文件。例如，华盛顿生态部颁布了法规，进一步说明这些限制（《华盛顿行政法典》第 173-443 章），并且发布了 信息指南 ，以便公众可以更好地了解氢氟碳化合物法律法规。此外，该部门还在其 网站 上提供了有关该法律的信息。

同样，加州空气资源委员会（加州法典第17 编第 95371-95378 条）和纽约州环境保护局（纽约法典规则和条例第 6 编第 494 部分）都制定了州级法规，明令在州内禁止销售某些氢氟碳化合物和含氢氟碳化合物的商品，并在其网站上提供了有关法律和实施细则的更多信息。

其他州可能也制定了有关制冷剂限制的法规。

如果您在我们的商城中发布包含臭氧消耗物质的商品，则必须遵守所有联邦和州法律。

您不可销售法律禁止或限制向买家销售的商品，包括但不限于包含以下任何物质的商品：

- I 类或 II 类臭氧消耗物质

- 仅可向经认证的技术人员合法出售的制冷剂替代品

- 清单中的氢氟碳化合物

## 准售商品示例

- 遵守所有联邦、州以及地方法律法规（包括联邦《清洁空气法》《美国创新与制造法》以及相关的规则和通知）的制冷剂。

- 仅针对允许用途销售的豁免制冷剂，包括如果制冷剂不是 I 类或 II 类臭氧消耗物质，或目录中的氢氟碳化合物，则是装在容量不超过 2 磅（32 盎司）的自密封容器中用于机动车空调的制冷剂。这些商品必须明确注明制冷剂、用途、容器尺寸以及阀门类型。

- 冰箱、冰柜或包含制冷剂的其他组装商品或家电。

- 空制冷剂罐

## 禁售商品示例

- 任何 I 类或 II 类臭氧消耗物质

- 仅可向经认证的技术人员合法出售的制冷剂替代品

- 针对不允许用途销售的豁免制冷剂

- 清单中的氢氟碳化合物

- 美国联邦法典第 40 卷第 82 部分附录 U 和 V 中列出的商品和设备

## 其他资源

- 美国国家环境保护局关于臭氧消耗物质的指南 ，其中详细介绍了某些危险物质的运输要求

- 美国国家环境保护局重要新替代品政策政策计划

- 臭氧消耗物质法规

- I 类物质

- II 类物质

- 《美国创新与制造法》

- 美国国家环境保护局关于氢氟碳化合物的指南

- 美国国家环境保护局氢氟碳化合物法规

- 华盛顿州生态部氢氟碳化合物信息指南 （2024 年 3 月）

- 华盛顿州生态部网站上有关华盛顿氢氟碳化合物法的信息 。

- 华盛顿氢氟碳化合物法律

- 华盛顿氢氟碳化合物法规

- 加州空气资源委员会网站上有关氢氟碳化合物法规的信息

- 加利福尼亚州氢氟碳化合物法规

- 纽约环境保护部网站上有关氢氟碳化合物法规的信息

- 纽约氢氟碳化合物法规

## Notes
- This preview is markdown-first for subagent execution.
- Transport-only URL and adjacency metadata are intentionally omitted.

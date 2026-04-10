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

# 无线电射频装置

## Minimal Metadata
- doc_id: us_GHXJGN6T5K8HGGWW
- marketplace: us
- source_file: us_电子产品_无线电射频装置_GHXJGN6T5K8HGGWW.html

## Regulation Source Markdown

如果您要在亚马逊商城发布商品，则必须遵守与这些商品和商品信息相关的所有适用法律、法规、标准以及亚马逊政策。

## 我们的无线电射频装置政策

通常，您可以销售符合以下条件的无线电射频装置：合法销售、在其授权范围内运行、符合适用的行业标准，且不会对其他电子产品造成干扰。在美国，联邦通信委员会 (FCC) 负责对可以发射无线电波的电子装置（称为“无线电射频装置”或“RF 装置”）进行监管。这些装置可能会干扰已获授权的无线电通信，它们必须依据适当的联邦通信委员会程序获得授权，然后才能在美国推广和使用或进口至美国。

在亚马逊商城销售的无线电射频装置必须依据适当的联邦通信委员会设备授权程序获得授权。要了解更多信息，请参阅 美国联邦通信委员会设备授权 - 无线电射频装置 和 美国联邦通信委员会设备授权程序 。

需要美国联邦通信委员会授权的装置包括但不限于：

- Wi-Fi 装置

- 蓝牙装置

- 手机

- 具有蜂窝网络连接的电子平板电脑和其他装置

- 双向无线电和对讲机

- 自动识别系统 (AIS) 装置

- 广播发射机

- 信号增强器

仅允许销售美国联邦通信委员会 (FCC) 及其工程技术办公室 (OET) 知识数据库 (KDB) 中批准频率范围内的无线电射频装置。

自 2023 年 2 月 6 日起，经认定属于美国联邦通信委员会覆盖清单上的“覆盖”设备的任何设备不得获得该委员会的设备授权。要了解更多信息，请参阅 美国联邦通信委员会禁止对“覆盖”设备进行授权 。

## 针对亚马逊政策规定的可售商品的亚马逊合规性要求

您必须满足下列合规性要求：

要求 | 商品详情页面 | 合规信息

声明 | 必须符合的要求

商品详情页面

商品详情页面必须满足以下所有条件：

声明

声明必须满足以下所有条件：

- 商品信息不得声称商品可以在美国联邦通信委员会工程技术办公室知识数据库批准的频率范围之外运行

为确保您的商品符合要求，请检查您的无线电射频装置商品信息，并确认营销内容（如商品名称、图片、要点和描述）仅显示美国联邦通信委员会工程技术办公室知识数据库中批准的该装置的频率范围。要了解更多信息，请参阅 美国联邦通信委员会分步指南 。

## 亚马逊政策规定的禁售商品

我们必须确保买家在亚马逊商城找到的商品品类充足、安全可靠且符合相关法规要求。我们不允许发布或销售不合规的商品或禁售商品。

禁售商品包括但不限于：

- 需要获得美国联邦通信委员会认证但尚未获得此认证的无线电射频装置

- 需要根据供应商符合性声明 (SDoC) 程序获得授权但尚未通过供应商符合性声明 (SDoC) 和美国联邦通信委员会认证获得授权的无线电射频装置

- 宣称需要根据供应商符合性声明 (SDoC) 程序获得授权但在美国没有合规责任方的无线电射频装置

- 用于除海上航行安全通信以外的其他目的（如追踪渔网）的自动识别系统 (AIS) 装置

- 用于库房、体育场、机场、办公大楼、医院、隧道和校园等大型工业或商业空间的信号增强器

- 与民用波段无线电搭配使用的功率放大器

- 用于故意屏蔽、堵塞或干扰获得许可或授权的无线电通信的商品，例如手机干扰器、GPS 干扰器、激光干扰器、PCS 干扰器、雷达干扰器或 Wi-Fi 干扰器、GPS 中继器和雷达移频器

- 在 600 MHz 频段（617-652 MHz 和 663-698 MHz）或 700 MHz 频段 (698-806 MHz) 工作的无线麦克风

- 声称在美国联邦通信委员会工程技术办公室知识数据库批准的频率范围之外运行的无线电射频装置

## 提交申诉

如果您认为您的商品被错误地归为禁售商品，请通过 账户状况 提交申诉。

## 资源

- 亚马逊服务商业解决方案协议

- 移除库存概览

- 修复无在售信息的亚马逊库存

- 受限商品

- 服务提供商网络

## 其他资源

- 联邦通信委员会规章制度

- 联邦通信委员会有关无线电射频装置的信息

- 联邦通信委员会有关设备授权程序的信息

- 联邦通信委员会执法咨询

- 联邦通信委员会有关高频收发器的公告

- 联邦通信委员会有关信号干扰器的执法指南

- 联邦通信委员会有关信号增强器的信息

- 联邦通信委员会有关无线麦克风的信息

## Notes
- This preview is markdown-first for subagent execution.
- Transport-only URL and adjacency metadata are intentionally omitted.

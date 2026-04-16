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

# 汽车轮胎、轮毂和轮圈

## Minimal Metadata
- doc_id: us_GJQMR3AUDBH6RXR5
- marketplace: us
- source_file: us_汽车轮胎轮毂和轮圈_GJQMR3AUDBH6RXR5.html

## Regulation Source Markdown

亚马逊禁止销售需要注册的机动车。但是，您通常可以销售符合《联邦机动车安全标准》和《清洁空气法》等适用法律要求的汽车零部件以及其他汽车用品和户外动力车用品。

## 我们关于汽车轮胎、轮毂和轮辋的政策

轮胎、轮毂和轮辋必须满足以下合规性要求：

- 轮胎、轮毂和轮辋必须符合《联邦机动车安全标准》（其他要求如下所示）。

- 轮胎、轮毂、轮辋和车轮配件必须为全新、未使用且未破损，原始制造商标签或贴标必须完好无损。

- 禁止发布二手轮胎、轮毂、轮辋和车轮配件。

- 轮胎未曾安装在任何胎圈接触的轮毂或轮辋（用于支撑轮胎或内外胎总成的金属支架）之上。

- 轮胎必须具有未经修改的有效美国运输部轮胎识别号。

- 根据轮胎识别号中列出的制造日期，轮胎的销售日期必须在其制造日期三年内。

- 不应出售距离原始制造商的保修截止日期（如有）不足两年的轮胎。

- 要符合 轮胎注册要求 ，您必须：

## 《联邦机动车辆安全标准》(FMVSS) 的机动车设备

根据《机动车安全法》的规定，进口到美国或在美国销售的部分汽车用品必须经过认证，以符合所有适用的《联邦机动车安全标准》。适用于汽车轮胎、轮毂和轮辋的安全标准可能包括以下内容：

商品 | 法规和标准要求

汽车轮胎和轮辋 | 49 CFR 571.109 – 新型斜纹帘布充气轮胎和某些专用轮胎 49 CFR 571.110 – 适用于额定总重量 (GVWR) 不超过 10,000 磅的机动车的可选轮胎和轮辋 49 CFR 571.119 – 适用于摩托车和额定总重量超过 10,000 磅的机动车的新型充气轮胎 49 CFR 571.120 – 适用于额定总重量超过 10,000 磅的机动车的可选轮胎和轮辋 49 CFR 571.129 – 适用于乘用车的新型非充气轮胎 49 CFR 571.139 – 适用于轻型车的新型子午线充气轮胎

有关《联邦机动车安全标准》的更多信息，请参阅 美国国家公路交通安全管理局的《联邦机动车安全标准》 。

## 受《联邦机动车安全标准》约束的汽车轮胎和轮圈

此分类下的商品包括但不限于：

- 机动车（乘用车、公共汽车、摩托车、卡车和房车）轮胎

- 拖车轮胎

- 备用轮胎

- 四季轮胎和雪地轮胎

- 附带或不带轮胎的机动车轮圈和轮毂

- 设计或宣传在普通公路或高速公路上使用的任何轮胎

## 所需文件

如果您在我们的网站上发布汽车轮胎、轮毂和轮辋，则需要提交相应文件，证明您的商品符合适用的安全标准和法规。您需要为每个相关 ASIN 提交以下文件：

文件 1 ： 填写完整的亚马逊 《联邦机动车安全标准》合规证明 表，由商品制造商的授权代表签署；对于国外的商品制造商，则由商品制造商或备案进口商签署。合规证明中提供的商品信息（包括品牌、制造商、型号和尺寸）必须与该 ASIN 商品详情页面中的商品信息一致。

文件 2（仅限轮胎和轮毂）： 由内部或外部实验室出具的《联邦机动车安全标准》有效检测报告，确认商品已经过检测，符合所有适用《联邦机动车安全标准》的全部性能要求。《联邦机动车安全标准》检测报告中的商品信息（包括品牌、制造商、型号和尺寸）必须与该 ASIN 商品详情页面中的商品信息一致。

《联邦机动车安全标准》检测报告必须包含以下信息：

- 商品的制造商、型号和尺寸 注意： 同一型号和层级但尺寸不同的轮胎，只需提供一张检测报告。如果提交的检测报告涉及多个轮胎尺寸，请提交所需合规性文件的签名书面陈述，以验证同一型号（和层级）的 ASIN 与提供的详细信息之间的关系。

- 检测机构的名称和地址

- 涉及的已执行检测的适用安全标准

- 所有适用安全标准已通过检测的数据

对于带轮胎和轮辋的车轮总成，请参阅下方的 常见问题 ，了解特殊说明。

## 如何提交信息

要提交文件或就合规性要求提出申诉，请参阅 提交合规文件或对文件请求提出申诉 。

## 申请从亚马逊运营中心移除商品

仅限亚马逊配送 (FBA)：

如果您无法或不愿意就 ASIN 被禁止显示的问题提出申诉，您将有 30 天的时间来创建移除订单，将商品从亚马逊运营中心移除。

有关更多信息，请参阅以下帮助文章：

- 亚马逊服务商业解决方案协议

- 移除库存（概览）

- 修复无在售信息的亚马逊库存

## 违反政策

如果您未在适用的截止日期之前提供所需信息，我们可能会从亚马逊商城移除相关的商品信息。

## 其他资源

- 49 CFR 第 571 部分

- 美国国家公路交通安全管理局颁布的《联邦机动车安全标准》

- 美国国家公路交通安全管理局新颁布的制造商手册

- 美国国家公路交通安全管理局颁布的《联邦机动车安全标准》标准检测模板

- 管理您的合规性

- 受限商品

- 汽车用品分类准售和禁售商品列表

- 亚马逊服务商业解决方案协议

## 常见问题

如何得知我的汽车轮胎和轮辋是否获准发布？

如果您的商品符合要求，您将收到一封电子邮件通知。

如果我认为我的商品不受《联邦机动车安全标准》约束，该怎么办？

如果您认为自己的商品被误认定为需遵循《联邦机动车安全标准》，您可以前往“管理您的合规性”控制面板，点击【添加或申诉合规性】，然后点击【申诉请求】进行申诉。

如果我是转销商，而不是制造商或备案进口商，该怎么办？

如果您是转销商，则需要联系商品的制造商或备案进口商，获取所需文件。您可以将 合规证明 表发给制造商或备案进口商，由其进行填写。您也可以要求制造商或备案进口商提供《联邦机动车安全标准》检测报告的副本。 然后，您需要通过“管理您的合规性”门户提交由制造商或备案进口商填写完整的合规证明表以及《联邦机动车安全标准》检测报告，供亚马逊审核。

如果合规文件中的商品信息与 ASIN 商品详情页面中的信息不一致，该怎么办？

合规文件中的商品信息（如制造商、品牌、型号和尺寸）必须与商品详情页面中的商品信息一致。如果商品信息不一致，则需要更新商品详情页面，使其与经过检测和认证的商品的准确信息一致。如果 ASIN 详情页面上列出的详细信息无法更新，请提交带有合规文件的书面陈述并签名，以便验证您提供的所有详细信息之间的关系。

如果我的商品是带轮胎和轮辋的车轮总成，我需要提交哪些表单？

您需要按照上述要求，提交合规证明和《联邦机动车安全标准》检测报告。但是，对于车轮总成，请遵循以下特殊说明。

合格证书：

- 如果轮毂的制造商（或备案进口商）同时也是其总成中所用的 轮胎和轮辋 的制造商（或备案进口商），则仅需提供轮毂 ASIN 的合规证明。

- 如果轮胎和轮辋由不同实体制造或进口，您需要提供轮胎制造商（或进口商）和轮辋制造商（或进口商）的合规证明。

FMVSS 检测报告：

- 只需提供轮胎的《联邦机动车安全标准》检测报告。无需提交轮辋和全轮配置的检测报告。

## Notes
- This preview is markdown-first for subagent execution.
- Transport-only URL and adjacency metadata are intentionally omitted.

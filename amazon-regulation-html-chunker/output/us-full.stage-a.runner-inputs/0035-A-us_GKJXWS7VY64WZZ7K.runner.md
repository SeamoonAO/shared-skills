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

# 联邦排放 - 需要美国国家环境保护局合格证书的商品

## Minimal Metadata
- doc_id: us_GKJXWS7VY64WZZ7K
- marketplace: us
- source_file: us_联邦排放-需要美国国家环境保护局合格证书的商品_GKJXWS7VY64WZZ7K.html

## Regulation Source Markdown

如果您在亚马逊商城销售商品，则必须遵守适用于这些商品和商品信息的所有联邦、州和其他法律以及亚马逊政策。

在美国，《清洁空气法》规定，燃料动力发动机（包括作为其他产品组件的发动机）以及燃料动力和电动汽车的制造商或进口商在进入美国商业领域或进口到美国之前，必须获得美国国家环境保护局 (EPA) 颁发的合格证书，以证明其符合联邦排放要求。您有责任确定您在我们商城发布的任何商品是否需要提供美国国家环境保护局合格证书。

## 需要提供美国国家环境保护局合格证书的商品

需要提供美国国家环境保护局合格证书的商品示例包括：

- 燃油发动机

- 燃油驱动的割草机、吹叶机、链锯、碎木机和其他工具

- 燃油发电机

- 燃油驱动的船用发动机和舷外发动机

- 燃油驱动的电动自行车发动机套件

- 燃油驱动的越野摩托车、全地形车辆和越野多功能车

- 燃油驱动和电动公路摩托车

有关美国国家环境保护局合格证书认证程序的信息，请参阅 https://www.epa.gov/ve-certification

## 要求提供美国国家环境保护局合格证书的商品合规性

要发布需要美国国家环境保护局合格证书的商品，您必须提交向商品（或其组件发动机）签发的有效的美国国家环境保护局合格证书编号。如果未提供有效的美国国家环境保护局合格证书编号，则在提供有效编号之前，商品可能会被移除。 如果您没有美国国家环境保护局合格证书编号，请联系商品制造商或进口商以获取美国国家环境保护局合格证书编号。

我们还将接受有效的加利福尼亚州空气资源委员会 (CARB) 行政命令编号，以代替美国国家环境保护局合格证书，证明符合加州的排放要求。有关 CARB 行政命令的信息以及如何提交 CARB 行政命令编号的说明，请参阅 加利福尼亚州空气资源委员会 (CARB)

了解美国国家环境保护局合格证书和 CARB 合规性视频

本视频提供了有关如何确保符合美国国家环境保护局法规并成功更新合格证书编号或 CARB EO 编号的基本信息。

## 如何提交美国国家环境保护局合格证书编号

要为 单个商品 提交美国国家环境保护局合格证书编号，请完成以下步骤：

- 如果您没有美国国家环境保护局合格证书编号，请联系商品制造商或进口商以获取美国国家环境保护局合格证书编号。

- 登录卖家平台。

- 前往 库存 选项卡，然后选择 管理库存 。

- 找到要编辑的商品信息，并从其对应的下拉菜单中选择 编辑 。

- 在弹出的新选项卡中，导航至 安全与合规性 选项卡。

- 向下滚动至 合规性法规类型 ，然后选择 美国国家环境保护局合格证书 (CoC) 。

- 在 法规标识 框中，输入在合格证书文件中显示的美国国家环境保护局合格证书编号，包括合格证书编号中存在的破折号和句号。美国国家环境保护局合格证书编号示例包括 NCEXL0275AAH-008、CJDXL024074-026、DY9XL16.4CAA-002-R01、MBCXX.976CHF-005-R02

- 点击 保存并完成 。

要为 多个商品 提交美国国家环境保护局合格证书编号，请完成以下步骤：

- 如果您没有美国国家环境保护局合格证书编号，请联系商品制造商或进口商以获取美国国家环境保护局合格证书编号。

- 登录卖家平台。

- 前往 目录 选项卡，然后选择 批量上传商品 。

- 点击 下载库存文件 选项卡。

- 在 第 1 步： 选择您想要销售 的商品类型，在“搜索工具”框中输入您想要搜索的商品，然后点击 搜索 。

- 点击 选择 ，将想要的商品分类添加到库存文件模板中。

- 在 第 2 步： 选择模板 类型，选择 自定义模式 ，并从可用属性组选项中选择 基本 和 合规性 属性。

- 点击 添加至已选属性组 。

- 点击 生成模板 。这将生成一个 Excel 电子表格。

- 打开 Excel 电子表格。在 模板 选项卡中，在 卖家 SKU 列中输入需要更新的 SKU。

- 从 update_delete 列的下拉选项中选择 partial_update 。

- 导航至 安全与 合规性 部分，从合规性法规下的下拉列表中选择 美国国家环境保护局合格证书 (COC) 。

- 在 法规标识 列输入美国国家环境保护局合格证书编号，包括合格证书编号中存在的破折号和句号。美国国家环境保护局合格证书编号示例包括 NCEXL0275AAH-008、CJDXL024074-026、DY9XL16.4CAA-002-R01、MBCXX.976CHF-005-R02

- 创建库存文件后，请将文件保存为使用制表符分隔的文本 (.txt) 或 Excel (.xls) 格式。

- 前往 库存 选项卡，选择 批量上传商品 ，然后点击 上传库存文件 选项卡。

- 填写 上传文件 部分的字段，然后点击 上传 。

- 点击 监控上传状态 选项卡。您最新上传文件的日期、时间、批次编号、状态和结果均显示在此处。

- 每次上传后，点击 下载处理报告 ，查看处理报告。如果处理报告显示错误，请修改库存文件，然后重新上传。

如果我认为我的商品不需要提供美国国家环境保护局合格证书，该怎么办？

## 其他信息

- 受限商品

- 《清洁空气法》概述

- 车辆和发动机的美国国家环境保护局认证与合规性

- 加利福尼亚州空气资源委员会 (CARB)

## Notes
- This preview is markdown-first for subagent execution.
- Transport-only URL and adjacency metadata are intentionally omitted.

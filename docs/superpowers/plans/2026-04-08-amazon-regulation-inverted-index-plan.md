# Amazon Regulation Chunk Inverted Index Implementation Plan (Two-Stage)

## Summary

- 采用两阶段实现：
  - Stage A：先做 LLM 语义分段（文档级 subagent）。
  - Stage B：再做逐 chunk LLM 倒排索引词生成（chunk 级 subagent 并发）。
- 法规场景只输出 `final_terms`，不输出 `final_title`。
- 必须保证输入契约：`page_profile + chunk_packet + seed_terms`。

## Scope

- Script: `amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py`
- Skill doc: `amazon-regulation-html-chunker/SKILL.md`
- Agent metadata: `amazon-regulation-html-chunker/agents/openai.yaml`
- Tests: `amazon-regulation-html-chunker/tests/test_chunk_amazon_help_html.py`
- Skill docs: `amazon-regulation-html-chunker/docs/*`

## CLI Design

### Stage A

- `--mode llm-doc-packets`
  - 产文档级 subagent 输入包（每文档一条 JSONL）
- `--mode llm-semantic-merge`
  - 合并 Stage A subagent 语义分段结果
- `--mode semantic-excel-export`
  - 导出 Stage A chunk 验收 Excel

### Stage B

- `--mode llm-index-packets`
  - 从 Stage A merged 结果生成逐 chunk subagent 输入包
- `--mode llm-results-merge`
  - 合并 Stage B `final_terms` 结果
- `--mode excel-export`
  - 导出 Stage B `final_terms` 验收 Excel

## Contracts

### Stage A Subagent Input

- `page_profile`
- `chunk_packet`
- `seed_terms`

### Stage A Subagent Output

- `doc_id`
- `semantic_chunks[]`
  - `chunk_id/heading/heading_path/chunk_text/chunk_source_url/prev_context/next_context`

### Stage B Subagent Input

- `page_profile`
- `chunk_packet` (single chunk)
- `seed_terms`

### Stage B Subagent Output

- `doc_id`
- `chunk_id`
- `final_terms[]` (source language + English)

## Quality Gates

- 不传 `--mode` 时默认行为仍为 `draft`。
- Stage A 和 Stage B 都支持 JSON/JSONL 输入输出与批处理。
- Stage A chunk 能独立导出 Excel 审核。
- Stage B 结果具备低噪声、可检索、可落库属性。
- 全量 fixture 冒烟测试通过。

## Validation

```bash
python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py --help
python3 -m unittest discover -s amazon-regulation-html-chunker/tests -p "test_*.py" -v
```


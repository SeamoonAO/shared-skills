# Amazon 法规 LLM 两阶段实施说明（2026-04-08）

## 1. 最终流程

- **Stage A（语义分段）**：文档级 subagent 执行语义 chunk。
- **Stage B（倒排索引）**：chunk 级 subagent 并发生成 `final_terms`。

法规场景只输出 `final_terms`，不输出 `final_title`。

## 2. Stage A：语义分段

### 2.1 输入

- `page_profile`
- `chunk_packet`
- `seed_terms`
- `orchestration.prompt_template_path`
- `orchestration.subagent_model`

由 CLI 生成：`--mode llm-doc-packets`

### 2.2 输出（subagent）

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

其中 `screening_relevance_score` 用于判断该法规 chunk 是否值得纳入“禁售筛查向量库”：

- `10`：明确禁售、禁止销售、直接筛掉
- `8-9`：强准入门槛，如年龄限制、许可证、批准、进口要求、FBA 禁用、决定性阈值
- `6-7`：对上架资格有实质影响的合规要求，如注册、申报、报告、记录、强制检验
- `4-5`：辅助性法规背景、范围、锚点
- `2-3`：泛贴标、包装、物流、格式要求
- `0-1`：资源链接、导航项、免责声明、弱相关内容

### 2.3 Stage A 后处理（脚本）

- 合并：`--mode llm-semantic-merge`
- Excel 验收：`--mode semantic-excel-export`

`semantic-excel-export` 会导出：

- `screening_relevance_score`
- `screening_relevance_reason`

用于和 `chunk_text` 一起判断“分段质量 + 入库必要性”。

## 3. Stage B：逐 Chunk 倒排索引

### 3.1 输入（chunk 级 subagent）

由 Stage A merged 结果生成：`--mode llm-index-packets`

每条记录含：

- `page_profile`
- `chunk_packet`（单 chunk）
- `seed_terms`（该 chunk）
- `orchestration.prompt_template_path`
- `orchestration.subagent_model`

### 3.2 输出（subagent）

```json
{
  "doc_id": "us_G200164370",
  "chunk_id": "us_G200164370_c001",
  "final_terms": ["源语言术语", "english retrieval term"]
}
```

### 3.3 Stage B 后处理（脚本）

- 合并：`--mode llm-results-merge`
- Excel 验收：`--mode excel-export`

### 3.4 Stage B 入库阈值

默认情况下，只有 `screening_relevance_score >= 5` 的 semantic chunk 会进入 Stage B：

- CLI 参数：`--min-index-score`
- 默认值：`5`

这意味着以下低价值 chunk 默认不会再生成倒排索引：

- 泛配送/贴标字段
- 包装/物流/格式性要求
- 免责声明、导航、资源链接

如果需要临时放宽，可以显式传更低阈值，例如：

- `--min-index-score 4`

## 4. CLI 模式清单

脚本：`scripts/chunk_amazon_help_html.py`

- `llm-doc-packets`
- `llm-task-manifest`
- `llm-prompt-preview`
- `llm-runner-inputs`
- `llm-semantic-merge`
- `semantic-excel-export`
- `llm-index-packets`
- `llm-results-merge`
- `excel-export`
- `combined-review-export`

默认输出目录：`amazon-regulation-html-chunker/output`

## 4.1 Subagent 模型选择

CLI 新增：

- `--subagent-model`
- `--fallback-subagent-models`

默认值：

- `GPT-5.3-Codex-Spark`

当前支持：

- `GPT-5.3-Codex-Spark`
- `GPT-5.4-Mini`
- `GPT-5.4`
- `GPT-5.3-Codex`
- `GPT-5.2`

容量回退规则：

- 当主模型为 `GPT-5.3-Codex-Spark` 时，默认回退到 `GPT-5.4-Mini`
- 其他主模型默认不附带回退链
- 可显式覆盖，例如：
  - `--fallback-subagent-models GPT-5.4-Mini,GPT-5.2`
- 可显式关闭：
  - `--fallback-subagent-models none`

该信息会写入：

- `orchestration.fallback_subagent_models`
- `llm-task-manifest`
- `llm-runner-inputs` 的 `## Runner Hints`

脚本会把它规范化为稳定的 canonical model id，并写入：

- `orchestration.subagent_model`
- `llm-task-manifest.tasks[].subagent_model`

例如：

- `GPT-5.4-Mini -> gpt-5.4-mini`

## 4.1 Subagent Prompt 模板（RAG 召回优化版）

- Stage A 语义分段模板：`references/subagent-stage-a-semantic-chunk-prompt.md`
- Stage B 倒排索引模板：`references/subagent-stage-b-inverted-index-prompt.md`

两份模板都强调：

- 召回优先（coverage-first）
- 严格 JSON 输出
- 去噪与可复现约束
- Stage A 使用“法规信息桶”辅助语义分段
- Stage B 使用 `Recall Enhancement` 递进加词，边际收益低时停止扩词
- 两阶段输入包都内置 `orchestration.prompt_template_path`，便于调度层直接读取模板

## 5. 验收命令

```bash
python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "amazon-regulation-html-chunker/tests/fixtures/amazon-drafts-us" \
  --input-format markdown \
  --mode llm-doc-packets \
  --subagent-model GPT-5.3-Codex-Spark

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-task-manifest

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-prompt-preview

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-doc-packets.jsonl" \
  --mode llm-runner-inputs

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.jsonl" \
  --mode llm-semantic-merge

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.jsonl" \
  --mode semantic-excel-export

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.semantic-merged.json" \
  --mode llm-index-packets \
  --min-index-score 5

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-index-packets.jsonl" \
  --mode llm-task-manifest

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-index-packets.jsonl" \
  --mode llm-prompt-preview

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-index-packets.jsonl" \
  --mode llm-runner-inputs

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-final-terms-results.jsonl" \
  --mode llm-results-merge

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-b-final-terms-results.jsonl" \
  --mode excel-export

python3 amazon-regulation-html-chunker/scripts/chunk_amazon_help_html.py \
  --input "/path/to/stage-a-semantic-results.semantic-merged.json" \
  --terms-input "/path/to/stage-b-final-terms-results.llm-merged.json" \
  --mode combined-review-export
```

`combined-review-export` 会把 Stage A 和 Stage B 合并到一张校对表里，便于同时检查：

- `source_url`
- `chunk_text`
- `screening_relevance_score`
- `screening_relevance_reason`
- `final_terms`
- `final_terms_count`

默认文件名为 `*.combined-review.xlsx`。

## 6. JSONL vs Markdown 输入边界

- `JSONL` 是脚本层的存储/调度契约，用于 merge、manifest、回收结果。
- `Markdown` 才是推荐给 subagent 的认知输入形式。

新增 `--mode llm-prompt-preview` 后：

- Stage A 会输出“精简 metadata + 规则源文 markdown”的预览文件
- Stage B 会输出“精简 metadata + 单 chunk 文本 + seed_terms”的预览文件
- Stage B 的精简 metadata 还会带上：
  - `bucket_hints`
  - `screening_relevance_score`
  - `screening_relevance_reason`
- `llm-runner-inputs` 会进一步输出带显式分隔的最终执行文件：
  - `## System Prompt Template`
  - `---`
  - `## Input Context`
  - `## Execution Packet`

这些预览会故意省略如下噪音字段：

- `chunk_source_url`
- `prev_context`
- `next_context`

这样可以降低 token 消耗，也减少模型被 JSON 结构牵着走的问题。

## 7. Runner 执行边界

- Runner 不再把原始 JSON/JSONL 正文直接拼进 subagent 提示词。
- Stage A 的 runner 输入固定为：
  - `references/subagent-stage-a-semantic-chunk-prompt.md`
  - `llm-prompt-preview` 生成的 Stage A markdown
- Stage B 的 runner 输入固定为：
  - `references/subagent-stage-b-inverted-index-prompt.md`
  - `llm-prompt-preview` 生成的 Stage B markdown
- Stage B 会把 `screening_relevance_score` 当作倒排索引密度校准提示，而不是脚本侧硬过滤条件
- `llm-task-manifest` 现在会提供：
  - `prompt_template_path`
  - `preview_markdown_path`
  - `runner_input_path`
  - `subagent_model`

## 8. Backlog

后续待办集中记录在：

- `docs/amazon-regulation-backlog.md`

其中 SQLite 相关内容只作为中期候选，不进入当前实施范围。

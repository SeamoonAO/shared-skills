---
name: merge-drafts
description: 多稿合并技能。将多份草稿合并为一份高质量文章。阅读所有稿子，选最佳稿为基础，融合其他稿子的亮点和缺失内容，最终润色输出。当用户要求“合并稿子”、“合稿”、“merge drafts”、“把这几篇合成一篇”、“综合这几份稿子”时使用此技能。
---

# Merge Drafts

将多份草稿融合为一份完整、统一、高质量的终稿。

默认原则：融合而非拼接。优先统一文章逻辑、语气、结构与信息密度，而不是机械叠加段落。

## 输入要求

1. 提供两份及以上草稿。
2. 每份草稿应尽量完整，至少能体现其核心观点、结构或表达亮点。
3. 如果用户提供了目标受众、风格要求、字数限制或用途，优先遵循这些约束。

## 工作流程

1. 通读所有稿件，分别判断每份稿子的优点、缺点、信息密度、结构完整性与语言质量。
2. 选出最适合作为主底稿的一份：
   - 优先选结构最清晰、逻辑最稳、可扩展性最强的版本。
   - 不一定选语言最华丽的版本，而是选最适合承载最终整合的版本。
3. 提取其他稿件中的亮点内容：
   - 更好的标题、开头、论点、例子、证据、结尾、表达方式。
   - 主底稿缺失但其他稿件补充到位的信息。
4. 开始融合：
   - 补充缺失信息。
   - 用更好的表达替换弱表达。
   - 删除重复、冲突或低价值内容。
   - 统一术语、口吻、段落节奏与叙述视角。
5. 完成润色：
   - 让全文像一位作者一次写成，而不是多稿拼接。
   - 修正明显重复、跳跃、风格断裂、语病和赘余。
6. 输出结果与简要说明：
   - 给出最终合并稿。
   - 说明选哪份为基础、吸收了其他稿子的哪些亮点。

## 关键原则

- 先选主底稿，再融合，避免平均拼接。
- 保留最强观点、最强表达和最完整信息。
- 如果多稿存在冲突，优先保留逻辑更完整、证据更充分、与用户目标更一致的版本。
- 如果无法判断哪种表述更准确，保守处理，并用 `<!-- TODO: author confirmation needed -->` 标记。
- 若用户额外指定风格控制类 skill，可在最终润色阶段调用，例如 `writing-style`。

## 输出格式

按以下顺序输出：

1. `## Merged Draft`
2. 最终合并后的完整文章
3. `## Merge Notes`
4. 3-6 条简要说明，包含：
   - 以哪份稿子为基础
   - 融合了哪些关键亮点
   - 删除了哪些重复或冲突内容
5. 如有未决冲突，再输出 `## Open Questions`

## 快速执行模板

```text
Please merge these drafts into one polished article:
1) Read all drafts and evaluate their strengths and weaknesses;
2) Choose the best draft as the base;
3) Merge the best parts and missing content from the others;
4) Ensure the final article feels unified rather than stitched together;
5) Output: Merged Draft + Merge Notes + Open Questions (if any).
```

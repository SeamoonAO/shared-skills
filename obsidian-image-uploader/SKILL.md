---
name: obsidian-image-uploader
description: 为包含本地图片的 Obsidian Markdown 构建或扩展自动上传组件，并把图片替换为图床 URL 或 X media_id。默认使用通用 S3 配置。用于用户要求“上传 Markdown 图片到图床”“处理 Obsidian ![[image.png]]/Markdown 图片语法”“把本地文章转成可发布版本”“实现 S3/R2/s.ee/GitHub/Medium/X 图片上传策略”时。
---

# Obsidian Image Uploader

实现一个高内聚、低耦合的 TypeScript 组件，把本地 Obsidian Markdown 中的图片批量上传到图床，并输出可发布的新 Markdown 副本。

优先复用 [assets/template](./assets/template) 里的项目骨架；只在用户已有项目约束明显不同的时候再按需改写。模板已包含策略接口、工厂、`S3`、`R2` 与 `s.ee` 的实现、其余平台的适配器骨架、配置加载、Markdown 解析与并发上传处理，并提供正式的 `MOCK`/`--dry-run` 验收模式。

## 工作流程

1. 确认输入与输出。
   - 输入通常是一个或多个本地 `.md` 文件，且图片语法可能混用 `![[image.png]]` 与 `![alt](image.png)`。
   - 输出通常是与原文件同目录的新副本，默认以 `_post.md` 结尾；如目标是 X，还需要把 `media_id` 注入 Frontmatter。
2. 先读模板结构，再决定是否直接复制。
   - 目录结构和核心代码在 [assets/template](./assets/template)。
   - 多平台上传差异、限流与鉴权说明在 [references/provider-notes.md](./references/provider-notes.md)。
3. 默认使用通用 `S3` 配置。
   - 如果底层实际是 Cloudflare R2，也可以继续用 `S3` 模式，只要 endpoint 与公网域名配对。
   - 若用户明确指定其他平台，再切换 `UploaderFactory` 默认值或 CLI 参数。
4. 实现时保持以下边界：
   - `UploaderStrategy` 只负责单文件上传。
   - `MarkdownProcessor` 只负责提取、去重、并发、替换、Frontmatter 注入。
   - `index.ts` 只负责 CLI 参数、配置加载和输出落盘。
5. 交付前至少验证：
   - `![[foo.png]]` 被标准化为 `![foo](https://...)`
   - 相对路径按 Markdown 文件目录解析
   - Obsidian vault-root 相对路径能正确回退解析
   - 文件缺失时记录 warning 并跳过
   - 上传失败时不中断整篇处理，保留原始图片语法
   - X 模式下写入 `x_media_ids`

## 何时读取额外资源

- 需要直接产出代码时：读取 `assets/template` 下相关文件，优先复制并小改。
- 需要补第三方平台实现时：读取 [references/provider-notes.md](./references/provider-notes.md) 中对应 provider 说明。
- 需要解释配置项时：读取 [assets/template/config.example.yaml](./assets/template/config.example.yaml)。
- 需要引导用户完成真实配置时：读取 [references/config-guide.md](./references/config-guide.md)。

## 实施要求

- 使用 TypeScript，保持显式类型。
- 运行和示例命令优先使用 `bun`；只有用户环境不支持时再回退到 `node` 生态命令。
- 配置从 `config.yaml` 和环境变量读取，不要硬编码敏感信息。
- 真实密钥配置不要提交到 git。仓库内只保留 `config.example.yaml`；本地真实配置优先放 `~/.config/obsidian-image-uploader/config.yaml`，必要时再通过 `--config` 指定其他路径。
- 先提供 `--dry-run` 命令，等用户确认输出的 `_post.md` 正确后，再引导切换到真实 uploader。
- Obsidian 图片路径解析要同时支持：
  - Markdown 同目录相对路径
  - Obsidian 库根目录相对路径
  - 常见 `attachments/` 子目录回退
- 默认并发要保守，尤其是 `s.ee`、GitHub、X。
- 替换 Markdown 时优先保留原 alt 文本；Obsidian 语法没有 alt 时，用文件名去扩展名作为 alt。
- 默认输出文件名规则为 `<原文件名>_post.md`，保留原始 Markdown 不覆盖。
- 如果用户只要求最小可用版本，至少交付：
  - `UploaderStrategy`
  - `UploaderFactory`
  - `R2Uploader`
  - `SeeUploader`
  - `MarkdownProcessor`
  - `index.ts`

## 输出建议

默认给出：

1. 目录结构
2. 核心接口与类
3. 配置示例
4. `bun` 运行命令
5. 已覆盖与未覆盖的平台说明

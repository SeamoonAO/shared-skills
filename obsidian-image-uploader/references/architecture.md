# Template Architecture

```text
obsidian-image-uploader/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── architecture.md
│   └── provider-notes.md
└── assets/
    └── template/
        ├── config.example.yaml
        ├── package.json
        ├── tsconfig.json
        └── src/
            ├── index.ts
            ├── adapters/
            │   ├── GitHubUploader.ts
            │   ├── MediumUploader.ts
            │   ├── R2Uploader.ts
            │   ├── SeeUploader.ts
            │   └── XUploader.ts
            ├── core/
            │   ├── loadConfig.ts
            │   ├── logger.ts
            │   ├── MarkdownProcessor.ts
            │   └── UploaderFactory.ts
            └── types/
                └── index.ts
```

## 模块职责

- `types/`: 统一接口和配置类型。
- `adapters/`: 每个图床一个类，避免 provider 逻辑泄漏到处理层。
- `core/UploaderFactory.ts`: 根据配置实例化策略。
- `core/MarkdownProcessor.ts`: 提取图片、并发上传、替换链接、注入 Frontmatter，并生成默认的 `_post.md` 副本。
- `src/index.ts`: CLI 入口，示例命令优先按 `bun run` 组织。

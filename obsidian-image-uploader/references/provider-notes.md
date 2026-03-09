# Provider Notes

## 目标

给实现 Obsidian 图片上传组件的 Codex 一个最小但够用的 provider 选择与实现提示，避免把大量 API 文档塞进 `SKILL.md`。

## 通用规则

- `UploaderStrategy.upload(localFilePath)` 只做单文件上传，返回统一的 `UploadResult`。
- 上传器内部负责 provider 特有的鉴权、请求头、body 编码与结果解析。
- 优先返回稳定 URL；若 provider 只返回媒体标识，则返回 `type: "media_id"`。
- 命名建议使用内容哈希或时间戳前缀，避免覆盖。
- Markdown 侧的本地文件解析不要只假设“相对当前 `.md` 所在目录”；Obsidian 经常混用 vault-root 相对路径和 `attachments/` 目录。

## R2

- 使用 `@aws-sdk/client-s3`。
- 典型流程：
  1. 从 `config` 读取 endpoint / access key / secret / bucket / custom domain
  2. `PutObjectCommand` 上传文件内容
  3. 返回 `${customDomain}/${objectKey}`
- `customDomain` 末尾斜杠要修正。
- `ContentType` 用 `mime-types` 或自定义映射。

## s.ee / SM.MS

- 使用 `POST multipart/form-data` 上传。
- 常见 header：`Authorization: <token>`
- 成功响应里通常包含公网 `url`；重复上传也可能返回现有 `images` URL。
- 对 `code !== "success"` 或缺失 `url` 要抛错。

## GitHub

- 用 REST API `PUT /repos/{owner}/{repo}/contents/{path}`。
- body 里要放 Base64 内容和 commit message。
- 公开仓库可返回 `raw.githubusercontent.com` 或 jsDelivr CDN URL。
- 注意较严格的速率限制，默认并发建议 2。

## Medium

- 用 `POST /v1/images`。
- 返回 Medium CDN URL。
- token 放 `Authorization: Bearer ...`。

## X

- 上传接口返回 `media_id_string`，不是可嵌入公网 URL。
- `MarkdownProcessor` 需要把结果收集到 Frontmatter，例如：

```yaml
x_media_ids:
  - "1888888888888888888"
  - "1999999999999999999"
```

- Markdown 可保留占位协议，如 `![alt](x-media-id:1888...)`，供后续发帖组件识别。

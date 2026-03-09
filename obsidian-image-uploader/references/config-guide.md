# Config Guide

## 推荐先走的路径

1. 先用 `--dry-run` 跑通 Markdown 解析、路径解析和 `_post.md` 输出。
2. 再切到真实图床，默认优先用 `S3`。
3. 如果要一次性验证 5 个 provider，先跑 `smokeTest.ts`，再选一个稳定 provider 跑整篇文章。

## 配置文件放哪

- 提交到 git 的只有 `config.example.yaml`。
- 真实密钥配置建议放在 `~/.config/obsidian-image-uploader/config.yaml`。
- 如果你想为某个项目单独放配置，再使用 `--config /path/to/config.yaml` 显式指定。
- 默认加载顺序：
  1. `--config` 指定的路径
  2. 当前工作目录下的 `config.yaml`
  3. `~/.config/obsidian-image-uploader/config.yaml`

## 最小 `config.yaml`

```yaml
DEFAULT_UPLOADER: "S3"
CONCURRENCY: 3
OUTPUT_SUFFIX: "_post"
OBSIDIAN_VAULT_ROOT: "/absolute/path/to/your/obsidian/vault"
MOCK_BASE_URL: "https://cdn.example.com/mock"

S3_ENDPOINT_URL: "https://your-s3-endpoint.example.com"
S3_ACCESS_KEY_ID: "your_s3_access_key"
S3_SECRET_ACCESS_KEY: "your_s3_secret_key"
S3_BUCKET_NAME: "your_bucket"
S3_PUBLIC_BASE_URL: "https://your-public-cdn-domain"
S3_KEY_PREFIX: "obsidian"

R2_ENDPOINT: "https://<account_id>.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID: "your_access_key"
R2_SECRET_ACCESS_KEY: "your_secret_key"
R2_BUCKET_NAME: "your_bucket"
R2_CUSTOM_DOMAIN: "https://cdn.yourdomain.com"
R2_KEY_PREFIX: "obsidian"
```

## 干跑命令

```bash
bun run src/index.ts \
  --config ./config.yaml \
  --file "/path/to/article.md" \
  --dry-run
```

## 真实 R2 上传命令

```bash
bun run src/index.ts \
  --config ./config.yaml \
  --file "/path/to/article.md" \
  --uploader R2
```

## 真实 S3 上传命令

```bash
bun run src/index.ts \
  --config ./config.yaml \
  --file "/path/to/article.md" \
  --uploader S3
```

## 五图床 smoke test 命令

```bash
bun run src/smokeTest.ts \
  --config ./config.yaml \
  --markdown "/path/to/article.md"
```

如果只测一个 provider：

```bash
bun run src/smokeTest.ts \
  --config ./config.yaml \
  --markdown "/path/to/article.md" \
  --uploader R2
```

## R2 配置提示

- `R2_ENDPOINT`: Cloudflare R2 的 S3 endpoint，不是公开 CDN 域名。
- `R2_CUSTOM_DOMAIN`: 你绑定到 bucket 的公开访问域名，输出 Markdown 时会用它拼接最终 URL。
- `R2_KEY_PREFIX`: 可选，建议填文章/仓库前缀，避免所有图片都堆在 bucket 根目录。

## 其他 provider 必填项

- `SEE`: `SEE_API_TOKEN`
- `GITHUB`: `GITHUB_PAT`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH`
- `MEDIUM`: `MEDIUM_INTEGRATION_TOKEN`
- `X`: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`

## S3 配置提示

- `S3_ENDPOINT_URL`: 真正的 S3/S3-compatible API endpoint。
- `S3_PUBLIC_BASE_URL`: 最终给 Markdown 用的公网前缀；如果你填的是私有 API endpoint，上传会成功，但图片仍会是破图。
- 如果底层其实是 R2，也可以把它走 `S3` uploader，只要 endpoint 和公网域名都配对即可。

## 并发建议

- `GITHUB`: 默认强制串行上传，避免 GitHub Contents API 在同一分支上出现 `409` 提交冲突。
- `SEE`: 建议并发不超过 `2`。

## X 的特殊说明

- X 上传成功后返回的是 `media_id`，不是可直接嵌入 Markdown 的 CDN 链接。
- 这是平台设计，不是模板限制。后续发帖要使用 `media_id`。

## 常见错误

- 上传成功但链接 404：通常是 `R2_CUSTOM_DOMAIN` 没绑定到 bucket，或者 CDN 规则未生效。
- 全部图片都提示 missing：通常是 `OBSIDIAN_VAULT_ROOT` 没指到 vault 根目录。
- 文章被覆盖：检查 `OUTPUT_SUFFIX`，默认应为 `_post`。

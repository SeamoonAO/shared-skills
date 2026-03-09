import fs from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";
import pLimit from "p-limit";
import { logger } from "./logger.js";
import type { AppConfig, MarkdownProcessResult, ProcessMarkdownOptions, UploadResult, UploaderName, UploaderStrategy } from "../types/index.js";

type ImageToken = {
  raw: string;
  source: string;
  alt: string;
};

const OBSIDIAN_IMAGE_REGEX = /!\[\[([^\]]+)\]\]/g;
const MARKDOWN_IMAGE_REGEX = /!\[([^\]]*)\]\(([^)]+)\)/g;

function normalizeObsidianTarget(target: string): string {
  return target.split("|")[0]?.trim() ?? target.trim();
}

function deriveAltText(source: string): string {
  return path.basename(source, path.extname(source));
}

function encodeMarkdownUrl(url: string): string {
  try {
    const parsed = new URL(url);
    parsed.pathname = parsed.pathname
      .split("/")
      .map((segment) => encodeURIComponent(decodeURIComponent(segment)))
      .join("/");
    return parsed.toString();
  } catch {
    return url.replace(/ /g, "%20");
  }
}

function extractImageTokens(markdown: string): ImageToken[] {
  const matches: ImageToken[] = [];

  for (const match of markdown.matchAll(OBSIDIAN_IMAGE_REGEX)) {
    const source = normalizeObsidianTarget(match[1] ?? "");
    matches.push({
      raw: match[0],
      source,
      alt: deriveAltText(source)
    });
  }

  for (const match of markdown.matchAll(MARKDOWN_IMAGE_REGEX)) {
    const source = (match[2] ?? "").trim();
    if (/^(https?:)?\/\//i.test(source) || source.startsWith("data:")) {
      continue;
    }
    matches.push({
      raw: match[0],
      source,
      alt: (match[1] ?? "").trim() || deriveAltText(source)
    });
  }

  return matches;
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function injectFrontmatter(markdown: string, mediaIds: string[]): string {
  if (mediaIds.length === 0) {
    return markdown;
  }

  const parsed = matter(markdown);
  const existing = Array.isArray(parsed.data.x_media_ids) ? parsed.data.x_media_ids.map(String) : [];
  parsed.data.x_media_ids = [...existing, ...mediaIds];
  return matter.stringify(parsed.content, parsed.data);
}

function getDefaultOutputPath(filePath: string, suffix: string): string {
  const parsed = path.parse(filePath);
  const normalizedSuffix = suffix || "_post";
  return path.join(parsed.dir, `${parsed.name}${normalizedSuffix}${parsed.ext || ".md"}`);
}

function getEffectiveConcurrency(config: AppConfig, uploaderName: UploaderName): number {
  if (uploaderName === "GITHUB") {
    return 1;
  }

  if (uploaderName === "SEE") {
    return Math.min(config.CONCURRENCY, 2);
  }

  return config.CONCURRENCY;
}

async function resolveLocalImagePath(filePath: string, source: string, vaultRoot?: string): Promise<string | undefined> {
  const candidates = new Set<string>();
  const markdownDir = path.dirname(filePath);

  if (path.isAbsolute(source)) {
    candidates.add(path.resolve(source));
  } else {
    candidates.add(path.resolve(markdownDir, source));
    candidates.add(path.resolve(markdownDir, "attachments", source));

    if (vaultRoot) {
      candidates.add(path.resolve(vaultRoot, source));
      candidates.add(path.resolve(vaultRoot, "attachments", source));
    }

    let currentDir = markdownDir;
    while (true) {
      candidates.add(path.resolve(currentDir, source));
      candidates.add(path.resolve(currentDir, "attachments", source));
      const parentDir = path.dirname(currentDir);
      if (parentDir === currentDir) {
        break;
      }
      currentDir = parentDir;
    }
  }

  for (const candidate of candidates) {
    if (await fileExists(candidate)) {
      return candidate;
    }
  }

  return undefined;
}

export class MarkdownProcessor {
  constructor(
    private readonly config: AppConfig,
    private readonly uploader: UploaderStrategy
  ) {}

  async process(options: ProcessMarkdownOptions): Promise<MarkdownProcessResult> {
    const filePath = path.resolve(options.filePath);
    const outputPath = options.outputPath ?? getDefaultOutputPath(filePath, this.config.OUTPUT_SUFFIX);
    const uploaderName = options.uploaderName ?? this.config.DEFAULT_UPLOADER;

    const original = await fs.readFile(filePath, "utf8");
    const tokens = extractImageTokens(original);
    const uniqueSources = [...new Set(tokens.map((token) => token.source))];
    const limit = pLimit(getEffectiveConcurrency(this.config, uploaderName));
    const results = new Map<string, UploadResult>();

    await Promise.all(
      uniqueSources.map((source) =>
        limit(async () => {
          const resolvedPath = await resolveLocalImagePath(filePath, source, this.config.OBSIDIAN_VAULT_ROOT);
          if (!resolvedPath) {
            logger.warn(`Skip missing image: ${source}`);
            return;
          }

          try {
            const result = await this.uploader.upload(resolvedPath);
            results.set(source, result);
            logger.info(`Uploaded ${source} -> ${result.value}`);
          } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            logger.warn(`Upload failed for ${source}: ${message}`);
          }
        })
      )
    );

    const xMediaIds: string[] = [];
    let content = original;
    const uploads: MarkdownProcessResult["uploads"] = [];

    for (const token of tokens) {
      const result = results.get(token.source);
      if (!result) {
        continue;
      }

      const replacement =
        result.type === "url"
          ? `![${token.alt}](${encodeMarkdownUrl(result.value)})`
          : `![${token.alt}](x-media-id:${result.value})`;

      if (result.type === "media_id") {
        xMediaIds.push(result.value);
      }

      content = content.replace(token.raw, replacement);
      uploads.push({
        source: token.source,
        replacement,
        result
      });
    }

    content = injectFrontmatter(content, xMediaIds);
    await fs.writeFile(outputPath, content, "utf8");

    return {
      content,
      outputPath,
      uploads
    };
  }
}

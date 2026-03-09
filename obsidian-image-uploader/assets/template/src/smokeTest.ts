import fs from "node:fs/promises";
import path from "node:path";
import { loadConfig } from "./core/loadConfig.js";
import { UploaderFactory } from "./core/UploaderFactory.js";
import type { UploaderName } from "./types/index.js";

const UPLOADERS: UploaderName[] = ["R2", "S3", "SEE", "GITHUB", "MEDIUM", "X"];

function readArg(flag: string): string | undefined {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function normalizeObsidianTarget(target: string): string {
  return target.split("|")[0]?.trim() ?? target.trim();
}

async function resolveLocalImagePath(markdownPath: string, source: string, vaultRoot?: string): Promise<string | undefined> {
  const candidates = new Set<string>();
  const markdownDir = path.dirname(markdownPath);

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

async function pickImageFromMarkdown(markdownPath: string, vaultRoot?: string): Promise<string> {
  const content = await fs.readFile(markdownPath, "utf8");
  const obsidianMatches = [...content.matchAll(/!\[\[([^\]]+)\]\]/g)];
  for (const match of obsidianMatches) {
    const source = normalizeObsidianTarget(match[1] ?? "");
    const resolved = await resolveLocalImagePath(markdownPath, source, vaultRoot);
    if (resolved) {
      return resolved;
    }
  }

  const markdownMatches = [...content.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g)];
  for (const match of markdownMatches) {
    const source = (match[2] ?? "").trim();
    if (/^(https?:)?\/\//i.test(source) || source.startsWith("data:")) {
      continue;
    }
    const resolved = await resolveLocalImagePath(markdownPath, source, vaultRoot);
    if (resolved) {
      return resolved;
    }
  }

  throw new Error(`No local image could be resolved from ${markdownPath}`);
}

async function main(): Promise<void> {
  const configPath = readArg("--config");
  const config = loadConfig(configPath ? path.resolve(configPath) : undefined);
  const explicitImage = readArg("--file");
  const markdownPath = readArg("--markdown");
  const uploaderArg = readArg("--uploader")?.toUpperCase() as UploaderName | undefined;

  const sampleFile = explicitImage
    ? path.resolve(explicitImage)
    : markdownPath
      ? await pickImageFromMarkdown(path.resolve(markdownPath), config.OBSIDIAN_VAULT_ROOT)
      : undefined;

  if (!sampleFile) {
    throw new Error("Usage: bun run src/smokeTest.ts --config ./config.yaml (--file ./image.png | --markdown ./article.md) [--uploader R2]");
  }

  const targets = uploaderArg ? [uploaderArg] : UPLOADERS;
  const results: Array<Record<string, string>> = [];

  for (const uploaderName of targets) {
    try {
      const uploader = UploaderFactory.create(uploaderName, config);
      const result = await uploader.upload(sampleFile);
      results.push({
        uploader: uploaderName,
        status: "ok",
        type: result.type,
        value: result.value
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      results.push({
        uploader: uploaderName,
        status: "error",
        message
      });
    }
  }

  console.log(JSON.stringify({ sampleFile, results }, null, 2));
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(message);
  process.exitCode = 1;
});

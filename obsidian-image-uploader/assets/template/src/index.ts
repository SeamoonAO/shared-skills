import path from "node:path";
import { loadConfig } from "./core/loadConfig.js";
import { MarkdownProcessor } from "./core/MarkdownProcessor.js";
import { UploaderFactory } from "./core/UploaderFactory.js";
import { logger } from "./core/logger.js";
import type { UploaderName } from "./types/index.js";

function readArg(flag: string): string | undefined {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function hasFlag(flag: string): boolean {
  return process.argv.includes(flag);
}

async function main(): Promise<void> {
  const file = readArg("--file");
  if (!file) {
    throw new Error("Usage: bun run src/index.ts --file ./draft.md [--uploader R2|S3|MOCK] [--dry-run] [--output ./draft_post.md]");
  }

  const configPath = readArg("--config");
  const config = loadConfig(configPath ? path.resolve(configPath) : undefined);
  const dryRun = hasFlag("--dry-run");
  const uploaderName = dryRun
    ? "MOCK"
    : (readArg("--uploader")?.toUpperCase() as UploaderName | undefined) ?? config.DEFAULT_UPLOADER;
  const outputPath = readArg("--output");

  const uploader = UploaderFactory.create(uploaderName, config);
  const processor = new MarkdownProcessor(config, uploader);
  const result = await processor.process({
    filePath: file,
    outputPath,
    uploaderName
  });

  if (dryRun) {
    logger.info("Dry-run mode enabled; no real image uploads were performed");
  }
  logger.info(`Processed ${result.uploads.length} images`);
  logger.info(`Output written to ${result.outputPath}`);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  logger.error(message);
  process.exitCode = 1;
});

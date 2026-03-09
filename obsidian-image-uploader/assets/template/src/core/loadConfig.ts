import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import dotenv from "dotenv";
import YAML from "yaml";
import type { AppConfig, UploaderName } from "../types/index.js";

const VALID_UPLOADERS = new Set<UploaderName>(["R2", "S3", "SEE", "GITHUB", "MEDIUM", "X", "MOCK"]);

function parseKeyValueConfig(raw: string): Record<string, string> {
  const result: Record<string, string> = {};
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    const separator = trimmed.includes("=") ? "=" : trimmed.includes(":") ? ":" : "";
    if (!separator) {
      continue;
    }
    const index = trimmed.indexOf(separator);
    const key = trimmed.slice(0, index).trim();
    const value = trimmed.slice(index + 1).trim().replace(/^["']|["']$/g, "");
    if (key) {
      result[key] = value;
    }
  }
  return result;
}

function readYamlConfig(configPath: string): Partial<AppConfig> {
  if (!fs.existsSync(configPath)) {
    return {};
  }

  const raw = fs.readFileSync(configPath, "utf8");
  try {
    return {
      ...parseKeyValueConfig(raw),
      ...(YAML.parse(raw) as Partial<AppConfig> | null)
    };
  } catch {
    return parseKeyValueConfig(raw) as Partial<AppConfig>;
  }
}

function normalizeUploader(value: string | undefined): UploaderName {
  const normalized = (value ?? "S3").toUpperCase() as UploaderName;
  if (!VALID_UPLOADERS.has(normalized)) {
    throw new Error(`Unsupported uploader: ${value}`);
  }
  return normalized;
}

export function loadConfig(configPath = path.resolve(process.cwd(), "config.yaml")): AppConfig {
  dotenv.config();

  const resolvedConfigPath = fs.existsSync(configPath)
    ? configPath
    : path.resolve(os.homedir(), ".config/obsidian-image-uploader/config.yaml");

  const yamlConfig = readYamlConfig(resolvedConfigPath);
  const merged = {
    ...yamlConfig,
    ...process.env
  } as Record<string, string | number | undefined>;

  return {
    DEFAULT_UPLOADER: normalizeUploader(String(merged.DEFAULT_UPLOADER ?? "S3")),
    CONCURRENCY: Number(merged.CONCURRENCY ?? 3),
    OUTPUT_SUFFIX: String(merged.OUTPUT_SUFFIX ?? "_post"),
    OBSIDIAN_VAULT_ROOT: merged.OBSIDIAN_VAULT_ROOT ? String(merged.OBSIDIAN_VAULT_ROOT) : undefined,
    MOCK_BASE_URL: merged.MOCK_BASE_URL ? String(merged.MOCK_BASE_URL) : undefined,
    S3_ENDPOINT_URL: merged.S3_ENDPOINT_URL ? String(merged.S3_ENDPOINT_URL) : undefined,
    S3_ACCESS_KEY_ID: merged.S3_ACCESS_KEY_ID ? String(merged.S3_ACCESS_KEY_ID) : undefined,
    S3_SECRET_ACCESS_KEY: merged.S3_SECRET_ACCESS_KEY ? String(merged.S3_SECRET_ACCESS_KEY) : undefined,
    S3_BUCKET_NAME: merged.S3_BUCKET_NAME ? String(merged.S3_BUCKET_NAME) : undefined,
    S3_PUBLIC_BASE_URL: merged.S3_PUBLIC_BASE_URL ? String(merged.S3_PUBLIC_BASE_URL) : undefined,
    S3_KEY_PREFIX: merged.S3_KEY_PREFIX ? String(merged.S3_KEY_PREFIX) : undefined,
    R2_ENDPOINT: merged.R2_ENDPOINT ? String(merged.R2_ENDPOINT) : undefined,
    R2_ACCESS_KEY_ID: merged.R2_ACCESS_KEY_ID ? String(merged.R2_ACCESS_KEY_ID) : undefined,
    R2_SECRET_ACCESS_KEY: merged.R2_SECRET_ACCESS_KEY ? String(merged.R2_SECRET_ACCESS_KEY) : undefined,
    R2_BUCKET_NAME: merged.R2_BUCKET_NAME ? String(merged.R2_BUCKET_NAME) : undefined,
    R2_CUSTOM_DOMAIN: merged.R2_CUSTOM_DOMAIN ? String(merged.R2_CUSTOM_DOMAIN) : undefined,
    R2_KEY_PREFIX: merged.R2_KEY_PREFIX ? String(merged.R2_KEY_PREFIX) : undefined,
    SEE_API_TOKEN: merged.SEE_API_TOKEN ? String(merged.SEE_API_TOKEN) : undefined,
    GITHUB_PAT: merged.GITHUB_PAT ? String(merged.GITHUB_PAT) : undefined,
    GITHUB_OWNER: merged.GITHUB_OWNER ? String(merged.GITHUB_OWNER) : undefined,
    GITHUB_REPO: merged.GITHUB_REPO ? String(merged.GITHUB_REPO) : undefined,
    GITHUB_BRANCH: merged.GITHUB_BRANCH ? String(merged.GITHUB_BRANCH) : undefined,
    GITHUB_BASE_PATH: merged.GITHUB_BASE_PATH ? String(merged.GITHUB_BASE_PATH) : undefined,
    GITHUB_CDN_BASE: merged.GITHUB_CDN_BASE ? String(merged.GITHUB_CDN_BASE) : undefined,
    MEDIUM_INTEGRATION_TOKEN: merged.MEDIUM_INTEGRATION_TOKEN ? String(merged.MEDIUM_INTEGRATION_TOKEN) : undefined,
    X_API_KEY: merged.X_API_KEY ? String(merged.X_API_KEY) : undefined,
    X_API_SECRET: merged.X_API_SECRET ? String(merged.X_API_SECRET) : undefined,
    X_ACCESS_TOKEN: merged.X_ACCESS_TOKEN ? String(merged.X_ACCESS_TOKEN) : undefined,
    X_ACCESS_SECRET: merged.X_ACCESS_SECRET ? String(merged.X_ACCESS_SECRET) : undefined
  };
}

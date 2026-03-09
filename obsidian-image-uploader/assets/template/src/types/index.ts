export type UploadResult =
  | { type: "url"; value: string }
  | { type: "media_id"; value: string };

export type UploaderName = "R2" | "S3" | "SEE" | "GITHUB" | "MEDIUM" | "X" | "MOCK";

export interface UploaderStrategy {
  upload(localFilePath: string): Promise<UploadResult>;
}

export interface AppConfig {
  DEFAULT_UPLOADER: UploaderName;
  CONCURRENCY: number;
  OUTPUT_SUFFIX: string;
  OBSIDIAN_VAULT_ROOT?: string;
  MOCK_BASE_URL?: string;
  S3_ENDPOINT_URL?: string;
  S3_ACCESS_KEY_ID?: string;
  S3_SECRET_ACCESS_KEY?: string;
  S3_BUCKET_NAME?: string;
  S3_PUBLIC_BASE_URL?: string;
  S3_KEY_PREFIX?: string;
  R2_ENDPOINT?: string;
  R2_ACCESS_KEY_ID?: string;
  R2_SECRET_ACCESS_KEY?: string;
  R2_BUCKET_NAME?: string;
  R2_CUSTOM_DOMAIN?: string;
  R2_KEY_PREFIX?: string;
  SEE_API_TOKEN?: string;
  GITHUB_PAT?: string;
  GITHUB_OWNER?: string;
  GITHUB_REPO?: string;
  GITHUB_BRANCH?: string;
  GITHUB_BASE_PATH?: string;
  GITHUB_CDN_BASE?: string;
  MEDIUM_INTEGRATION_TOKEN?: string;
  X_API_KEY?: string;
  X_API_SECRET?: string;
  X_ACCESS_TOKEN?: string;
  X_ACCESS_SECRET?: string;
}

export interface ProcessMarkdownOptions {
  filePath: string;
  outputPath?: string;
  uploaderName?: UploaderName;
}

export interface MarkdownProcessResult {
  content: string;
  outputPath: string;
  uploads: Array<{
    source: string;
    replacement: string;
    result: UploadResult;
  }>;
}

import fs from "node:fs/promises";
import path from "node:path";
import { PutObjectCommand, S3Client } from "@aws-sdk/client-s3";
import mime from "mime-types";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

function requireConfig(value: string | undefined, key: string): string {
  if (!value) {
    throw new Error(`Missing required config: ${key}`);
  }
  return value;
}

export class R2Uploader implements UploaderStrategy {
  private readonly client: S3Client;
  private readonly bucketName: string;
  private readonly customDomain: string;
  private readonly keyPrefix: string;

  constructor(private readonly config: AppConfig) {
    this.bucketName = requireConfig(config.R2_BUCKET_NAME, "R2_BUCKET_NAME");
    this.customDomain = requireConfig(config.R2_CUSTOM_DOMAIN, "R2_CUSTOM_DOMAIN").replace(/\/$/, "");
    this.keyPrefix = (config.R2_KEY_PREFIX ?? "obsidian").replace(/^\/+|\/+$/g, "");

    this.client = new S3Client({
      region: "auto",
      endpoint: requireConfig(config.R2_ENDPOINT, "R2_ENDPOINT"),
      credentials: {
        accessKeyId: requireConfig(config.R2_ACCESS_KEY_ID, "R2_ACCESS_KEY_ID"),
        secretAccessKey: requireConfig(config.R2_SECRET_ACCESS_KEY, "R2_SECRET_ACCESS_KEY")
      }
    });
  }

  async upload(localFilePath: string): Promise<UploadResult> {
    const body = await fs.readFile(localFilePath);
    const ext = path.extname(localFilePath).toLowerCase();
    const base = path.basename(localFilePath, ext);
    const objectKey = `${this.keyPrefix}/${base}-${Date.now()}${ext}`;

    await this.client.send(
      new PutObjectCommand({
        Bucket: this.bucketName,
        Key: objectKey,
        Body: body,
        ContentType: mime.lookup(localFilePath) || "application/octet-stream"
      })
    );

    return {
      type: "url",
      value: `${this.customDomain}/${objectKey}`
    };
  }
}

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

export class S3Uploader implements UploaderStrategy {
  private readonly client: S3Client;
  private readonly bucketName: string;
  private readonly publicBaseUrl: string;
  private readonly keyPrefix: string;

  constructor(private readonly config: AppConfig) {
    this.bucketName = requireConfig(config.S3_BUCKET_NAME, "S3_BUCKET_NAME");
    this.publicBaseUrl = (config.S3_PUBLIC_BASE_URL ?? config.S3_ENDPOINT_URL ?? "").replace(/\/$/, "");
    if (!this.publicBaseUrl) {
      throw new Error("Missing required config: S3_PUBLIC_BASE_URL or S3_ENDPOINT_URL");
    }
    this.keyPrefix = (config.S3_KEY_PREFIX ?? "obsidian").replace(/^\/+|\/+$/g, "");

    this.client = new S3Client({
      region: "auto",
      endpoint: requireConfig(config.S3_ENDPOINT_URL, "S3_ENDPOINT_URL"),
      credentials: {
        accessKeyId: requireConfig(config.S3_ACCESS_KEY_ID, "S3_ACCESS_KEY_ID"),
        secretAccessKey: requireConfig(config.S3_SECRET_ACCESS_KEY, "S3_SECRET_ACCESS_KEY")
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
      value: `${this.publicBaseUrl}/${objectKey}`
    };
  }
}

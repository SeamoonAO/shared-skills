import path from "node:path";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

export class MockUploader implements UploaderStrategy {
  constructor(private readonly config: AppConfig) {}

  async upload(localFilePath: string): Promise<UploadResult> {
    const baseUrl = (this.config.MOCK_BASE_URL ?? "https://cdn.example.com/mock").replace(/\/$/, "");
    return {
      type: "url",
      value: `${baseUrl}/${encodeURIComponent(path.basename(localFilePath))}`
    };
  }
}

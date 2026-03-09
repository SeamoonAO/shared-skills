import { GitHubUploader } from "../adapters/GitHubUploader.js";
import { MediumUploader } from "../adapters/MediumUploader.js";
import { MockUploader } from "../adapters/MockUploader.js";
import { R2Uploader } from "../adapters/R2Uploader.js";
import { S3Uploader } from "../adapters/S3Uploader.js";
import { SeeUploader } from "../adapters/SeeUploader.js";
import { XUploader } from "../adapters/XUploader.js";
import type { AppConfig, UploaderName, UploaderStrategy } from "../types/index.js";

export class UploaderFactory {
  static create(name: UploaderName, config: AppConfig): UploaderStrategy {
    switch (name) {
      case "R2":
        return new R2Uploader(config);
      case "S3":
        return new S3Uploader(config);
      case "SEE":
        return new SeeUploader(config);
      case "GITHUB":
        return new GitHubUploader(config);
      case "MEDIUM":
        return new MediumUploader(config);
      case "X":
        return new XUploader(config);
      case "MOCK":
        return new MockUploader(config);
      default:
        throw new Error(`Unsupported uploader strategy: ${String(name)}`);
    }
  }
}

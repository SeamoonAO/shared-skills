import path from "node:path";
import fs from "node:fs/promises";
import axios from "axios";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

export class MediumUploader implements UploaderStrategy {
  constructor(private readonly config: AppConfig) {}

  async upload(localFilePath: string): Promise<UploadResult> {
    if (!this.config.MEDIUM_INTEGRATION_TOKEN) {
      throw new Error("Missing required config: MEDIUM_INTEGRATION_TOKEN");
    }

    const file = await fs.readFile(localFilePath);
    const form = new FormData();
    form.append("image", new Blob([file]), path.basename(localFilePath));

    const response = await axios.post("https://api.medium.com/v1/images", form, {
      headers: {
        Authorization: `Bearer ${this.config.MEDIUM_INTEGRATION_TOKEN}`
      }
    });

    const payload = response.data as { data?: { url?: string; imageUrl?: string }; url?: string; imageUrl?: string };
    const url = payload.data?.url ?? payload.data?.imageUrl ?? payload.url ?? payload.imageUrl;
    if (!url) {
      throw new Error("Medium upload failed");
    }

    return {
      type: "url",
      value: url
    };
  }
}

import fs from "node:fs/promises";
import path from "node:path";
import axios from "axios";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

function requireToken(token: string | undefined): string {
  if (!token) {
    throw new Error("Missing required config: SEE_API_TOKEN");
  }
  return token;
}

export class SeeUploader implements UploaderStrategy {
  private readonly token: string;

  constructor(config: AppConfig) {
    this.token = requireToken(config.SEE_API_TOKEN);
  }

  async upload(localFilePath: string): Promise<UploadResult> {
    const file = await fs.readFile(localFilePath);
    const form = new FormData();
    form.append("smfile", new Blob([file]), path.basename(localFilePath));

    const response = await axios.post("https://smms.app/api/v2/upload", form, {
      headers: {
        Authorization: this.token
      }
    });

    const payload = response.data as {
      success?: boolean;
      code?: string;
      images?: string;
      data?: { url?: string };
      message?: string;
    };

    const url = payload.data?.url ?? payload.images;
    if ((!payload.success && payload.code !== "success") || !url) {
      throw new Error(payload.message ?? "s.ee upload failed");
    }

    return {
      type: "url",
      value: url
    };
  }
}

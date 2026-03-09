import fs from "node:fs/promises";
import path from "node:path";
import axios from "axios";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

export class GitHubUploader implements UploaderStrategy {
  constructor(private readonly config: AppConfig) {}

  async upload(localFilePath: string): Promise<UploadResult> {
    const { GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH, GITHUB_BASE_PATH, GITHUB_CDN_BASE } = this.config;
    if (!GITHUB_PAT || !GITHUB_OWNER || !GITHUB_REPO || !GITHUB_BRANCH) {
      throw new Error("Missing required GitHub uploader config");
    }

    const file = await fs.readFile(localFilePath);
    const ext = path.extname(localFilePath).toLowerCase();
    const base = path.basename(localFilePath, ext);
    const remotePath = `${GITHUB_BASE_PATH ?? "images"}/${base}-${Date.now()}${ext}`;

    await axios.put(
      `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${remotePath}`,
      {
        message: `upload ${remotePath}`,
        content: file.toString("base64"),
        branch: GITHUB_BRANCH
      },
      {
        headers: {
          Authorization: `Bearer ${GITHUB_PAT}`,
          Accept: "application/vnd.github+json"
        }
      }
    );

    return {
      type: "url",
      value:
        GITHUB_CDN_BASE?.replace(/\/$/, "")
          ? `${GITHUB_CDN_BASE.replace(/\/$/, "")}/${remotePath}`
          : `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GITHUB_BRANCH}/${remotePath}`
    };
  }
}

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import axios from "axios";
import mime from "mime-types";
import type { AppConfig, UploadResult, UploaderStrategy } from "../types/index.js";

const UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json";

function percentEncode(value: string): string {
  return encodeURIComponent(value)
    .replace(/[!'()*]/g, (char) => `%${char.charCodeAt(0).toString(16).toUpperCase()}`);
}

function buildOauthHeader(
  method: string,
  url: string,
  consumerKey: string,
  consumerSecret: string,
  accessToken: string,
  accessSecret: string,
  params: Record<string, string>
): string {
  const oauthParams: Record<string, string> = {
    oauth_consumer_key: consumerKey,
    oauth_nonce: crypto.randomBytes(16).toString("hex"),
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: accessToken,
    oauth_version: "1.0"
  };

  const signatureParams = {
    ...params,
    ...oauthParams
  };

  const normalized = Object.keys(signatureParams)
    .sort()
    .map((key) => `${percentEncode(key)}=${percentEncode(signatureParams[key] ?? "")}`)
    .join("&");

  const signatureBase = [
    method.toUpperCase(),
    percentEncode(url),
    percentEncode(normalized)
  ].join("&");

  const signingKey = `${percentEncode(consumerSecret)}&${percentEncode(accessSecret)}`;
  const signature = crypto.createHmac("sha1", signingKey).update(signatureBase).digest("base64");
  oauthParams.oauth_signature = signature;

  return `OAuth ${Object.keys(oauthParams)
    .sort()
    .map((key) => `${percentEncode(key)}="${percentEncode(oauthParams[key])}"`)
    .join(", ")}`;
}

export class XUploader implements UploaderStrategy {
  constructor(private readonly config: AppConfig) {}

  async upload(localFilePath: string): Promise<UploadResult> {
    if (!this.config.X_API_KEY || !this.config.X_API_SECRET || !this.config.X_ACCESS_TOKEN || !this.config.X_ACCESS_SECRET) {
      throw new Error("Missing required X uploader config");
    }

    const file = await fs.readFile(localFilePath);
    const mediaType = mime.lookup(localFilePath) || "application/octet-stream";
    const params = {
      media_data: file.toString("base64"),
      media_category: "tweet_image"
    };

    const authorization = buildOauthHeader(
      "POST",
      UPLOAD_URL,
      this.config.X_API_KEY,
      this.config.X_API_SECRET,
      this.config.X_ACCESS_TOKEN,
      this.config.X_ACCESS_SECRET,
      params
    );

    const response = await axios.post(
      UPLOAD_URL,
      new URLSearchParams(params).toString(),
      {
        headers: {
          Authorization: authorization,
          "Content-Type": "application/x-www-form-urlencoded",
          Accept: "application/json",
          "X-Upload-Content-Type": mediaType
        }
      }
    );

    const mediaId = (response.data as { media_id_string?: string }).media_id_string;
    if (!mediaId) {
      throw new Error(`X upload failed for ${path.basename(localFilePath)}`);
    }

    return {
      type: "media_id",
      value: mediaId
    };
  }
}

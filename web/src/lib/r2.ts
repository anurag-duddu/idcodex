import {
  GetObjectCommand,
  PutObjectCommand,
  HeadObjectCommand,
  S3Client,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

/** True for absolute http(s) storage keys (dev sample files, proxied as-is). */
export function isRemoteUrl(key: string): boolean {
  return /^https?:\/\//i.test(key);
}

type R2Config = {
  accessKeyId: string;
  secretAccessKey: string;
  bucket: string;
  endpoint: string;
};

/** Endpoint from R2_ENDPOINT, else derived from R2_ACCOUNT_ID. */
function resolveEndpoint(): string | undefined {
  if (process.env.R2_ENDPOINT) return process.env.R2_ENDPOINT;
  if (process.env.R2_ACCOUNT_ID)
    return `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`;
  return undefined;
}

function readR2Config(): R2Config {
  const cfg = {
    R2_ACCESS_KEY_ID: process.env.R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY: process.env.R2_SECRET_ACCESS_KEY,
    R2_BUCKET: process.env.R2_BUCKET,
    "R2_ENDPOINT or R2_ACCOUNT_ID": resolveEndpoint(),
  };
  const missing = Object.entries(cfg)
    .filter(([, v]) => !v)
    .map(([k]) => k);
  if (missing.length > 0) {
    throw new Error(`R2 not configured: missing ${missing.join(", ")}`);
  }
  return {
    accessKeyId: cfg.R2_ACCESS_KEY_ID!,
    secretAccessKey: cfg.R2_SECRET_ACCESS_KEY!,
    bucket: cfg.R2_BUCKET!,
    endpoint: cfg["R2_ENDPOINT or R2_ACCOUNT_ID"]!,
  };
}

/** True when all R2 credentials are present (endpoint may be derived). */
export function isR2Configured(): boolean {
  return (
    !!process.env.R2_ACCESS_KEY_ID &&
    !!process.env.R2_SECRET_ACCESS_KEY &&
    !!process.env.R2_BUCKET &&
    !!resolveEndpoint()
  );
}

let _client: S3Client | null = null;
let _bucket: string | null = null;

function client(): { s3: S3Client; bucket: string } {
  if (!_client) {
    const cfg = readR2Config();
    _client = new S3Client({
      region: "auto",
      endpoint: cfg.endpoint,
      credentials: {
        accessKeyId: cfg.accessKeyId,
        secretAccessKey: cfg.secretAccessKey,
      },
    });
    _bucket = cfg.bucket;
  }
  return { s3: _client, bucket: _bucket! };
}

/** A short-lived presigned GET URL for an R2 object key. */
export async function signedUrlFor(
  key: string,
  opts: { expiresIn?: number } = {},
): Promise<string> {
  const { s3, bucket } = client();
  return getSignedUrl(s3, new GetObjectCommand({ Bucket: bucket, Key: key }), {
    expiresIn: opts.expiresIn ?? 300,
  });
}

/** Upload bytes to R2 (used by migration + the future Contribute flow). */
export async function uploadToR2(
  key: string,
  body: Buffer | Uint8Array,
  contentType: string,
): Promise<void> {
  const { s3, bucket } = client();
  await s3.send(
    new PutObjectCommand({
      Bucket: bucket,
      Key: key,
      Body: body,
      ContentType: contentType,
    }),
  );
}

/** True if an object already exists at `key` (idempotent uploads). */
export async function existsInR2(key: string): Promise<boolean> {
  const { s3, bucket } = client();
  try {
    await s3.send(new HeadObjectCommand({ Bucket: bucket, Key: key }));
    return true;
  } catch {
    return false;
  }
}

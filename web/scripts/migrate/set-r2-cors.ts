import "dotenv/config";
import {
  S3Client,
  PutBucketCorsCommand,
  GetBucketCorsCommand,
  type CORSRule,
} from "@aws-sdk/client-s3";

/**
 * One-time: apply CORS to the R2 bucket so the browser can fetch the signed R2
 * URL that /api/file/[nodeId] 302-redirects to. R2 has NO CORS by default
 * (GetBucketCors -> NoSuchCORSConfiguration), so pdf.js's cross-origin fetch
 * (and its Range preflight, which 403s) is blocked → "Failed to fetch".
 *
 * This keeps the 302 redirect (preserves R2's $0 egress). <img>/<video> already
 * work across the redirect; this unblocks the pdf.js fetch() path.
 *
 * Wildcard origin is safe here: pdf.js fetches WITHOUT credentials and auth
 * lives in the signed-URL query string, so ACAO:* is not a credentialed-CORS
 * violation. It also covers dynamic *.vercel.app preview origins.
 *
 * Run:  npx tsx scripts/migrate/set-r2-cors.ts          # apply
 *       npx tsx scripts/migrate/set-r2-cors.ts --check  # print current config
 */

const endpoint =
  process.env.R2_ENDPOINT ??
  (process.env.R2_ACCOUNT_ID
    ? `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`
    : undefined);
const bucket = process.env.R2_BUCKET;
const accessKeyId = process.env.R2_ACCESS_KEY_ID;
const secretAccessKey = process.env.R2_SECRET_ACCESS_KEY;

if (!endpoint || !bucket || !accessKeyId || !secretAccessKey) {
  console.error(
    "R2 not configured — need R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, " +
      "and R2_ENDPOINT or R2_ACCOUNT_ID in the root .env.",
  );
  process.exit(1);
}

const s3 = new S3Client({
  region: "auto",
  endpoint,
  credentials: { accessKeyId, secretAccessKey },
});

const CORS_RULES: CORSRule[] = [
  {
    AllowedOrigins: ["*"],
    AllowedMethods: ["GET", "HEAD"],
    AllowedHeaders: ["Range", "If-Range", "If-None-Match", "If-Modified-Since"],
    ExposeHeaders: [
      "Content-Range",
      "Accept-Ranges",
      "Content-Length",
      "Content-Type",
      "ETag",
      "Last-Modified",
    ],
    MaxAgeSeconds: 3600,
  },
];

async function main() {
  if (process.argv.includes("--check")) {
    try {
      const res = await s3.send(new GetBucketCorsCommand({ Bucket: bucket }));
      console.log("Current CORS:", JSON.stringify(res.CORSRules, null, 2));
    } catch (e) {
      console.log("No CORS configured (or error):", (e as Error).name);
    }
    return;
  }

  await s3.send(
    new PutBucketCorsCommand({
      Bucket: bucket,
      CORSConfiguration: { CORSRules: CORS_RULES },
    }),
  );
  console.log(`Applied CORS to R2 bucket "${bucket}".`);
  const res = await s3.send(new GetBucketCorsCommand({ Bucket: bucket }));
  console.log("Now:", JSON.stringify(res.CORSRules, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });

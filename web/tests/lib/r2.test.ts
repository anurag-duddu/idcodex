import { describe, it, expect, vi } from "vitest";

vi.mock("@aws-sdk/s3-request-presigner", () => ({
  getSignedUrl: vi.fn(async () => "https://signed.example/object"),
}));

import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { signedUrlFor, isRemoteUrl } from "@/lib/r2";

const R2_KEYS = [
  "R2_ACCOUNT_ID",
  "R2_ACCESS_KEY_ID",
  "R2_SECRET_ACCESS_KEY",
  "R2_BUCKET",
  "R2_ENDPOINT",
] as const;

describe("isRemoteUrl", () => {
  it("detects absolute http(s) keys", () => {
    expect(isRemoteUrl("https://example.com/x.pdf")).toBe(true);
    expect(isRemoteUrl("http://example.com/x.pdf")).toBe(true);
    expect(isRemoteUrl("courses/a/b/x.pdf")).toBe(false);
  });
});

describe("signedUrlFor", () => {
  // Runs first, before any successful call constructs/caches the client.
  it("throws when R2 is not configured", async () => {
    for (const k of R2_KEYS) delete process.env[k];
    await expect(signedUrlFor("courses/a/x.pdf")).rejects.toThrow(
      /R2 not configured/,
    );
  });

  it("returns a signed url and passes bucket + key", async () => {
    process.env.R2_ACCOUNT_ID = "acc";
    process.env.R2_ACCESS_KEY_ID = "ak";
    process.env.R2_SECRET_ACCESS_KEY = "sk";
    process.env.R2_BUCKET = "bucket";
    process.env.R2_ENDPOINT = "https://acc.r2.cloudflarestorage.com";

    const url = await signedUrlFor("courses/a/b/x.pdf", { expiresIn: 300 });
    expect(url).toBe("https://signed.example/object");

    const call = vi.mocked(getSignedUrl).mock.calls.at(-1)!;
    const command = call[1] as { input: { Bucket: string; Key: string } };
    expect(command.input.Bucket).toBe("bucket");
    expect(command.input.Key).toBe("courses/a/b/x.pdf");
  });
});

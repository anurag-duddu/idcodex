import { describe, it, expect } from "vitest";
import { readEnv } from "@/lib/env";

describe("readEnv", () => {
  it("returns required vars when present", () => {
    const e = readEnv({ DATABASE_URL: "x", APP_URL: "z" });
    expect(e.DATABASE_URL).toBe("x");
    expect(e.APP_URL).toBe("z");
  });

  it("includes optional vars when present", () => {
    const e = readEnv({
      DATABASE_URL: "x",
      APP_URL: "z",
      R2_BUCKET: "bucket",
    });
    expect(e.R2_BUCKET).toBe("bucket");
  });

  it("throws listing all missing required vars", () => {
    expect(() => readEnv({})).toThrowError(/DATABASE_URL/);
    expect(() => readEnv({})).toThrowError(/APP_URL/);
  });
});

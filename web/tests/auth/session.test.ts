import { describe, it, expect, beforeAll } from "vitest";
import { createSession, verifySession } from "@/auth/session";

beforeAll(() => {
  process.env.AUTH_SECRET = "test-secret-aaaaaaaaaaaaaaaaaaaaaaaaaaaa";
});

describe("session crypto", () => {
  it("round-trips a payload", async () => {
    const token = await createSession({ sub: "u1", email: "a@b.com" });
    const payload = await verifySession(token);
    expect(payload.sub).toBe("u1");
    expect(payload.email).toBe("a@b.com");
  });

  it("rejects a tampered token", async () => {
    const token = await createSession({ sub: "u1", email: "a@b.com" });
    await expect(verifySession(token + "x")).rejects.toThrow();
  });

  it("rejects an expired token", async () => {
    const token = await createSession(
      { sub: "u1", email: "a@b.com" },
      { expiresIn: 1 }, // epoch second 1 → long past
    );
    await expect(verifySession(token)).rejects.toThrow();
  });
});

import { describe, it, expect } from "vitest";
import { emailDomain, isAutoAllowedDomain, isAllowedEmail } from "@/auth/allowlist";

describe("emailDomain", () => {
  it("extracts and lowercases the domain", () => {
    expect(emailDomain("Person@Hawk.IIT.edu")).toBe("hawk.iit.edu");
  });
  it("returns null for malformed input", () => {
    expect(emailDomain("not-an-email")).toBeNull();
  });
});

describe("isAutoAllowedDomain", () => {
  it("allows IIT/ID domains", () => {
    expect(isAutoAllowedDomain("a@hawk.iit.edu")).toBe(true);
    expect(isAutoAllowedDomain("a@iit.edu")).toBe(true);
    expect(isAutoAllowedDomain("a@id.iit.edu")).toBe(true);
  });
  it("rejects others", () => {
    expect(isAutoAllowedDomain("a@gmail.com")).toBe(false);
  });
});

describe("isAllowedEmail", () => {
  it("allows auto-domain accounts", () => {
    expect(isAllowedEmail("student@hawk.iit.edu")).toBe(true);
  });
  it("allows an explicitly allowlisted personal email (alumni)", () => {
    expect(
      isAllowedEmail("alum@gmail.com", { allowed: ["alum@gmail.com"] }),
    ).toBe(true);
  });
  it("is case-insensitive for the allowlist", () => {
    expect(isAllowedEmail("Alum@Gmail.com", { allowed: ["alum@gmail.com"] })).toBe(
      true,
    );
  });
  it("denies an unknown personal email", () => {
    expect(isAllowedEmail("random@gmail.com")).toBe(false);
  });
});

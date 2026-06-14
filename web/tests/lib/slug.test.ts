import { describe, it, expect } from "vitest";
import { slugify, uniqueSlug } from "@/lib/slug";

describe("slugify", () => {
  it("lowercases and hyphenates", () => {
    expect(slugify("Systems & Systems Theory")).toBe("systems-systems-theory");
  });
  it("drops a file extension by default", () => {
    expect(slugify("Cognition in the Wild.pdf")).toBe("cognition-in-the-wild");
  });
  it("keeps extension when keepExt", () => {
    expect(slugify("Case.pdf", { keepExt: true })).toBe("case-pdf");
  });
  it("handles unicode/punctuation and trims dashes", () => {
    expect(slugify("  Héllo—World!  ")).toBe("hello-world");
  });
  it("falls back to 'item' for empty result", () => {
    expect(slugify("***")).toBe("item");
  });
});

describe("uniqueSlug", () => {
  it("returns base when unused", () => {
    expect(uniqueSlug("readings", new Set())).toBe("readings");
  });
  it("appends a counter on collision", () => {
    const used = new Set(["readings"]);
    expect(uniqueSlug("readings", used)).toBe("readings-2");
  });
  it("keeps incrementing", () => {
    const used = new Set(["readings", "readings-2"]);
    expect(uniqueSlug("readings", used)).toBe("readings-3");
  });
});

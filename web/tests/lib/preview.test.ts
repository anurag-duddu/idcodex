import { describe, it, expect } from "vitest";
import { previewTypeFor } from "@/lib/preview";

describe("previewTypeFor", () => {
  it("maps pdf", () => {
    expect(previewTypeFor("application/pdf")).toBe("pdf");
  });
  it("maps any image/* to image", () => {
    expect(previewTypeFor("image/png")).toBe("image");
    expect(previewTypeFor("image/jpeg")).toBe("image");
    expect(previewTypeFor("image/svg+xml")).toBe("image");
  });
  it("maps any video/* to video", () => {
    expect(previewTypeFor("video/mp4")).toBe("video");
  });
  it("maps office document mimetypes to office", () => {
    expect(previewTypeFor("application/msword")).toBe("office");
    expect(
      previewTypeFor(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ),
    ).toBe("office");
    expect(
      previewTypeFor(
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      ),
    ).toBe("office");
  });
  it("maps unknown / missing to none", () => {
    expect(previewTypeFor("application/zip")).toBe("none");
    expect(previewTypeFor(undefined)).toBe("none");
    expect(previewTypeFor(null)).toBe("none");
  });
});

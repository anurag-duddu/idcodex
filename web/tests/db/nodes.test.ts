import { describe, it, expect } from "vitest";
import { resolvePath, buildBreadcrumb } from "@/db/queries/nodes";

const nodes = [
  { id: "r", parentId: null, slug: "readings", kind: "folder" as const },
  { id: "l", parentId: null, slug: "lectures", kind: "folder" as const },
  { id: "c", parentId: "r", slug: "cognition-in-the-wild", kind: "file" as const },
  { id: "w", parentId: "r", slug: "week-1", kind: "file" as const },
];

describe("resolvePath", () => {
  it("resolves a nested path to the right file node", () => {
    expect(resolvePath(nodes, ["readings", "cognition-in-the-wild"])?.id).toBe(
      "c",
    );
  });
  it("resolves a single folder segment", () => {
    expect(resolvePath(nodes, ["readings"])?.id).toBe("r");
  });
  it("returns null for an unknown first segment", () => {
    expect(resolvePath(nodes, ["nope"])).toBeNull();
  });
  it("returns null when a deeper segment is missing", () => {
    expect(resolvePath(nodes, ["readings", "missing"])).toBeNull();
  });
  it("does not match a child slug under the wrong parent", () => {
    expect(resolvePath(nodes, ["lectures", "week-1"])).toBeNull();
  });
});

describe("buildBreadcrumb", () => {
  it("returns ancestors root→target inclusive", () => {
    expect(buildBreadcrumb(nodes, "c").map((n) => n.id)).toEqual(["r", "c"]);
  });
  it("returns just the node for a root", () => {
    expect(buildBreadcrumb(nodes, "r").map((n) => n.id)).toEqual(["r"]);
  });
  it("returns empty for an unknown id", () => {
    expect(buildBreadcrumb(nodes, "zzz")).toEqual([]);
  });
});

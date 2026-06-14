import { describe, it, expect } from "vitest";
import { assembleCourseList } from "@/db/queries/courses";

describe("assembleCourseList", () => {
  const courses = [
    { id: "a", title: "Alpha" },
    { id: "b", title: "Beta" },
  ];

  it("groups professor names and file counts per course", () => {
    const res = assembleCourseList(
      courses,
      [
        { courseId: "a", name: "Dr X" },
        { courseId: "a", name: "Dr Y" },
      ],
      [{ courseId: "a", fileCount: 5 }],
    );
    expect(res[0].professors).toEqual(["Dr X", "Dr Y"]);
    expect(res[0].fileCount).toBe(5);
  });

  it("defaults to no professors and zero files", () => {
    const res = assembleCourseList(courses, [], []);
    expect(res[1].professors).toEqual([]);
    expect(res[1].fileCount).toBe(0);
  });
});

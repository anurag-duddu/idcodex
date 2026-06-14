import type { CourseTypeValue } from "@/db/schema";

/** Top-level nav order (per design): Studio · Workshop · Seminar. */
export const COURSE_TYPES: {
  value: CourseTypeValue;
  label: string;
  credits: string;
  blurb: string;
}[] = [
  { value: "studio", label: "Studio", credits: "4.0 cr", blurb: "14-week immersive design projects." },
  { value: "workshop", label: "Workshop", credits: "3.0 cr", blurb: "14-week skill- and method-building." },
  { value: "seminar", label: "Seminar", credits: "1.5 cr", blurb: "7-week focused topics." },
];

export function isCourseType(s: string): s is CourseTypeValue {
  return s === "studio" || s === "workshop" || s === "seminar";
}

export function courseTypeLabel(t: CourseTypeValue): string {
  return COURSE_TYPES.find((x) => x.value === t)?.label ?? t;
}

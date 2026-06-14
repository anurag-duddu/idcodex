import type { PreviewTypeValue } from "@/db/schema";

const OFFICE_MIMES = new Set([
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.ms-powerpoint",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.oasis.opendocument.text",
  "application/vnd.oasis.opendocument.presentation",
]);

/** Map a MIME type to how it should be previewed. */
export function previewTypeFor(
  mimeType: string | null | undefined,
): PreviewTypeValue {
  if (!mimeType) return "none";
  const mime = mimeType.toLowerCase();
  if (mime === "application/pdf") return "pdf";
  if (mime.startsWith("image/")) return "image";
  if (mime.startsWith("video/")) return "video";
  if (OFFICE_MIMES.has(mime)) return "office";
  return "none";
}

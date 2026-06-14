// Grounded corrections for the ID archive: which files to exclude (student work /
// non-ID) and metadata overrides for the rest. The data names students, so it is
// NOT committed: it lives in the gitignored data/ folder next to export.json and
// file_upload_map.json, which the migration needs anyway.
//
// File shape (data/migrate/corrections.json):
//   { "excludedPaths": string[], "metadataOverrides": Record<path, MetaOverride> }
// Keys are paths RELATIVE to the archive root (portable; not tied to a mountpoint).
// Override the location with CORRECTIONS_PATH.

import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

/** Archive root on disk; override with LACIE_ROOT env. Default: the LaCie mount. */
export const ARCHIVE_ROOT = process.env.LACIE_ROOT ?? "/Volumes/LaCie";

/** Convert an absolute source path to an archive-relative key. */
export function toArchiveRelative(p: string): string {
  return p.startsWith(ARCHIVE_ROOT + "/") ? p.slice(ARCHIVE_ROOT.length + 1) : p;
}

export type MetaOverride = { title: string; author: string | null; year: number | null };

type CorrectionsFile = {
  excludedPaths: string[];
  metadataOverrides: Record<string, MetaOverride>;
};

const CORRECTIONS_PATH =
  process.env.CORRECTIONS_PATH ?? resolve(process.cwd(), "..", "data/migrate/corrections.json");

function load(): CorrectionsFile {
  // Fail loudly: migrating without exclusions would publish student work.
  if (!existsSync(CORRECTIONS_PATH)) {
    throw new Error(
      `Corrections file not found at ${CORRECTIONS_PATH}. It is gitignored (it names students); ` +
        `restore it from the local data/ backup or set CORRECTIONS_PATH.`,
    );
  }
  const data = JSON.parse(readFileSync(CORRECTIONS_PATH, "utf8")) as Partial<CorrectionsFile>;
  if (!Array.isArray(data.excludedPaths) || typeof data.metadataOverrides !== "object" || !data.metadataOverrides) {
    throw new Error(`Corrections file at ${CORRECTIONS_PATH} is missing excludedPaths or metadataOverrides.`);
  }
  return data as CorrectionsFile;
}

const corrections = load();

export const EXCLUDED_PATHS: ReadonlySet<string> = new Set(corrections.excludedPaths);
export const METADATA_OVERRIDES: Record<string, MetaOverride> = corrections.metadataOverrides;

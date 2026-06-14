const FILE_EXT = /\.[a-z0-9]{1,6}$/i;

/** URL-safe slug. Drops a trailing file extension unless `keepExt`. */
export function slugify(input: string, opts: { keepExt?: boolean } = {}): string {
  let s = input.trim();
  if (!opts.keepExt) s = s.replace(FILE_EXT, "");
  s = s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "") // strip diacritics
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return s || "item";
}

/** Returns `base`, or `base-2`, `base-3`, … if already in `used`. Mutates `used`. */
export function uniqueSlug(base: string, used: Set<string>): string {
  if (!used.has(base)) {
    used.add(base);
    return base;
  }
  let n = 2;
  while (used.has(`${base}-${n}`)) n++;
  const result = `${base}-${n}`;
  used.add(result);
  return result;
}

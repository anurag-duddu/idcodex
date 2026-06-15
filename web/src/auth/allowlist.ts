import { eq } from "drizzle-orm";
import { db } from "@/db/client";
import { users } from "@/db/schema";

/**
 * Domains whose accounts are admitted automatically. ID Codex is ID-only, so
 * this is deliberately narrow — not every Illinois Tech address.
 */
export const AUTO_DOMAINS = [
  "id.iit.edu", // ID students/alumni on the legacy domain
  "hawk.illinoistech.edu", // current students (post-rebrand)
  "illinoistech.edu", // faculty/staff
];

/** Lowercased domain part of an email, or null if malformed. */
export function emailDomain(email: string): string | null {
  const m = email.trim().toLowerCase().match(/^[^@\s]+@([^@\s]+)$/);
  return m ? m[1] : null;
}

export function isAutoAllowedDomain(email: string): boolean {
  const d = emailDomain(email);
  return d ? AUTO_DOMAINS.includes(d) : false;
}

/** Pure check: auto-domain, or present in the provided allowlist. */
export function isAllowedEmail(
  email: string,
  opts: { allowed?: string[] } = {},
): boolean {
  if (isAutoAllowedDomain(email)) return true;
  const norm = email.trim().toLowerCase();
  return (opts.allowed ?? []).some((e) => e.trim().toLowerCase() === norm);
}

/** DB-backed check: auto-domain OR an active row in `users`. */
export async function isAllowed(email: string): Promise<boolean> {
  if (isAutoAllowedDomain(email)) return true;
  const norm = email.trim().toLowerCase();
  const rows = await db
    .select({ status: users.status })
    .from(users)
    .where(eq(users.email, norm))
    .limit(1);
  return rows[0]?.status === "active";
}

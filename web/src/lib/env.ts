/**
 * Typed access to environment variables.
 *
 * Server-only by convention — never import this from a Client Component.
 * The single `.env` lives at the repo root; `web/.env` is a symlink to it.
 * Next.js loads it at runtime; standalone scripts (drizzle-kit, seed, migrate)
 * must `import "dotenv/config"` before importing this module.
 */

// Auth is Clerk (its own NEXT_PUBLIC_CLERK_* / CLERK_SECRET_KEY vars are read by
// @clerk/nextjs directly, not here). The former magic-link vars (AUTH_SECRET,
// RESEND_API_KEY, AUTH_EMAIL_FROM) were dropped with that migration.
const REQUIRED = ["DATABASE_URL", "APP_URL"] as const;
const OPTIONAL = [
  "DATABASE_URL_UNPOOLED",
  "R2_ACCOUNT_ID",
  "R2_ACCESS_KEY_ID",
  "R2_SECRET_ACCESS_KEY",
  "R2_BUCKET",
  "R2_ENDPOINT",
  "NOTION_API_KEY",
] as const;

type RequiredKey = (typeof REQUIRED)[number];
type OptionalKey = (typeof OPTIONAL)[number];

export type AppEnv = { [K in RequiredKey]: string } & {
  [K in OptionalKey]?: string;
};

export function readEnv(
  src: Record<string, string | undefined> = process.env,
): AppEnv {
  const missing = REQUIRED.filter((k) => !src[k]);
  if (missing.length > 0) {
    throw new Error(
      `Missing required env vars: ${missing.join(", ")}. ` +
        `Check the repo-root .env (web/.env is a symlink to it).`,
    );
  }
  const out: Record<string, string> = {};
  for (const k of [...REQUIRED, ...OPTIONAL]) {
    const v = src[k];
    if (v != null && v !== "") out[k] = v;
  }
  return out as AppEnv;
}

let cached: AppEnv | null = null;

/** Memoized, validated environment for app/server code. */
export function getEnv(): AppEnv {
  return (cached ??= readEnv());
}

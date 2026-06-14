import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import { getEnv } from "@/lib/env";
import * as schema from "./schema";

type DB = ReturnType<typeof drizzle<typeof schema>>;

let _db: DB | null = null;

/** Lazily constructed Drizzle client (env is only read on first query). */
export function getDb(): DB {
  return (_db ??= drizzle(neon(getEnv().DATABASE_URL), { schema }));
}

/**
 * Convenience proxy so call sites can `import { db }` and use `db.select()`.
 * The underlying client (and env read) is created on first property access,
 * which keeps module imports side-effect-free for unit tests.
 */
export const db = new Proxy({} as DB, {
  get(_target, prop) {
    const inst = getDb();
    const value = inst[prop as keyof DB];
    return typeof value === "function" ? value.bind(inst) : value;
  },
});

export { schema };

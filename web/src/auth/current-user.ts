import { currentUser } from "@clerk/nextjs/server";

/**
 * Primary email of the signed-in Clerk user, or null. The single place the app
 * reads identity from Clerk — server components and route handlers call this,
 * then check it against `isAllowed` (see `./allowlist`).
 */
export async function getCurrentUserEmail(): Promise<string | null> {
  const u = await currentUser();
  return (
    u?.primaryEmailAddress?.emailAddress ??
    u?.emailAddresses?.[0]?.emailAddress ??
    null
  );
}

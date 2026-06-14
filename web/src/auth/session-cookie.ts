import { cookies } from "next/headers";
import {
  SESSION_COOKIE,
  createSession,
  verifySession,
  type SessionPayload,
} from "./session";

const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

function cookieOptions() {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: MAX_AGE,
  };
}

/** Set the session cookie (server actions). */
export async function startSession(payload: SessionPayload): Promise<void> {
  const token = await createSession(payload);
  const jar = await cookies();
  jar.set(SESSION_COOKIE, token, cookieOptions());
}

/** Clear the session cookie (server actions). */
export async function clearSession(): Promise<void> {
  const jar = await cookies();
  jar.delete(SESSION_COOKIE);
}

/** Current signed-in user from the cookie, or null. */
export async function getCurrentUser(): Promise<SessionPayload | null> {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  if (!token) return null;
  try {
    return await verifySession(token);
  } catch {
    return null;
  }
}

export { cookieOptions };

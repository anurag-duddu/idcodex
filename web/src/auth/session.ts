import { SignJWT, jwtVerify } from "jose";

/**
 * Pure session-token crypto (no Next APIs) so it's unit-testable and
 * edge-safe. Reads AUTH_SECRET directly from the environment.
 */

export const SESSION_COOKIE = "idcodex_session";

export type SessionPayload = { sub: string; email: string };

function secretKey(): Uint8Array {
  const s = process.env.AUTH_SECRET;
  if (!s) throw new Error("AUTH_SECRET is not set");
  return new TextEncoder().encode(s);
}

export async function createSession(
  payload: SessionPayload,
  opts: { expiresIn?: string | number } = {},
): Promise<string> {
  return new SignJWT({ email: payload.email })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(payload.sub)
    .setIssuedAt()
    .setExpirationTime(opts.expiresIn ?? "30d")
    .sign(secretKey());
}

export async function verifySession(token: string): Promise<SessionPayload> {
  const { payload } = await jwtVerify(token, secretKey());
  return { sub: String(payload.sub), email: String(payload.email) };
}

/** Short-lived token used in magic-link emails (purpose=login). */
export async function createLoginToken(
  email: string,
  opts: { expiresIn?: string | number } = {},
): Promise<string> {
  return new SignJWT({ email, purpose: "login" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(opts.expiresIn ?? "20m")
    .sign(secretKey());
}

export async function verifyLoginToken(token: string): Promise<{ email: string }> {
  const { payload } = await jwtVerify(token, secretKey());
  if (payload.purpose !== "login") throw new Error("wrong token purpose");
  return { email: String(payload.email) };
}

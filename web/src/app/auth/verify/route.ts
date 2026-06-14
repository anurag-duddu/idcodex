import { NextResponse, type NextRequest } from "next/server";
import { eq } from "drizzle-orm";
import { verifyLoginToken, createSession, SESSION_COOKIE } from "@/auth/session";
import { cookieOptions } from "@/auth/session-cookie";
import { isAllowed } from "@/auth/allowlist";
import { db } from "@/db/client";
import { users } from "@/db/schema";

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token");
  if (!token) {
    return NextResponse.redirect(new URL("/signin?error=1", req.url));
  }

  let email: string;
  try {
    ({ email } = await verifyLoginToken(token));
  } catch {
    return NextResponse.redirect(new URL("/signin?error=1", req.url));
  }

  // Re-check allowlist at consume time.
  if (!(await isAllowed(email))) {
    return NextResponse.redirect(new URL("/signin?denied=1", req.url));
  }

  // Upsert the user.
  const existing = await db
    .select()
    .from(users)
    .where(eq(users.email, email))
    .limit(1);
  let user = existing[0];
  if (!user) {
    [user] = await db
      .insert(users)
      .values({ email, status: "active" })
      .returning();
  }

  const sessionToken = await createSession({ sub: user.id, email });
  const res = NextResponse.redirect(new URL("/", req.url));
  res.cookies.set(SESSION_COOKIE, sessionToken, cookieOptions());
  return res;
}

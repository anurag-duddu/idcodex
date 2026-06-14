import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, verifySession } from "@/auth/session";

// Paths that never require a session.
const PUBLIC_PREFIXES = ["/signin", "/auth"];

/**
 * Optimistic gate (Next 16 "proxy", formerly middleware): if there's no valid
 * session cookie, redirect to /signin. The allowlist + DB checks happen in the
 * data layer (file route, server components) — not here.
 */
export async function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (
    PUBLIC_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + "/"))
  ) {
    return NextResponse.next();
  }

  const token = req.cookies.get(SESSION_COOKIE)?.value;
  if (token) {
    try {
      await verifySession(token);
      return NextResponse.next();
    } catch {
      // fall through to redirect
    }
  }

  const url = new URL("/signin", req.url);
  url.searchParams.set("next", pathname);
  return NextResponse.redirect(url);
}

export const config = {
  // Run on all pages except API routes (they self-gate), Next internals,
  // and brand assets.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|icon.svg).*)"],
};

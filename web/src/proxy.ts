import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

/**
 * Next 16 "proxy" (formerly middleware), composed with Clerk.
 *
 * - Clerk's sign-in/up pages are the only routes reachable while signed out.
 * - API routes self-gate: they return JSON 401/403 from `auth()` in the route
 *   handler, so we let Clerk populate the auth context but never force a
 *   redirect on them.
 * - Every other route requires a signed-in Clerk session. The ID-only
 *   allowlist (auto-domains + DB-backed individual emails) is enforced one
 *   layer up, in the (app) layout and the file route — not here.
 */
const isPublicRoute = createRouteMatcher(["/sign-in(.*)", "/sign-up(.*)"]);
const isApiRoute = createRouteMatcher(["/api(.*)"]);

export default clerkMiddleware(
  async (auth, req) => {
    if (isApiRoute(req)) return;
    if (!isPublicRoute(req)) await auth.protect();
  },
  // Pin the expected request origin so Clerk rejects tokens minted for other
  // (sub)domains — guards against subdomain cookie-leaking / CSRF attacks.
  { authorizedParties: ["https://idcodex.org"] },
);

export const config = {
  matcher: [
    // All pages except Next internals and brand assets.
    "/((?!_next/static|_next/image|favicon.ico|icon.svg).*)",
    // Always run on API routes so `auth()` works in route handlers.
    "/(api|trpc)(.*)",
  ],
};

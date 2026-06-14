import { createLoginToken } from "./session";
import { isAllowed } from "./allowlist";

export type RequestLinkResult = { ok: true; devLink?: string };

/**
 * Issue a magic-link for an allowed email. To avoid account enumeration the
 * result is always `{ ok: true }`; the link is only created/sent for allowed
 * addresses. Dev transport logs the link to the server console (and returns it
 * as `devLink` outside production so e2e can drive the flow).
 */
export async function requestLink(
  email: string,
  origin: string,
): Promise<RequestLinkResult> {
  const norm = email.trim().toLowerCase();
  if (!(await isAllowed(norm))) return { ok: true };

  const token = await createLoginToken(norm);
  const link = `${origin}/auth/verify?token=${encodeURIComponent(token)}`;

  if (process.env.RESEND_API_KEY) {
    await sendViaResend(norm, link);
  } else {
    // Dev transport: print the link to the server log.
    console.log(`\n[magic-link] ${norm}\n  ${link}\n`);
  }

  return {
    ok: true,
    devLink: process.env.NODE_ENV !== "production" ? link : undefined,
  };
}

async function sendViaResend(to: string, link: string): Promise<void> {
  const from = process.env.AUTH_EMAIL_FROM ?? "ID Codex <login@idcodex.org>";
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      to,
      subject: "Your ID Codex sign-in link",
      html: `<p>Click to sign in to ID Codex:</p><p><a href="${link}">Sign in</a></p><p>This link expires in 20 minutes.</p>`,
    }),
  });
  if (!res.ok) {
    console.error("[magic-link] Resend failed:", res.status, await res.text());
  }
}

"use server";

import { headers } from "next/headers";
import { requestLink } from "@/auth/magic-link";

export type SigninState = { sent: boolean; error?: string; devLink?: string };

export async function requestMagicLink(
  _prev: SigninState,
  formData: FormData,
): Promise<SigninState> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email || !email.includes("@")) {
    return { sent: false, error: "Enter a valid email address." };
  }
  const h = await headers();
  const proto = h.get("x-forwarded-proto") ?? "http";
  const host = h.get("host") ?? "localhost:3000";
  const res = await requestLink(email, `${proto}://${host}`);
  return { sent: true, devLink: res.devLink };
}

"use client";

import { useActionState } from "react";
import { requestMagicLink, type SigninState } from "@/app/signin/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const initial: SigninState = { sent: false };

export function SigninForm() {
  const [state, action, pending] = useActionState(requestMagicLink, initial);

  if (state.sent) {
    return (
      <div className="space-y-3" role="status">
        <p className="text-sm text-slate">
          If that address has access, a sign-in link is on its way. Check your
          email.
        </p>
        {state.devLink && (
          <a
            className="block break-all text-sm text-id-blue underline"
            href={state.devLink}
          >
            Dev link — click to sign in
          </a>
        )}
      </div>
    );
  }

  return (
    <form action={action} className="space-y-3">
      <Input
        type="email"
        name="email"
        placeholder="you@hawk.illinoistech.edu"
        required
        autoFocus
        aria-label="Email address"
      />
      {state.error && (
        <p className="text-sm text-destructive">{state.error}</p>
      )}
      <Button type="submit" disabled={pending} className="w-full">
        {pending ? "Sending…" : "Email me a sign-in link"}
      </Button>
    </form>
  );
}

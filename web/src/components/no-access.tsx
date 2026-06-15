import { SignOutButton } from "@clerk/nextjs";
import { Wordmark } from "@/components/brand/wordmark";
import { Button } from "@/components/ui/button";

/**
 * Shown to a signed-in user whose email isn't on the ID Codex access list.
 * Replaces the old `/signin?denied=1` flow.
 */
export function NoAccess({ email }: { email: string | null }) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center px-6">
      <Wordmark size="lg" />
      <h1 className="mt-8 text-xl font-semibold text-ink">Access pending</h1>
      <p className="mt-2 text-sm leading-relaxed text-slate">
        {email ? (
          <>
            <span className="font-medium text-ink">{email}</span> isn’t on the
            ID Codex access list yet.
          </>
        ) : (
          "Your account isn’t on the ID Codex access list yet."
        )}{" "}
        Access is open to IIT Institute of Design students, alumni, and faculty.
        If that’s you, ask an admin to add your address.
      </p>
      <div className="mt-6">
        <SignOutButton redirectUrl="/sign-in">
          <Button className="w-full">Sign out</Button>
        </SignOutButton>
      </div>
    </main>
  );
}

import type { Metadata } from "next";
import { Wordmark } from "@/components/brand/wordmark";
import { SigninForm } from "@/components/signin-form";

export const metadata: Metadata = { title: "Sign in" };

export default async function SigninPage({
  searchParams,
}: {
  searchParams: Promise<{ denied?: string; error?: string }>;
}) {
  const sp = await searchParams;
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center px-6">
      <Wordmark size="lg" />
      <h1 className="mt-8 text-xl font-semibold text-ink">Sign in</h1>
      <p className="mt-1 text-sm text-slate">
        For IIT Institute of Design students and alumni.
      </p>

      {sp.denied && (
        <p className="mt-4 text-sm text-destructive">
          That email isn’t on the access list yet. Ask an admin to add you.
        </p>
      )}
      {sp.error && (
        <p className="mt-4 text-sm text-destructive">
          That sign-in link was invalid or expired. Please try again.
        </p>
      )}

      <div className="mt-6">
        <SigninForm />
      </div>
    </main>
  );
}

import Link from "next/link";
import { Wordmark } from "@/components/brand/wordmark";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col items-start justify-center px-6">
      <Wordmark />
      <p className="mt-8 font-mono text-xs uppercase tracking-widest text-id-gray">
        404
      </p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">
        Page not found
      </h1>
      <p className="mt-2 text-sm text-slate">
        This page doesn’t exist or has moved.
      </p>
      <Link
        href="/"
        className="mt-6 text-sm text-id-blue transition hover:underline"
      >
        ← Back to home
      </Link>
    </main>
  );
}

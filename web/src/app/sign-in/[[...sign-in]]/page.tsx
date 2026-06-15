import { SignIn } from "@clerk/nextjs";
import { Wordmark } from "@/components/brand/wordmark";

export default function SignInPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-sm flex-col items-center justify-center gap-8 px-6">
      <Wordmark size="lg" />
      <SignIn />
    </main>
  );
}

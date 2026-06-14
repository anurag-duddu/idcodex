import { TopNav } from "@/components/top-nav";

export function AppShell({
  email,
  children,
}: {
  email: string | null;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav email={email} />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
        {children}
      </main>
      <footer className="border-t border-id-border/60 py-6">
        <div className="mx-auto max-w-6xl px-4 text-xs text-id-gray sm:px-6">
          ID Codex · IIT Institute of Design · view-only archive
        </div>
      </footer>
    </div>
  );
}

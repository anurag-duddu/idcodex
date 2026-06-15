import { getCurrentUserEmail } from "@/auth/current-user";
import { isAllowed } from "@/auth/allowlist";
import { AppShell } from "@/components/app-shell";
import { NoAccess } from "@/components/no-access";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // The proxy guarantees a signed-in Clerk user here; this gate enforces the
  // ID-only allowlist (auto-domains OR a DB-backed individual allow).
  const email = await getCurrentUserEmail();
  if (!email || !(await isAllowed(email))) {
    return <NoAccess email={email} />;
  }
  return <AppShell email={email}>{children}</AppShell>;
}

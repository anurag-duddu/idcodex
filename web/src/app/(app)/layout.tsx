import { getCurrentUser } from "@/auth/session-cookie";
import { AppShell } from "@/components/app-shell";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();
  return <AppShell email={user?.email ?? null}>{children}</AppShell>;
}

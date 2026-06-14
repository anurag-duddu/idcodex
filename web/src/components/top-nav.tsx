"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Wordmark } from "@/components/brand/wordmark";
import { SearchBar } from "@/components/search-bar";
import { AccountMenu } from "@/components/account-menu";
import { COURSE_TYPES } from "@/lib/course-types";
import { cn } from "@/lib/utils";

export function TopNav({ email }: { email: string | null }) {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-id-border bg-white/85 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4 sm:gap-6 sm:px-6">
        <Link href="/" className="shrink-0" aria-label="ID Codex home">
          <Wordmark />
        </Link>

        <nav className="hidden items-center sm:flex" aria-label="Course types">
          {COURSE_TYPES.map((t) => {
            const href = `/${t.value}`;
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={t.value}
                href={href}
                className={cn(
                  "relative px-3 py-1.5 text-sm font-medium text-slate transition-colors hover:text-ink",
                  active && "text-ink",
                )}
              >
                {t.label}
                {active && (
                  <span className="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-id-blue" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <SearchBar />
          <AccountMenu email={email} />
        </div>
      </div>

      {/* mobile type tabs */}
      <nav
        className="flex items-center gap-1 border-t border-id-border/60 px-4 py-1.5 sm:hidden"
        aria-label="Course types"
      >
        {COURSE_TYPES.map((t) => {
          const href = `/${t.value}`;
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={t.value}
              href={href}
              className={cn(
                "rounded px-2.5 py-1 text-sm font-medium text-slate",
                active && "bg-mist text-ink",
              )}
            >
              {t.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}

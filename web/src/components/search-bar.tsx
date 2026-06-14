"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MagnifyingGlass } from "@phosphor-icons/react/dist/ssr";

export function SearchBar() {
  const router = useRouter();
  const [q, setQ] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const term = q.trim();
        if (term) router.push(`/search?q=${encodeURIComponent(term)}`);
      }}
      className="hidden items-center gap-2 rounded-md border border-id-border px-2.5 py-1.5 transition focus-within:border-id-blue focus-within:ring-2 focus-within:ring-id-blue/30 md:flex"
    >
      <MagnifyingGlass size={16} weight="bold" className="text-id-gray" />
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search courses, files…"
        aria-label="Search"
        className="w-40 bg-transparent text-sm text-ink outline-none placeholder:text-id-gray lg:w-56"
      />
    </form>
  );
}

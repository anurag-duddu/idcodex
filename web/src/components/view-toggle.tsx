"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { GridFour, Rows } from "@phosphor-icons/react/dist/ssr";
import { cn } from "@/lib/utils";

export function ViewToggle() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const view = sp.get("view") === "list" ? "list" : "grid";

  const set = (v: "grid" | "list") => {
    const p = new URLSearchParams(sp.toString());
    p.set("view", v);
    router.replace(`${pathname}?${p.toString()}`, { scroll: false });
  };

  return (
    <div className="flex items-center gap-0.5 rounded-md border border-id-border p-0.5">
      <button
        onClick={() => set("grid")}
        aria-label="Grid view"
        aria-pressed={view === "grid"}
        className={cn(
          "rounded p-1 transition",
          view === "grid" ? "bg-mist text-ink" : "text-id-gray hover:text-ink",
        )}
      >
        <GridFour size={16} weight="bold" />
      </button>
      <button
        onClick={() => set("list")}
        aria-label="List view"
        aria-pressed={view === "list"}
        className={cn(
          "rounded p-1 transition",
          view === "list" ? "bg-mist text-ink" : "text-id-gray hover:text-ink",
        )}
      >
        <Rows size={16} weight="bold" />
      </button>
    </div>
  );
}

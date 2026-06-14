import Link from "next/link";
import { CaretRight } from "@phosphor-icons/react/dist/ssr";

export type Crumb = { href?: string; label: string };

export function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1.5 font-mono text-xs text-id-gray">
        {items.map((c, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {i > 0 && <CaretRight size={11} className="text-id-border" />}
            {c.href ? (
              <Link href={c.href} className="hover:text-ink">
                {c.label}
              </Link>
            ) : (
              <span className="text-slate">{c.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

import Link from "next/link";
import type { PreviewTypeValue } from "@/db/schema";
import { FileGlyph, FolderGlyph } from "@/components/file-icon";
import { ViewToggle } from "@/components/view-toggle";

export type NodeItem = {
  id: string;
  kind: "folder" | "file";
  name: string;
  slug: string;
  previewType: PreviewTypeValue | null;
  resourceType: string | null;
};

function typeLabel(n: NodeItem): string {
  if (n.kind === "folder") return "Folder";
  return n.resourceType ?? "File";
}

function NodeGrid({ nodes, basePath }: { nodes: NodeItem[]; basePath: string }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {nodes.map((n) => (
        <Link
          key={n.id}
          href={`${basePath}/${n.slug}`}
          data-testid="node-link"
          className="group rounded-lg border border-id-border bg-white p-3 transition hover:border-ink/30 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-id-blue"
        >
          {n.kind === "folder" ? (
            <FolderGlyph size={26} />
          ) : (
            <FileGlyph preview={n.previewType} size={26} />
          )}
          <div className="mt-2 truncate text-sm text-ink" title={n.name}>
            {n.name}
          </div>
          <div className="font-mono text-[11px] text-id-gray">
            {typeLabel(n)}
          </div>
        </Link>
      ))}
    </div>
  );
}

function NodeList({ nodes, basePath }: { nodes: NodeItem[]; basePath: string }) {
  return (
    <ul className="divide-y divide-id-border/70 rounded-lg border border-id-border">
      {nodes.map((n) => (
        <li key={n.id}>
          <Link
            href={`${basePath}/${n.slug}`}
            data-testid="node-link"
            className="flex items-center gap-3 px-4 py-2.5 transition hover:bg-mist/40"
          >
            {n.kind === "folder" ? (
              <FolderGlyph size={18} />
            ) : (
              <FileGlyph preview={n.previewType} size={18} />
            )}
            <span className="min-w-0 flex-1 truncate text-sm text-ink">
              {n.name}
            </span>
            <span className="hidden font-mono text-[11px] text-id-gray sm:block">
              {typeLabel(n)}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function NodeBrowser({
  nodes,
  basePath,
  view,
}: {
  nodes: NodeItem[];
  basePath: string;
  view?: string;
}) {
  const mode = view === "list" ? "list" : "grid";

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-mono text-xs uppercase tracking-widest text-id-gray">
          Files &amp; folders · {nodes.length}
        </h2>
        <ViewToggle />
      </div>
      {nodes.length === 0 ? (
        <p className="rounded-lg border border-dashed border-id-border p-8 text-center text-sm text-id-gray">
          No materials here yet.{" "}
          <span className="text-id-blue">Contribute →</span>
        </p>
      ) : mode === "grid" ? (
        <NodeGrid nodes={nodes} basePath={basePath} />
      ) : (
        <NodeList nodes={nodes} basePath={basePath} />
      )}
    </section>
  );
}

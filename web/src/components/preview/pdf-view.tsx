"use client";

import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import {
  CaretLeft,
  CaretRight,
  MagnifyingGlassPlus,
  MagnifyingGlassMinus,
} from "@phosphor-icons/react/dist/ssr";

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export function PdfView({ src }: { src: string }) {
  const [numPages, setNumPages] = useState(0);
  const [page, setPage] = useState(1);
  const [scale, setScale] = useState(1);

  return (
    <div
      className="overflow-hidden rounded-lg border border-id-border"
      onContextMenu={(e) => e.preventDefault()}
    >
      <div className="flex items-center gap-2 border-b border-id-border bg-white px-3 py-2 text-sm">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
          aria-label="Previous page"
          className="rounded p-1 text-id-gray hover:text-ink disabled:opacity-40"
        >
          <CaretLeft size={16} weight="bold" />
        </button>
        <span className="font-mono text-xs text-slate">
          {page} / {numPages || "–"}
        </span>
        <button
          onClick={() => setPage((p) => Math.min(numPages || p, p + 1))}
          disabled={!!numPages && page >= numPages}
          aria-label="Next page"
          className="rounded p-1 text-id-gray hover:text-ink disabled:opacity-40"
        >
          <CaretRight size={16} weight="bold" />
        </button>
        <div className="ml-auto flex items-center gap-1">
          <button
            onClick={() => setScale((s) => Math.max(0.5, s - 0.2))}
            aria-label="Zoom out"
            className="rounded p-1 text-id-gray hover:text-ink"
          >
            <MagnifyingGlassMinus size={16} />
          </button>
          <button
            onClick={() => setScale((s) => Math.min(2.5, s + 0.2))}
            aria-label="Zoom in"
            className="rounded p-1 text-id-gray hover:text-ink"
          >
            <MagnifyingGlassPlus size={16} />
          </button>
        </div>
      </div>

      <div className="flex max-h-[78vh] justify-center overflow-auto bg-mist/40 p-4">
        <Document
          file={src}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          loading={<p className="p-8 text-sm text-id-gray">Loading preview…</p>}
          error={
            <p className="p-8 text-sm text-id-gray">
              Couldn’t load this document.
            </p>
          }
        >
          <Page
            pageNumber={page}
            scale={scale}
            renderTextLayer={false}
            renderAnnotationLayer={false}
            className="shadow-sm"
          />
        </Document>
      </div>
    </div>
  );
}

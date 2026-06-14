"use client";

import dynamic from "next/dynamic";

// react-pdf/pdfjs touch browser-only APIs (DOMMatrix) at module load, so it
// must never be server-rendered. Load it client-only.
const PdfView = dynamic(() => import("./pdf-view").then((m) => m.PdfView), {
  ssr: false,
  loading: () => (
    <div className="rounded-lg border border-id-border p-8 text-sm text-id-gray">
      Loading preview…
    </div>
  ),
});

export function PdfViewClient({ src }: { src: string }) {
  return <PdfView src={src} />;
}

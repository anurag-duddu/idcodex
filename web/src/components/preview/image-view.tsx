"use client";

export function ImageView({ src, alt }: { src: string; alt: string }) {
  return (
    <div
      className="flex max-h-[78vh] items-center justify-center overflow-auto rounded-lg border border-id-border bg-mist/40 p-4"
      onContextMenu={(e) => e.preventDefault()}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={alt}
        draggable={false}
        className="max-h-full max-w-full object-contain"
      />
    </div>
  );
}

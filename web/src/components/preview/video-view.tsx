"use client";

export function VideoView({ src }: { src: string }) {
  return (
    <div className="overflow-hidden rounded-lg border border-id-border bg-black">
      <video
        src={src}
        controls
        controlsList="nodownload noremoteplayback noplaybackrate"
        disablePictureInPicture
        onContextMenu={(e) => e.preventDefault()}
        className="max-h-[78vh] w-full"
      />
    </div>
  );
}

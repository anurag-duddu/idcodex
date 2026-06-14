import type { Node } from "@/db/schema";
import { PdfViewClient } from "@/components/preview/pdf-view-client";
import { ImageView } from "@/components/preview/image-view";
import { VideoView } from "@/components/preview/video-view";
import { UnsupportedView } from "@/components/preview/unsupported-view";
import { MetadataPanel } from "@/components/metadata-panel";

export function FilePreview({
  node,
  courseTitle,
}: {
  node: Node;
  courseTitle?: string;
}) {
  const src = `/api/file/${node.id}`;

  let viewer: React.ReactNode;
  switch (node.previewType) {
    case "pdf":
      viewer = <PdfViewClient src={src} />;
      break;
    case "image":
      viewer = <ImageView src={src} alt={node.name} />;
      break;
    case "video":
      viewer = <VideoView src={src} />;
      break;
    default:
      viewer = <UnsupportedView />;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
      <div className="min-w-0">{viewer}</div>
      <MetadataPanel node={node} courseTitle={courseTitle} />
    </div>
  );
}

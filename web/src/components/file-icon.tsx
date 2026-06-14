import {
  FilePdf,
  Image as ImageIcon,
  VideoCamera,
  FileText,
  File as FileIcon,
  Folder,
} from "@phosphor-icons/react/dist/ssr";
import type { PreviewTypeValue } from "@/db/schema";

export function FileGlyph({
  preview,
  size = 20,
}: {
  preview: PreviewTypeValue | null;
  size?: number;
}) {
  switch (preview) {
    case "pdf":
      return <FilePdf size={size} weight="regular" className="text-id-blue" />;
    case "image":
      return <ImageIcon size={size} className="text-id-gray" />;
    case "video":
      return <VideoCamera size={size} className="text-id-gray" />;
    case "office":
      return <FileText size={size} className="text-id-gray" />;
    default:
      return <FileIcon size={size} className="text-id-gray" />;
  }
}

export function FolderGlyph({ size = 20 }: { size?: number }) {
  return <Folder size={size} weight="fill" className="text-slate" />;
}

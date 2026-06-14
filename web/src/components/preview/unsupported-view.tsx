import { FileX } from "@phosphor-icons/react/dist/ssr";

export function UnsupportedView() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-id-border bg-mist/30 p-16 text-center">
      <FileX size={40} className="text-id-gray" />
      <p className="text-sm text-slate">
        Preview isn’t available for this file type.
      </p>
      <p className="text-xs text-id-gray">
        The metadata is shown alongside.
      </p>
    </div>
  );
}

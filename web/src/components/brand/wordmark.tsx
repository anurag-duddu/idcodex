import { cn } from "@/lib/utils";

type Size = "sm" | "md" | "lg";

const textSize: Record<Size, string> = {
  sm: "text-base",
  md: "text-lg",
  lg: "text-2xl",
};

const markSize: Record<Size, string> = {
  sm: "size-2",
  md: "size-2.5",
  lg: "size-3",
};

/**
 * "ID Codex" wordmark in the spirit of the Institute of Design mark
 * (ink + a single ID-blue accent). Not the proprietary ID logo.
 */
export function Wordmark({
  className,
  size = "md",
  withMark = true,
}: {
  className?: string;
  size?: Size;
  withMark?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 font-sans tracking-tight",
        textSize[size],
        className,
      )}
    >
      {withMark && (
        <span
          className={cn("rounded-[2px] bg-id-blue", markSize[size])}
          aria-hidden
        />
      )}
      <span className="font-semibold text-ink">
        ID <span className="font-normal text-slate">Codex</span>
      </span>
    </span>
  );
}

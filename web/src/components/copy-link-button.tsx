"use client";

import { useState } from "react";
import { LinkSimple, Check } from "@phosphor-icons/react/dist/ssr";

export function CopyLinkButton() {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        } catch {
          /* ignore */
        }
      }}
      className="inline-flex items-center gap-1.5 text-xs text-id-gray transition hover:text-id-blue"
    >
      {copied ? <Check size={14} /> : <LinkSimple size={14} />}
      {copied ? "Copied" : "Copy link"}
    </button>
  );
}

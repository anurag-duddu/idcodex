/**
 * ID brand palette — a TS mirror of the CSS custom properties in globals.css.
 * Source: Institute of Design theme (id.iit.edu). Use Tailwind utilities
 * (`text-ink`, `bg-id-blue`, `border-id-border`, …) in components; use these
 * constants only where a JS color value is needed (e.g. canvas, inline SVG).
 */
export const idColors = {
  ink: "#23282f",
  blue: "#00b2ff",
  white: "#ffffff",
  black: "#000000",
  slate: "#4a5464",
  gray: "#728197",
  border: "#c1c8d1",
  mist: "#dcdfe5",
} as const;

export type IdColor = keyof typeof idColors;

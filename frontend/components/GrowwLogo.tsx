import type { SVGProps } from "react";

/**
 * Groww brand mark: a circle split by a chart line, blue above and teal below.
 * Traced from screens/Groww logo.jpg so it scales without the JPEG's white box.
 */
export function GrowwLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 64 64" role="img" aria-label="Groww" {...props}>
      <circle cx="32" cy="32" r="30" fill="#00f3bb" />
      <path
        d="M5.6 46.3 25.5 30.8 38 38.1 58.8 18.6A30 30 0 1 0 5.6 46.3Z"
        fill="#5367fe"
      />
    </svg>
  );
}

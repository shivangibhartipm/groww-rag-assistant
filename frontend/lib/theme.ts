export type Theme = "light" | "dark";

export const THEME_KEY = "groww-ai:theme";

/**
 * Applies the stored theme before the first paint.
 *
 * This has to be an inline blocking script in the document head rather than an
 * effect: React only runs effects after hydration, by which point the browser
 * has already painted the light palette, so a dark-mode user would see a white
 * flash on every load. Reading localStorage can throw when cookies are blocked,
 * hence the try/catch around it.
 */
export const THEME_INIT_SCRIPT = `(function(){try{var s=localStorage.getItem(${JSON.stringify(
  THEME_KEY,
)});var d=s?s==="dark":window.matchMedia("(prefers-color-scheme: dark)").matches;if(d)document.documentElement.classList.add("dark");}catch(e){}})();`;

export function currentTheme(): Theme {
  if (typeof document === "undefined") return "light";
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

export function applyTheme(theme: Theme) {
  const root = document.documentElement;

  // Chips and buttons carry a hover `transition`, which also animates the
  // palette swap and makes the flip arrive as a staggered cross-fade. Disable
  // transitions, force a synchronous restyle so the new colours are painted
  // flat, then re-enable them for hover.
  root.classList.add("theme-switching");
  root.classList.toggle("dark", theme === "dark");
  void root.offsetHeight;
  root.classList.remove("theme-switching");

  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    // Private browsing with storage disabled; the theme still applies for this page.
  }
}

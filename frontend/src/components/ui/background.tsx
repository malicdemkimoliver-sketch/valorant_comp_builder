/**
 * Full-viewport radial backdrop for the builder and meta pages —
 * navy fading into a deep crimson glow at the bottom edges.
 * `fixed` (not absolute) so it covers the viewport regardless of page
 * height and the gradient anchor stays put while scrolling.
 */
export function Background() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 [background:radial-gradient(125%_125%_at_50%_10%,var(--color-navy-950)_40%,#3d1015_100%)]"
    />
  );
}

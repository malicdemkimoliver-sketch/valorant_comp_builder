import { useEffect, useRef } from "react";

/**
 * Pointer-tracking spotlight for a group of cards.
 *
 * Attach the returned ref to a container with the `spotlight-group` class;
 * every `[data-glow]` descendant gets card-local --glow-x/--glow-y CSS vars
 * that the globals.css ::after rule turns into a moving glow. One listener
 * per group (not per card), rAF-throttled to one rect pass per frame.
 */
export function useSpotlight<T extends HTMLElement>() {
  const ref = useRef<T>(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    let raf = 0;
    let last: { x: number; y: number } | null = null;

    const apply = () => {
      raf = 0;
      if (!last) return;
      for (const card of root.querySelectorAll<HTMLElement>("[data-glow]")) {
        const rect = card.getBoundingClientRect();
        card.style.setProperty("--glow-x", `${last.x - rect.left}px`);
        card.style.setProperty("--glow-y", `${last.y - rect.top}px`);
      }
    };
    const onMove = (e: PointerEvent) => {
      last = { x: e.clientX, y: e.clientY };
      if (!raf) raf = requestAnimationFrame(apply);
    };

    root.addEventListener("pointermove", onMove);
    return () => {
      root.removeEventListener("pointermove", onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return ref;
}

import Link from "next/link";
import type { ComponentPropsWithoutRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const neonButtonVariants = cva(
  "group relative inline-flex items-center justify-center rounded-xl font-display font-bold tracking-[0.15em] transition-all hover:-translate-y-0.5",
  {
    variants: {
      variant: {
        default: "bg-vred text-white hover:bg-vred/90",
        ghost: "border border-vred/60 text-vred hover:bg-vred/10",
      },
      size: {
        default: "px-12 py-4 text-lg",
        sm: "px-6 py-2 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

type NeonVariantProps = VariantProps<typeof neonButtonVariants>;

/** Red neon glow layers: soft under-glow plus a bottom light line. */
function Neon() {
  return (
    <>
      <span
        aria-hidden
        className="absolute inset-0 -z-10 rounded-xl bg-vred/60 opacity-50 blur-lg transition-opacity duration-300 group-hover:opacity-90"
      />
      <span
        aria-hidden
        className="absolute -bottom-1.5 left-1/2 h-[3px] w-3/5 -translate-x-1/2 rounded-full bg-gradient-to-r from-transparent via-vred to-transparent opacity-80 blur-[2px] transition-opacity duration-300 group-hover:opacity-100"
      />
    </>
  );
}

export function NeonButton({
  className,
  variant,
  size,
  children,
  ...props
}: ComponentPropsWithoutRef<"button"> & NeonVariantProps) {
  return (
    <button
      className={cn(neonButtonVariants({ variant, size }), className)}
      {...props}
    >
      {children}
      <Neon />
    </button>
  );
}

export function NeonButtonLink({
  className,
  variant,
  size,
  children,
  ...props
}: ComponentPropsWithoutRef<typeof Link> & NeonVariantProps) {
  return (
    <Link
      className={cn(neonButtonVariants({ variant, size }), className)}
      {...props}
    >
      {children}
      <Neon />
    </Link>
  );
}

export { neonButtonVariants };

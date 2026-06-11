import type { Metadata } from "next";
import { Geist, Rajdhani } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const rajdhani = Rajdhani({
  variable: "--font-rajdhani",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Gyd's VLR Comp Builder",
  description:
    "Build winning Valorant team compositions with live meta insights — agent scoring, map tier lists, and pick suggestions.",
};

const NAV_LINKS = [
  { href: "/builder", label: "Builder" },
  { href: "/meta", label: "Meta" },
  { href: "/saved", label: "Saved" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${rajdhani.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <header className="sticky top-0 z-50 border-b border-navy-700 bg-navy-900/90 backdrop-blur">
          <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
            <Link
              href="/"
              aria-label="Gyd's VLR Comp Builder — home"
              className="flex items-center gap-3"
            >
              <span className="relative block h-9 w-40 overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/gydrenzin-logo.png"
                  alt="GYDRENZIN"
                  className="absolute top-1/2 left-0 w-full -translate-y-1/2 mix-blend-screen"
                />
              </span>
              <span className="font-display text-sm font-bold tracking-[0.2em] text-vorange">
                VLR COMP BUILDER
              </span>
            </Link>
            <div className="flex items-center gap-6">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="font-display text-sm font-semibold tracking-widest text-slate-300 uppercase transition-colors hover:text-vred"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </nav>
        </header>
        <div className="flex-1">{children}</div>
        <footer className="border-t border-navy-700 bg-navy-950 px-6 py-6 text-center text-xs text-slate-500">
          Gyd&apos;s VLR Comp Builder — community project. Game data from{" "}
          <a
            href="https://valorant-api.com"
            className="text-slate-400 underline hover:text-vred"
          >
            valorant-api.com
          </a>
          . Not affiliated with Riot Games.
        </footer>
      </body>
    </html>
  );
}

import { NeonButtonLink } from "@/components/ui/neon-button";

const HERO_BG =
  "https://media.valorant-api.com/maps/7eaecc1b-4337-bbf6-6ab9-04b8f06b3319/splash.png";

const FEATURES = [
  {
    icon: "🎯",
    name: "BUILD",
    description:
      "Pick 5 agents and get an instant comp score with grade and breakdown.",
  },
  {
    icon: "📊",
    name: "META",
    description:
      "Live tier lists per map — win rates and pick rates from real data.",
  },
  {
    icon: "💾",
    name: "SAVE",
    description:
      "Keep your best comps in your account and revisit them anytime.",
  },
  {
    icon: "🔍",
    name: "ANALYZE",
    description:
      "Strengths, weaknesses, warnings, and suggested picks for every comp.",
  },
];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section
        className="relative flex min-h-[88vh] flex-col items-center justify-center px-6 py-16 text-center"
        style={{
          backgroundImage: `linear-gradient(135deg, rgba(15,25,35,0.90) 0%, rgba(26,35,50,0.84) 50%, rgba(45,27,61,0.90) 100%), url('${HERO_BG}')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <h1 className="animate-float">
          <span className="sr-only">Gyd&apos;s VLR Comp Builder</span>
          <span className="relative mx-auto block h-[80px] w-[340px] overflow-hidden sm:h-[110px] sm:w-[500px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/gydrenzin-logo.png"
              alt="GYDRENZIN"
              className="absolute top-1/2 left-0 w-full -translate-y-1/2 mix-blend-screen drop-shadow-[0_4px_24px_rgba(255,255,255,0.25)]"
            />
          </span>
          <span className="mt-2 block font-display text-3xl font-bold tracking-[0.25em] text-vorange drop-shadow-[0_4px_24px_rgba(255,140,66,0.35)] sm:text-5xl">
            VLR COMP BUILDER
          </span>
        </h1>
        <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-300 sm:text-lg">
          Create winning team compositions with VCT meta insights. Analyze
          agent picks and build the perfect team.
        </p>
        <div className="mt-7 rounded-full border border-sentinel px-5 py-1.5 font-display text-xs font-bold tracking-[0.25em] text-sentinel">
          🔓 NO LOGIN REQUIRED
        </div>
        <div className="mt-14 flex flex-col items-center gap-1 text-xs uppercase tracking-[0.3em] text-slate-400">
          <span>Scroll down</span>
          <span className="animate-bounce-down text-2xl leading-none text-vred">
            ⌄
          </span>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto grid max-w-6xl gap-4 px-6 py-14 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((feature) => (
          <div
            key={feature.name}
            className="rounded-xl border border-vred/20 bg-white/[0.025] p-6 transition-all hover:-translate-y-1.5 hover:border-vred hover:shadow-[0_12px_28px_rgba(255,70,85,0.12)]"
          >
            <div className="text-3xl">{feature.icon}</div>
            <div className="mt-3 mb-2 font-display text-lg font-bold tracking-[0.15em] text-vred">
              {feature.name}
            </div>
            <p className="text-sm leading-relaxed text-slate-400">
              {feature.description}
            </p>
          </div>
        ))}
      </section>

      {/* CTA */}
      <section className="flex justify-center px-6 pb-16">
        <NeonButtonLink href="/builder">
          🎮 LET&apos;S BUILD A COMP!
        </NeonButtonLink>
      </section>
    </main>
  );
}

import Link from "next/link";
import { auth, signIn } from "@/auth";
import { savedCompsHeaders, savedCompsUrl } from "@/lib/backend";
import { DeleteCompButton } from "@/components/saved/delete-comp-button";

type SavedComp = {
  id: string;
  name: string;
  map: string;
  agents: string[];
  code: string | null;
  score: number | null;
  grade: string | null;
  notes: string;
  saved_at: string;
};

function Heading() {
  return (
    <h1 className="font-display text-3xl font-bold tracking-[0.1em]">
      <span className="text-vred">SAVED</span>{" "}
      <span className="text-vorange">COMPS</span>
    </h1>
  );
}

export default async function Saved() {
  const session = await auth();

  if (!session?.user?.email) {
    return (
      <main className="mx-auto flex max-w-6xl flex-col items-center px-6 py-24 text-center">
        <Heading />
        <p className="mt-4 text-sm text-slate-400">
          Sign in with Google to save comps and revisit them anytime.
        </p>
        <form
          action={async () => {
            "use server";
            await signIn("google");
          }}
          className="mt-6"
        >
          <button
            type="submit"
            className="rounded bg-vred/15 px-5 py-2 font-display text-sm font-bold tracking-widest text-vred uppercase transition-colors hover:bg-vred hover:text-white"
          >
            Sign in
          </button>
        </form>
      </main>
    );
  }

  const res = await fetch(savedCompsUrl(), {
    headers: savedCompsHeaders(session.user.email),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`saved comps fetch failed: ${res.status}`);
  }
  const comps: SavedComp[] = await res.json();
  // Newest first — db.json appends
  comps.reverse();

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <div className="mb-8 flex items-baseline justify-between">
        <Heading />
        <span className="font-display text-sm tracking-[0.2em] text-slate-400">
          {comps.length} {comps.length === 1 ? "COMP" : "COMPS"}
        </span>
      </div>

      {comps.length === 0 ? (
        <p className="text-sm text-slate-400">
          Nothing saved yet — build a comp and hit{" "}
          <span className="font-bold text-vred">SAVE COMP</span> in the{" "}
          <Link href="/builder" className="underline hover:text-vred">
            builder
          </Link>
          .
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {comps.map((comp) => (
            <div
              key={comp.id}
              className="flex flex-col rounded-xl border border-navy-700 bg-navy-800/40 p-5"
            >
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="truncate font-display text-base font-bold tracking-wider text-slate-200">
                  {comp.name}
                </h2>
                {comp.grade && (
                  <span className="font-display text-lg font-bold text-vorange">
                    {comp.grade}
                  </span>
                )}
              </div>
              <p className="mt-0.5 font-display text-xs tracking-[0.2em] text-slate-400 uppercase">
                {comp.map}
                {comp.score != null && ` · ${Math.round(comp.score)}/100`}
              </p>

              <p className="mt-3 text-xs text-slate-300">
                {comp.agents.join(" · ")}
              </p>
              {comp.notes && (
                <p className="mt-2 text-[11px] text-slate-500">{comp.notes}</p>
              )}
              {comp.code && (
                <p className="mt-2 truncate rounded bg-navy-900 px-2 py-1 text-center font-mono text-[10px] text-slate-400">
                  {comp.code}
                </p>
              )}

              <div className="mt-4 flex items-center justify-between border-t border-navy-700/60 pt-3">
                <Link
                  href={`/builder?map=${encodeURIComponent(comp.map)}&agents=${encodeURIComponent(comp.agents.join(","))}`}
                  className="rounded bg-vred/15 px-3 py-1.5 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
                >
                  LOAD IN BUILDER
                </Link>
                <DeleteCompButton id={comp.id} />
              </div>
              <p className="mt-2 text-right text-[10px] text-slate-600">
                {new Date(comp.saved_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

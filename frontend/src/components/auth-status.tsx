import { auth, signIn, signOut } from "@/auth";

/**
 * Nav session widget (server component, sign-in/out via server actions).
 * Reading auth() makes the layout render dynamically per request — fine
 * here, every page already fetches live data.
 */
export async function AuthStatus() {
  const session = await auth();

  if (!session?.user) {
    return (
      <form
        action={async () => {
          "use server";
          await signIn("google");
        }}
      >
        <button
          type="submit"
          className="rounded bg-vred/15 px-3 py-1.5 font-display text-xs font-bold tracking-widest text-vred uppercase transition-colors hover:bg-vred hover:text-white"
        >
          Sign in
        </button>
      </form>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {session.user.image && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={session.user.image}
          alt=""
          referrerPolicy="no-referrer"
          className="h-7 w-7 rounded-full border border-navy-700"
        />
      )}
      <span className="hidden text-xs text-slate-300 sm:block">
        {session.user.name}
      </span>
      <form
        action={async () => {
          "use server";
          await signOut();
        }}
      >
        <button
          type="submit"
          className="text-[11px] font-bold tracking-wider text-slate-500 uppercase transition-colors hover:text-vred"
        >
          Sign out
        </button>
      </form>
    </div>
  );
}

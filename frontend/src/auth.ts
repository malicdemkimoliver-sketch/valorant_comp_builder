import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

/**
 * Google sign-in, JWT sessions, no DB adapter — the user's email is the
 * identity key, matching the saved-comps storage in data/db.json.
 * Credentials come from AUTH_GOOGLE_ID / AUTH_GOOGLE_SECRET / AUTH_SECRET
 * in .env.local (auto-detected by NextAuth v5).
 */
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [Google],
  session: { strategy: "jwt" },
});

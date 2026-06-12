import type { NextConfig } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        // Proxy the backend API, EXCLUDING /api/auth/* (NextAuth's dynamic
        // route would lose to afterFiles rewrites) and /api/saved* (handled
        // by session-checked Next route handlers; keeping them off the proxy
        // also stops browsers reaching FastAPI's saved-comps directly).
        source: "/api/:path((?!auth|saved).*)",
        destination: `${API_URL}/api/:path`,
      },
    ];
  },
};

export default nextConfig;

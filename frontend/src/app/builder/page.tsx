const API_URL = process.env.API_URL ?? "http://localhost:8000";

const ROLES: { name: string; colorClass: string }[] = [
  { name: "Duelist", colorClass: "text-duelist border-duelist" },
  { name: "Initiator", colorClass: "text-initiator border-initiator" },
  { name: "Controller", colorClass: "text-controller border-controller" },
  { name: "Sentinel", colorClass: "text-sentinel border-sentinel" },
];

type Agent = {
  name: string;
  role: string;
  icon: string;
  display_icon: string | null;
  curated: boolean;
};

async function getAgents(): Promise<Agent[]> {
  const res = await fetch(`${API_URL}/api/agents`);
  if (!res.ok) {
    throw new Error(`Failed to fetch agents: ${res.status}`);
  }
  return res.json();
}

export default async function Builder() {
  const agents = await getAgents();

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="font-display text-3xl font-bold tracking-[0.1em]">
        <span className="text-vred">COMP</span>{" "}
        <span className="text-vorange">BUILDER</span>
      </h1>
      <p className="mt-2 mb-10 text-sm text-slate-400">
        {agents.length} agents loaded — interactive builder coming in Phase 3.
      </p>
      {ROLES.map((role) => (
        <section key={role.name} className="mb-10">
          <h2
            className={`mb-4 border-l-4 pl-3 font-display text-xl font-bold tracking-[0.15em] uppercase ${role.colorClass}`}
          >
            {role.name}s
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {agents
              .filter((agent) => agent.role === role.name)
              .map((agent) => (
                <div
                  key={agent.name}
                  className="flex items-center gap-3 rounded-lg border border-navy-700 bg-navy-800/50 p-3 transition-colors hover:border-vred/60"
                >
                  {agent.display_icon ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={agent.display_icon}
                      alt={agent.name}
                      className="h-10 w-10 rounded-full border border-navy-700"
                    />
                  ) : (
                    <span>{agent.icon}</span>
                  )}
                  <span className="font-medium">{agent.name}</span>
                  {!agent.curated && (
                    <span className="ml-auto rounded bg-navy-700 px-1.5 py-0.5 text-xs text-slate-400">
                      NEW
                    </span>
                  )}
                </div>
              ))}
          </div>
        </section>
      ))}
    </main>
  );
}

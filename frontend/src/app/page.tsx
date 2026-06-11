const API_URL = process.env.API_URL ?? "http://localhost:8000";

const ROLE_ORDER = ["Duelist", "Initiator", "Controller", "Sentinel"];

type Agent = {
  name: string;
  role: string;
  icon: string;
  display_icon: string | null;
  curated: boolean;
  strengths: string[];
  weaknesses: string[];
  good_maps: string[];
  synergy_tags: string[];
  utility: string[];
};

async function getAgents(): Promise<Agent[]> {
  const res = await fetch(`${API_URL}/api/agents`);
  if (!res.ok) {
    throw new Error(`Failed to fetch agents: ${res.status}`);
  }
  return res.json();
}

export default async function Home() {
  const agents = await getAgents();
  const roles = ROLE_ORDER.filter((role) =>
    agents.some((agent) => agent.role === role)
  );

  return (
    <main className="mx-auto max-w-4xl p-8">
      <h1 className="mb-2 text-3xl font-bold">Valorant Comp Builder</h1>
      <p className="mb-8 text-sm opacity-70">
        {agents.length} agents served by the FastAPI backend
      </p>
      {roles.map((role) => (
        <section key={role} className="mb-8">
          <h2 className="mb-3 text-xl font-semibold">{role}</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {agents
              .filter((agent) => agent.role === role)
              .map((agent) => (
                <div
                  key={agent.name}
                  className="flex items-center gap-3 rounded-lg border border-neutral-700 p-3"
                >
                  {agent.display_icon ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={agent.display_icon}
                      alt={agent.name}
                      className="h-10 w-10 rounded-full border border-neutral-600"
                    />
                  ) : (
                    <span>{agent.icon}</span>
                  )}
                  <span className="font-medium">{agent.name}</span>
                  {!agent.curated && (
                    <span className="ml-auto rounded bg-neutral-800 px-1.5 py-0.5 text-xs opacity-60">
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

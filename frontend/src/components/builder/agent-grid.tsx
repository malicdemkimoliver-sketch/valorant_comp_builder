import type { Agent, RatedMetaEntry } from "@/lib/types";
import { ROLE_ORDER } from "@/lib/types";
import { useSpotlight } from "@/lib/use-spotlight";
import { AgentCard } from "./agent-card";

const ROLE_HEADER: Record<string, string> = {
  Duelist: "text-duelist border-duelist",
  Initiator: "text-initiator border-initiator",
  Controller: "text-controller border-controller",
  Sentinel: "text-sentinel border-sentinel",
};

export function AgentGrid({
  agents,
  selected,
  metaByName,
  onToggle,
}: {
  agents: Agent[];
  selected: string[];
  metaByName: Record<string, RatedMetaEntry>;
  onToggle: (name: string) => void;
}) {
  const full = selected.length >= 5;
  const spotlightRef = useSpotlight<HTMLDivElement>();

  return (
    <div ref={spotlightRef} className="spotlight-group">
      {ROLE_ORDER.map((role) => (
        <section key={role} className="mb-6">
          <h2
            className={`mb-3 border-l-4 pl-3 font-display text-lg font-bold tracking-[0.15em] uppercase ${ROLE_HEADER[role]}`}
          >
            {role}s
          </h2>
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-5">
            {agents
              .filter((agent) => agent.role === role)
              .map((agent) => (
                <AgentCard
                  key={agent.name}
                  agent={agent}
                  selected={selected.includes(agent.name)}
                  disabled={full && !selected.includes(agent.name)}
                  meta={metaByName[agent.name]}
                  onToggle={onToggle}
                />
              ))}
          </div>
        </section>
      ))}
    </div>
  );
}

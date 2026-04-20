import { ResultCard } from "@/components/ResultCard";
import { SaveIncidentModal, type SaveIncidentDraft } from "@/components/SaveIncidentModal";
import type { DiagnoseResponse } from "@/lib/api";

type DiagnosePanelProps = {
  result: DiagnoseResponse | null;
  saveDefaults: SaveIncidentDraft;
  transcript: string | null;
  onSave: (draft: SaveIncidentDraft) => Promise<void>;
};

function confidenceLabel(confidence: number): string {
  return `${Math.round(confidence * 100)}% confidence`;
}

export function DiagnosePanel({ result, saveDefaults, transcript, onSave }: DiagnosePanelProps) {
  const evidence = result?.evidence;
  const recommendations = result?.recommended_steps ?? [];

  return (
    <section className="space-y-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">Diagnosis</p>
          <h2 className="text-2xl font-semibold">Evidence-backed recommendations</h2>
        </div>
        <div className="rounded-full border border-zinc-800 px-3 py-1 text-sm text-zinc-400">
          {result ? confidenceLabel(result.confidence) : "Awaiting input"}
        </div>
      </div>
      {transcript ? (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4 text-sm text-zinc-300">
          <p className="mb-1 text-xs uppercase tracking-[0.2em] text-zinc-500">Transcript</p>
          {transcript}
        </div>
      ) : null}
      <ResultCard
        title="Manual section"
        body={evidence?.manual_section?.snippet ?? "Manual retrieval will appear here once search finds a match."}
        meta={evidence?.manual_section ? `${evidence.manual_section.source} ? page ${evidence.manual_section.page ?? "?"}` : "manual"}
      />
      <ResultCard
        title="Similar incident"
        body={
          evidence?.similar_incident
            ? `${evidence.similar_incident.fix_applied} (downtime ${evidence.similar_incident.downtime_min ?? "?"} min)`
            : "Historical incident evidence will appear here once search finds a match."
        }
        meta={evidence?.similar_incident?.id ?? "incident"}
      />
      <ResultCard
        title="Candidate part"
        body={
          evidence?.candidate_part
            ? `${evidence.candidate_part.part_no} ? ${evidence.candidate_part.name}`
            : "Part recommendations will appear here once parts are ingested."
        }
        meta="part"
      />
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
        <p className="mb-2 text-xs uppercase tracking-[0.2em] text-zinc-500">Recommended steps</p>
        {recommendations.length > 0 ? (
          <ol className="space-y-2 text-sm text-zinc-200">
            {recommendations.map((step) => (
              <li key={step} className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2">
                {step}
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-zinc-500">Run a diagnosis to generate deterministic next steps.</p>
        )}
      </div>
      <SaveIncidentModal defaults={saveDefaults} disabled={result === null} onSave={onSave} />
    </section>
  );
}

import { SaveIncidentModal, type SaveIncidentDraft } from "@/components/SaveIncidentModal";
import type { DiagnoseResponse } from "@/lib/api";

type DiagnosePanelProps = {
  result: DiagnoseResponse | null;
  saveDefaults: SaveIncidentDraft;
  transcript: string | null;
  onSave: (draft: SaveIncidentDraft) => Promise<void>;
};

type ConfidenceTone = {
  label: string;
  explanation: string;
  band: string;
  pill: string;
};

function toneFor(confidence: number): ConfidenceTone {
  if (confidence >= 0.6) {
    return {
      label: "High",
      explanation: "All three evidence slots matched with strong identifier overlap.",
      band: "border-emerald-500/30 bg-emerald-500/10",
      pill: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
    };
  }
  if (confidence >= 0.3) {
    return {
      label: "Medium",
      explanation: "Partial evidence match. Review the manual section before acting.",
      band: "border-amber-500/30 bg-amber-500/10",
      pill: "border-amber-500/40 bg-amber-500/10 text-amber-300",
    };
  }
  return {
    label: "Low",
    explanation: "Weak signal. Treat suggestions as a starting point, not a prescription.",
    band: "border-red-500/30 bg-red-500/10",
    pill: "border-red-500/40 bg-red-500/10 text-red-300",
  };
}

export function DiagnosePanel({ result, saveDefaults, transcript, onSave }: DiagnosePanelProps) {
  const evidence = result?.evidence;
  const recommendations = result?.recommended_steps ?? [];
  const tone = result ? toneFor(result.confidence) : null;
  const confidencePct = result ? Math.round(result.confidence * 100) : null;

  const manual = evidence?.manual_section;
  const incident = evidence?.similar_incident;
  const part = evidence?.candidate_part;

  return (
    <section className="space-y-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">Diagnosis</p>
          <h2 className="text-2xl font-semibold">Evidence-backed recommendations</h2>
        </div>
        {tone && confidencePct !== null ? (
          <div className={`rounded-full border px-3 py-1 text-sm font-medium ${tone.pill}`}>
            {tone.label} · {confidencePct}%
          </div>
        ) : (
          <div className="rounded-full border border-zinc-800 px-3 py-1 text-sm text-zinc-400">
            Awaiting input
          </div>
        )}
      </div>

      {transcript ? (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4 text-sm text-zinc-300">
          <p className="mb-1 text-xs uppercase tracking-[0.2em] text-zinc-500">Voice transcript</p>
          {transcript}
        </div>
      ) : null}

      {tone ? (
        <div className={`rounded-2xl border p-4 text-sm ${tone.band}`}>
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-400">Confidence</p>
          <p className="mt-1 text-zinc-200">{tone.explanation}</p>
        </div>
      ) : null}

      <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Recommended steps</p>
        {recommendations.length > 0 ? (
          <ol className="mt-3 space-y-2">
            {recommendations.map((step, index) => (
              <li
                key={step}
                className="flex items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-950/80 px-3 py-2 text-sm text-zinc-100"
              >
                <span className="mt-0.5 inline-flex h-6 w-6 flex-none items-center justify-center rounded-full bg-emerald-500/20 text-xs font-semibold text-emerald-300">
                  {index + 1}
                </span>
                <span className="text-zinc-100">{step}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="mt-3 text-sm text-zinc-500">Run a diagnosis to generate deterministic next steps.</p>
        )}
      </div>

      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Evidence</p>

        <article className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-100">Manual section</h3>
            <span className="text-xs text-zinc-500">
              {manual ? `${manual.source} · page ${manual.page ?? "?"}` : "—"}
            </span>
          </div>
          <p className="mt-2 text-sm text-zinc-300">
            {manual?.snippet ?? "Manual retrieval will appear here once search finds a match."}
          </p>
        </article>

        <article className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-100">Similar incident</h3>
            <span className="text-xs text-zinc-500">{incident?.id ?? "—"}</span>
          </div>
          <p className="mt-2 text-sm text-zinc-300">
            {incident
              ? `${incident.fix_applied} (downtime ${incident.downtime_min ?? "?"} min)`
              : "Historical incident evidence will appear here once search finds a match."}
          </p>
        </article>

        <article className="rounded-2xl border border-zinc-800 bg-zinc-900 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-100">Candidate part</h3>
            <span className="text-xs text-zinc-500">{part?.part_no ?? "—"}</span>
          </div>
          <p className="mt-2 text-sm text-zinc-300">
            {part ? part.name : "Part recommendations will appear here once parts are ingested."}
          </p>
        </article>
      </div>

      <SaveIncidentModal defaults={saveDefaults} disabled={result === null} onSave={onSave} />
    </section>
  );
}

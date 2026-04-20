"use client";

import { useMemo, useState } from "react";

import { DiagnosePanel } from "@/components/DiagnosePanel";
import { FilterPanel, type FilterValues } from "@/components/FilterPanel";
import { OfflineBanner } from "@/components/OfflineBanner";
import { SearchBar } from "@/components/SearchBar";
import { UploadZone } from "@/components/UploadZone";
import { type SaveIncidentDraft } from "@/components/SaveIncidentModal";
import { diagnose, saveIncident, type DiagnoseResponse } from "@/lib/api";

const emptyFilters: FilterValues = {
  machineType: "",
  severity: "",
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<FilterValues>(emptyFilters);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<DiagnoseResponse | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const normalizedFilters = useMemo(() => {
    const payload: Record<string, string> = {};
    if (filters.machineType) payload.machine_type = filters.machineType;
    if (filters.severity) payload.severity = filters.severity;
    return payload;
  }, [filters]);

  const saveDefaults = useMemo<SaveIncidentDraft>(
    () => ({
      machine_type: filters.machineType,
      model_no: "",
      fault_code: "",
      fix_applied: "",
      downtime_min: "",
      parts_used: result?.evidence.candidate_part?.part_no ?? "",
      severity: filters.severity,
      symptom: query || transcript || "",
    }),
    [filters.machineType, filters.severity, query, result?.evidence.candidate_part?.part_no, transcript],
  );

  async function handleDiagnose(): Promise<void> {
    setLoading(true);
    setError(null);
    setSaveMessage(null);
    try {
      const response = await diagnose({
        query,
        file: selectedFile,
        filters: normalizedFilters,
      });
      setResult(response);
      setTranscript(response.transcript ?? null);
    } catch (diagnoseError) {
      const message = diagnoseError instanceof Error ? diagnoseError.message : "Diagnosis failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(draft: SaveIncidentDraft): Promise<void> {
    if (result === null) {
      return;
    }
    const incidentRow = {
      id: `manual-save-${Date.now()}`,
      machine_type: draft.machine_type.trim(),
      model_no: draft.model_no.trim(),
      fault_code: draft.fault_code.trim(),
      severity: draft.severity.trim() || null,
      symptom: draft.symptom.trim(),
      fix_applied: draft.fix_applied.trim(),
      downtime_min: Number(draft.downtime_min),
      parts_used: draft.parts_used.trim() || null,
      part_no: draft.parts_used.trim() || null,
      verified: true,
    };

    try {
      setError(null);
      const saved = await saveIncident(incidentRow);
      setSaveMessage(`Saved incident ${saved.id}`);
    } catch (saveError) {
      throw (saveError instanceof Error ? saveError : new Error("Save failed"));
    }
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <OfflineBanner />
        <header className="space-y-2">
          <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">FixFirst Edge</p>
          <h1 className="text-4xl font-semibold">Offline maintenance copilot</h1>
          <p className="max-w-3xl text-zinc-400">
            Search manuals, incidents, parts, and voice notes locally.
          </p>
        </header>
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="space-y-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
            <SearchBar query={query} onQueryChange={setQuery} onSubmit={handleDiagnose} />
            <UploadZone file={selectedFile} onFileSelect={setSelectedFile} />
            <FilterPanel values={filters} onChange={setFilters} />
            <button
              className="inline-flex w-full items-center justify-center rounded-xl bg-emerald-500 px-4 py-3 text-sm font-medium text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading || (!query.trim() && selectedFile === null)}
              onClick={() => {
                void handleDiagnose();
              }}
            >
              {loading ? "Diagnosing..." : "Run diagnosis"}
            </button>
            {error ? <p className="text-sm text-red-400">{error}</p> : null}
            {saveMessage ? <p className="text-sm text-emerald-300">{saveMessage}</p> : null}
          </section>
          <DiagnosePanel result={result} saveDefaults={saveDefaults} transcript={transcript} onSave={handleSave} />
        </div>
      </div>
    </main>
  );
}

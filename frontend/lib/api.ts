export type HealthResponse = {
  status: "ok";
  online: false;
  db: string | boolean;
  collection_ready: boolean;
};

export type DiagnoseResponse = {
  evidence: {
    manual_section: {
      source: string;
      page: number | null;
      snippet: string;
    } | null;
    similar_incident: {
      id: string;
      fix_applied: string;
      downtime_min: number | null;
    } | null;
    candidate_part: {
      part_no: string;
      name: string;
    } | null;
  };
  confidence: number;
  recommended_steps: string[];
  transcript: string | null;
};

export type IncidentSaveRow = {
  fault_code: string;
  fix_applied: string;
  id: string;
  machine_type: string;
  model_no: string;
  downtime_min: number;
  part_no: string | null;
  parts_used: string | null;
  severity: string | null;
  symptom: string;
  verified: boolean;
};

type DiagnoseRequest = {
  query: string;
  file: File | null;
  filters: Record<string, string>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

export async function diagnose({ query, file, filters }: DiagnoseRequest): Promise<DiagnoseResponse> {
  const body = new FormData();
  if (query.trim()) {
    body.append("query", query.trim());
  }
  if (file !== null) {
    if (file.type.startsWith("image/")) {
      body.append("image", file);
    } else if (file.type.startsWith("audio/")) {
      body.append("voice", file);
    }
  }
  if (Object.keys(filters).length > 0) {
    body.append("filters", JSON.stringify(filters));
  }

  const response = await fetch(`${API_BASE}/api/diagnose`, {
    body,
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(`Diagnose request failed: ${response.status}`);
  }
  return (await response.json()) as DiagnoseResponse;
}

export async function saveIncident(row: IncidentSaveRow): Promise<{ id: string }> {
  const response = await fetch(`${API_BASE}/api/incident/save`, {
    body: JSON.stringify({ row }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(`Save incident failed: ${response.status}`);
  }
  return (await response.json()) as { id: string };
}

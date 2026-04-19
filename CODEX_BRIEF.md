# FixFirst Edge — Codex Implementation Brief

**Hackathon**: Actian VectorAI DB Build Challenge
**Deadline**: Apr 18 2026, 18:00 UTC
**Working directory**: `C:\Users\HP\Desktop\Github files\fixfirst-edge\`
**Owner OS**: Windows 11, 16 GB RAM, no Apple Silicon, no GPU, **zero budget**
**Recommended dev shell**: WSL2 Ubuntu 22.04 for the Python backend; Windows-native or WSL2 for the Next.js frontend.

---

## 1. Mission (one paragraph)

Build **FixFirst Edge** — an offline multimodal maintenance copilot for industrial technicians. A user can search by photo of a broken part, error code, voice note, manual text, or past incident, and get back evidence-based fix recommendations. Everything runs locally with no internet. The vector store is **Actian VectorAI DB** (early-access Docker image). The project must hit all three Actian features judges care about: **Named Vectors / Multimodal**, **Filtered Search**, and **Hybrid Fusion (RRF)**.

---

## 2. Hard constraints — read before writing any code

1. **No cloud APIs.** No OpenAI, Anthropic, Cohere, HuggingFace Inference API, or any hosted model. All inference is local. The "works offline" judging bonus depends on this.
2. **No Claude / Anthropic / Codex / OpenAI attribution** anywhere — no commit messages, no comments, no README mentions, no Co-Authored-By tags.
3. **No generative LLM in the diagnostic answer.** The "recommended steps" panel is **templated from retrieved evidence** (top manual chunk + top historical incident + top part match). Industrial users need auditable, deterministic answers, not hallucinated ones. This also keeps the project Actian-centric (judging weight 30%).
4. **Read first, write second.** Never edit a file you haven't read. Match the existing style of any file you touch.
5. **Simplest correct solution.** No premature abstractions, no speculative generality, no "future-proofing." Three similar lines beat one clever abstraction.
6. **No bloat.** Don't add features that aren't asked for. Don't add docstrings or comments to code you didn't change. Don't add error handling for impossible scenarios. Don't add logging/metrics unless explicitly listed below.
7. **No placeholder code.** No `# TODO: implement`, no `pass`, no `raise NotImplementedError`. If you can't complete a function, stop and report — don't ship a stub.
8. **No comments unless WHY is non-obvious.** No "explain what the code does" comments — naming should do that. One-line comments only when documenting a non-obvious constraint.
9. **The Actian SDK is unknown to you.** A bundle is being delivered to the owner. Build everything that does not depend on Actian first. When you reach Phase D (DB layer), **STOP and wait** — do not invent Actian API surface.
10. **Type hints everywhere in Python. No `any` in TypeScript** unless interfacing with a genuinely untyped external source.

---

## 3. Tech stack (pinned)

### Backend (Python 3.11, run inside WSL2)
- `fastapi==0.115.0`
- `uvicorn[standard]==0.32.0`
- `pydantic==2.9.2`
- `python-multipart==0.0.12` (file uploads)
- `pdfplumber==0.11.4` (PDF text extraction)
- `sentence-transformers==3.2.1` (text + image via CLIP wrapper)
- `faster-whisper==1.0.3` (audio transcription, model `tiny.en`)
- `numpy==2.1.2`
- `pandas==2.2.3` (CSV handling)
- `python-dotenv==1.0.1`
- `pytest==8.3.3`
- `httpx==0.27.2` (test client)
- Actian SDK: **TBD — added in Phase D when bundle arrives**

### Frontend (Node 20)
- `next@14` (app router)
- `react@18`, `react-dom@18`
- `typescript@5`
- `tailwindcss@3`
- `lucide-react` (icons)
- `react-dropzone` (file upload)
- `swr` (data fetching)

### Infra
- Docker Desktop for Windows + WSL2 backend
- `docker-compose.yml` with two services: `actian` (image TBD) and `backend` (our FastAPI)
- Frontend runs outside Docker for fast HMR during the hackathon

---

## 4. Folder structure to create

```
fixfirst-edge/
├── CODEX_BRIEF.md                 # this file
├── .gitignore
├── .env.example
├── docker-compose.yml             # Actian + backend (frontend runs separately)
├── README.md                      # written in Phase G — DO NOT write yet
├── data/
│   ├── raw/                       # owner drops PDFs/images/CSVs/WAVs here
│   │   ├── manuals/
│   │   ├── images/
│   │   ├── voice/
│   │   ├── incidents.csv
│   │   ├── parts.csv
│   │   └── error_codes.csv
│   └── processed/                 # generated artifacts (gitignored)
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .python-version            # 3.11
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── config.py              # env vars, paths, model names
│   │   ├── db.py                  # Actian abstraction — Phase D
│   │   ├── schemas.py             # pydantic request/response models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py
│   │   │   ├── search.py
│   │   │   ├── diagnose.py
│   │   │   └── health.py
│   │   ├── pipelines/
│   │   │   ├── __init__.py
│   │   │   ├── text_embedder.py
│   │   │   ├── image_embedder.py
│   │   │   ├── audio_transcriber.py
│   │   │   ├── pdf_chunker.py
│   │   │   └── csv_loader.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ingest_service.py
│   │       ├── search_service.py
│   │       └── diagnose_service.py
│   ├── scripts/
│   │   ├── bulk_ingest.py         # one-shot loader for data/raw/
│   │   └── verify_offline.py      # smoke test that queries with no internet
│   └── tests/
│       ├── test_text_embedder.py
│       ├── test_image_embedder.py
│       ├── test_audio_transcriber.py
│       ├── test_pdf_chunker.py
│       └── test_diagnose.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx               # main UI
    │   └── globals.css
    ├── components/
    │   ├── UploadZone.tsx
    │   ├── SearchBar.tsx
    │   ├── FilterPanel.tsx
    │   ├── ResultCard.tsx
    │   ├── DiagnosePanel.tsx
    │   ├── SaveIncidentModal.tsx
    │   └── OfflineBanner.tsx
    └── lib/
        └── api.ts
```

---

## 5. Phased implementation (build in this order)

### Phase A — Scaffold (target: 1 hour, no Actian dependency)

- Create the folder tree above (empty files where needed).
- Initialize git: `git init`, write `.gitignore` (ignore `data/raw/`, `data/processed/`, `.env`, `node_modules/`, `__pycache__/`, `.venv/`, `*.pyc`, `.pytest_cache/`, `.next/`, model cache dirs).
- Write `.env.example` with: `ACTIAN_HOST`, `ACTIAN_PORT`, `ACTIAN_API_KEY`, `MODEL_CACHE_DIR=./data/processed/models`, `BACKEND_PORT=8000`.
- Write `docker-compose.yml` with placeholder for `actian` service (image name TBD — leave `image: TBD_ACTIAN_IMAGE` and a `# Phase D: replace with real image from bundle` comment) and the `backend` service building from `./backend`.
- Backend: write `pyproject.toml` + `requirements.txt` with the pinned deps above.
- Frontend: `npx create-next-app@14 frontend --typescript --tailwind --app --no-src-dir --no-eslint --import-alias "@/*"` then add the components folder.
- FastAPI `main.py`: app + `/api/health` returning `{"status": "ok", "online": false, "db": "unknown"}`. Wire health router only.
- Verify: `uvicorn app.main:app --reload` from `backend/`, hit `/api/health`, get JSON.

### Phase B — Embedding + parsing pipelines (target: 3 hours, no Actian dependency)

Each module has one responsibility. Each has a unit test that loads tiny fixtures and asserts shapes.

**`pipelines/text_embedder.py`**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

_model: SentenceTransformer | None = None

def _load() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _model

def embed_text(text: str) -> np.ndarray:
    return _load().encode(text, normalize_embeddings=True)

def embed_texts(texts: list[str]) -> np.ndarray:
    return _load().encode(texts, normalize_embeddings=True, batch_size=32)
```
Output dim: **384**. Test asserts shape `(384,)` for single, `(N, 384)` for batch.

**`pipelines/image_embedder.py`**
Use `sentence-transformers` CLIP wrapper: `SentenceTransformer("clip-ViT-B-32")`. Functions: `embed_image(path: str) -> np.ndarray`, `embed_images(paths: list[str]) -> np.ndarray`. Output dim: **512**. Accepts JPG/PNG.

**`pipelines/audio_transcriber.py`**
Use `faster-whisper` with model `tiny.en`. Function: `transcribe(path: str) -> str`. Test on a 3-second WAV fixture saying "test one two three"; assert transcript contains "test".

**`pipelines/pdf_chunker.py`**
Use `pdfplumber`. Function: `chunk_pdf(path: str, target_tokens: int = 400, overlap: int = 50) -> list[dict]`. Each chunk dict: `{"text": str, "page": int, "chunk_id": int, "source": str}`. Approximate tokens as `len(text.split()) * 1.3`.

**`pipelines/csv_loader.py`**
Functions: `load_incidents(path: str) -> list[dict]`, `load_parts(path: str) -> list[dict]`, `load_error_codes(path: str) -> list[dict]`. Use pandas. Assert required columns are present, raise on missing.

Run `pytest backend/tests/` — all should pass before moving on.

### Phase C — STOP

Before writing the DB layer, **wait for the Actian bundle to arrive**. Do not guess the SDK shape. The owner will paste the SDK examples here when received.

While waiting, you may safely:
- Polish the frontend scaffolding (UploadZone, SearchBar, FilterPanel — see Phase G shapes below — but stub out API calls)
- Build the bulk ingest script structure (without the DB write step)
- Add more tests

### Phase D — DB layer (target: 2 hours, requires Actian bundle)

Implement `app/db.py` against the real Actian Python SDK. The interface to implement:

```python
# app/db.py
from typing import Literal
import numpy as np

DocType = Literal["manual", "incident", "part", "error_code", "voice_note"]

def init_collection() -> None:
    """Create the `incidents` collection with three named vectors:
       text_vec (384), image_vec (512), audio_text_vec (384),
       and the metadata schema below."""

def upsert(
    *,
    doc_id: str,
    text_vec: np.ndarray | None,
    image_vec: np.ndarray | None,
    audio_text_vec: np.ndarray | None,
    metadata: dict,  # see schema in section 7
) -> None: ...

def search_text(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]: ...
def search_image(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]: ...
def search_audio(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]: ...
def search_hybrid(query_text: str, query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]:
    """RRF fusion of text_vec ANN and BM25 keyword search over text_content."""

def health() -> bool: ...
```

Each search function returns `list[{"id": str, "score": float, "metadata": dict}]`.

### Phase E — Ingest endpoints (target: 3 hours)

Wire `routers/ingest.py` with the 5 endpoints listed in section 6. Each delegates to `services/ingest_service.py` which calls pipelines + `db.upsert`.

Then write `scripts/bulk_ingest.py`: walks `data/raw/`, calls each ingest endpoint via httpx, prints progress. After running, the `incidents` collection should hold ~150-200 records.

### Phase F — Search + diagnose endpoints (target: 5 hours)

`routers/search.py` — 4 endpoints (text, image, voice, multimodal). Each: embed query → call `db.search_*` with optional filters → return results.

`routers/diagnose.py` — `/api/diagnose`. Logic:
1. If `query` provided: hybrid search filtered by `doc_type=manual` → top manual section.
2. Filter by `doc_type=incident` (and any user filters): top similar incident.
3. Filter by `doc_type=part` (and incident's `fits_models`): candidate part.
4. Build `recommended_steps: list[str]` from a template:
   - `f"Per {manual.source} p.{manual.page}: {manual.snippet[:200]}"`
   - `f"Previous incident on {incident.machine_id} resolved by: {incident.fix_applied} (downtime: {incident.downtime_min} min)"`
   - `f"Likely replacement part: {part.part_no} ({part.name})"`
5. `confidence = mean of top scores across the 3 retrievals`.

Return shape per section 6.

### Phase G — Frontend (target: 10 hours)

**`app/page.tsx`** — single page, responsive, two-column on desktop:
- Left: `<UploadZone>` (drag any file or browse — auto-detects PDF/image/audio), `<SearchBar>` (text input), `<FilterPanel>` (dropdowns: machine_type, severity, doc_type)
- Right: `<DiagnosePanel>` showing evidence cards + recommended steps + confidence bar + "Save as new incident" button (`<SaveIncidentModal>`)
- Top: `<OfflineBanner>` — polls `/api/health` every 5s. If `online: false` (always, since we never check internet), show green pill **"OFFLINE — Running locally"**. This is the demo's centerpiece visual.

Tailwind only, no component library beyond `lucide-react` icons. Match Linear/Vercel-class minimalism — dark mode default, mono font for IDs/codes, clean type scale.

**`lib/api.ts`** — typed wrapper around fetch. Base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

### Phase H — README + demo prep (NOT for Codex — owner does this)

Owner records the demo, writes the README, makes the architecture diagram. Codex's job ends at a working app.

---

## 6. API surface (final, locked)

```
GET  /api/health
  → { status: "ok", online: false, db: bool }

POST /api/ingest/manual       multipart: file (PDF), machine_type, model_no
POST /api/ingest/incident     json: { row: {...} }
POST /api/ingest/image        multipart: file, machine_type, fault_code?, severity?
POST /api/ingest/voice        multipart: file (WAV), machine_type
POST /api/ingest/part         json: { row: {...} }

POST /api/search/text         json: { query, filters? }
POST /api/search/image        multipart: file, filters? (json string)
POST /api/search/voice        multipart: file, filters?
POST /api/search/multimodal   multipart: text?, image?, audio?, filters?

POST /api/diagnose            multipart: query?, image?, voice?, filters?
  → {
      evidence: {
        manual_section: { source, page, snippet } | null,
        similar_incident: { id, fix_applied, downtime_min } | null,
        candidate_part: { part_no, name } | null
      },
      confidence: float,            // 0.0 – 1.0
      recommended_steps: string[]
    }

POST /api/incident/save       json: { full incident row }
  → { id }
```

Filter object shape:
```ts
{
  doc_type?: "manual" | "incident" | "part" | "error_code" | "voice_note",
  machine_type?: string,
  model_no?: string,
  fault_code?: string,
  severity?: "low" | "medium" | "high" | "critical",
  part_no?: string
}
```

---

## 7. Collection schema (Actian VectorAI DB)

**Collection name**: `incidents`

**Named vectors**:
| Name | Model | Dims |
|---|---|---|
| `text_vec` | bge-small-en-v1.5 | 384 |
| `image_vec` | clip-ViT-B-32 | 512 |
| `audio_text_vec` | bge-small-en-v1.5 | 384 |

**Metadata fields** (used for filtered search and evidence display):
| Field | Type | Notes |
|---|---|---|
| `doc_type` | enum (5 values above) | Required, indexed |
| `machine_type` | string | Indexed |
| `model_no` | string \| null | Indexed |
| `fault_code` | string \| null | Indexed |
| `severity` | enum: low/medium/high/critical \| null | Indexed |
| `part_no` | string \| null | Indexed |
| `text_content` | string | Used by BM25 for hybrid fusion |
| `created_at` | timestamp | |
| `source_id` | string | filename or csv row id |
| `page` | int \| null | for manual chunks |
| `chunk_id` | int \| null | for manual chunks |
| `fix_applied` | string \| null | for incidents |
| `downtime_min` | int \| null | for incidents |
| `parts_used` | string \| null | for incidents (comma-sep part_nos) |

**Hybrid Fusion**: RRF over (`text_vec` ANN top-50) ∪ (BM25 on `text_content` top-50), final top-k by reciprocal rank sum.

---

## 8. Stopping rules

- After **Phase B**: STOP, run all tests, report progress.
- Before **Phase D**: STOP, wait for owner to paste Actian SDK examples.
- After **Phase F**: STOP, run end-to-end smoke test (`scripts/verify_offline.py`), report.
- After **Phase G**: STOP, owner takes over for demo recording / README / submission.

When stopping, report:
1. What was built (file paths)
2. Test results
3. What's blocked, if anything
4. Next phase to start

---

## 9. Definition of done (for Codex's scope)

A user can:
1. Drop the seed dataset into `data/raw/` and run `python backend/scripts/bulk_ingest.py` once.
2. Disconnect WiFi.
3. Open the Next.js frontend in a browser.
4. Drag a photo of a damaged motor part → see top-3 similar incidents + manual section + part recommendation + confidence score.
5. Type "E04 motor overload" → same, filtered by fault code.
6. Upload a voice note → transcript appears, retrieval runs against transcript.
7. Click "Save as new incident" → new record indexed live, retrievable in the next query.
8. The offline banner stays green throughout.

If all 8 work cold with no internet, the project is done.

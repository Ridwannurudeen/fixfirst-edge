# DoraHacks Submission — FixFirst Edge

Fill the form at https://dorahacks.io/hackathon/2097 with the content below.

## Owner-supplied fields before final submit

- Demo video URL (YouTube unlisted)
- Cover image / app screenshot
- Team member names and contact details

---

## Project name

FixFirst Edge

## Tagline (≤120 chars)

Offline multimodal maintenance copilot — search manuals, incidents, photos, and voice notes locally with Actian VectorAI DB.

## One-line description

An offline copilot that helps industrial technicians fix machines fast by retrieving evidence from manuals, prior incidents, parts catalogs, photos, and voice notes — all on a laptop, no internet required.

## Category / Track

Actian VectorAI DB Build Challenge — main track.

## Full description

Industrial downtime costs an estimated $50B per year. When a machine faults, the technician on the floor has minutes, not hours, to diagnose the problem. The information needed — equipment manuals, historical incidents, parts catalogs, even colleagues' voice notes — exists, but it is scattered across PDFs, spreadsheets, and shared drives, and the plant floor rarely has reliable internet.

FixFirst Edge is an offline multimodal maintenance copilot that fits on a laptop. A technician can search by error code, symptom text, a photo of the damaged part, or a spoken voice note. The system retrieves the most relevant evidence across all of these modalities in a single query and returns a templated, fully traceable fix recommendation — the relevant manual section, the closest prior incident, and the likely replacement part.

Every answer is auditable. No LLM is used in the diagnostic response; all recommendations are templated from retrieved rows in the vector store, each traceable back to a specific page of a specific manual or a specific prior incident.

## Why Actian VectorAI DB

Three Actian features make this workload possible in a single database, not a stitched-together pipeline:

1. **Named Vectors** — one `incidents` collection carries three embedding spaces side-by-side: `text_vec` (384d, bge-small-en-v1.5) for manual text, `image_vec` (512d, CLIP-ViT-B-32) for photos, and `audio_text_vec` (384d, bge-small over whisper transcripts) for voice notes. A single document can carry any subset of the three, and any modality can retrieve across the others.

2. **Filtered Search** — every query can be narrowed by `doc_type`, `machine_type`, `model_no`, `fault_code`, `severity`, or `part_no`. Filters hit Actian's keyword-indexed metadata, not post-filtered in Python. The diagnose endpoint uses this aggressively — it narrows part recommendations to only parts that fit the matched machine's model.

3. **Hybrid Fusion (RRF)** — text queries run a reciprocal rank fusion over dense ANN (top-50 on `text_vec`) and a second Actian-native retrieval lane that re-runs ANN with exact identifier filters extracted from the query (`fault_code`, `model_no`, `part_no`). During ingest, those identifiers are backfilled into indexed metadata fields for manuals, incidents, parts, and voice notes. This matters: tokens like `E04`, `CX-200`, and `OL-E04-R` are promoted through indexed metadata filters, while symptom phrases like "motor tripped on overload" are still dense-retrievable. RRF covers both.

## Why offline-only

Industrial sites have poor connectivity, strict data-egress rules, and technicians whose phones often have no signal near the machine. Cloud-backed AI assistants are also unauditable — an LLM-generated diagnostic can't be traced to a specific manual page. FixFirst Edge is 100% local. All embedding models (bge-small, CLIP, whisper tiny.en) run on CPU with no outbound requests. A green "OFFLINE — Running locally" banner on the UI is the demo's centerpiece.

## Tech stack

- **Database**: Actian VectorAI DB (Docker image `williamimoh/actian-vectorai-db:latest`, gRPC :50051)
- **Backend**: Python 3.11+ · FastAPI · pdfplumber · sentence-transformers · faster-whisper · pydantic
- **Frontend**: Next.js 14 (App Router) · TypeScript · Tailwind CSS · lucide-react
- **Embeddings**: all local, CPU, ~1.3 GB of cached weights on first run
- **Infra**: Docker Compose — Actian + backend container; frontend runs outside Docker for HMR

## Repository

https://github.com/Ridwannurudeen/fixfirst-edge

## Live landing page

https://edge.gudman.xyz

## Demo video

Owner to paste the final YouTube unlisted URL after recording.

## Architecture diagram

See [`ARCHITECTURE.md`](ARCHITECTURE.md) — Mermaid source plus request lifecycle and collection schema.

## Cover image

Owner to attach a screenshot of the app with the green OFFLINE pill and a filled Diagnose panel.

## Team

Owner to replace with final name, role, and contact details.

## What we built during the hackathon

- Full FastAPI backend with 11 endpoints across ingest / search / diagnose
- Three-vector Actian collection with `init_collection`, `upsert`, `search_text`, `search_image`, `search_audio`, `search_hybrid` (RRF), `health`
- Multimodal pipelines: text (bge-small), image (CLIP), audio (whisper tiny.en), PDF chunker, CSV loader
- Diagnose service that chains three filtered retrievals (manual → incident → part) and builds a templated, evidence-backed answer
- Next.js 14 frontend with UploadZone, SearchBar, FilterPanel, DiagnosePanel, OfflineBanner
- `verify_offline.py` — cold end-to-end smoke test
- Fixture CSV + demo asset generator (3 PDF manuals, 6 schematic images, 5 voice notes — fully regenerable from fixtures)
- 13 backend unit tests, all green

## How to run

See [README.md — Quickstart](README.md#quickstart). Five commands total: start Actian, install backend, seed, run backend+ingest, run frontend. Then disconnect WiFi and watch the banner stay green.

## License

MIT — see [LICENSE](LICENSE).

# Architecture

## Flow diagram (Mermaid — rendered on GitHub)

```mermaid
flowchart TB
  user[Technician]

  subgraph frontend["Next.js 14 — Frontend"]
    upload[UploadZone]
    search[SearchBar]
    filter[FilterPanel]
    diagnose[DiagnosePanel]
    banner[OfflineBanner]
  end

  subgraph backend["FastAPI — Backend"]
    routers["routers/
      ingest, search,
      diagnose, health"]
    services["services/
      ingest_service,
      search_service,
      diagnose_service"]
    pipelines["pipelines/
      text_embedder (bge-small 384d)
      image_embedder (CLIP 512d)
      audio_transcriber (whisper tiny.en)
      pdf_chunker, csv_loader"]
    dblayer["db.py
      init_collection,
      upsert,
      search_text/image/audio,
      search_hybrid (RRF)"]
  end

  actian[(Actian VectorAI DB
    :50051
    collection: incidents
    named vectors: text_vec, image_vec, audio_text_vec
    keyword filters: doc_type, machine_type, model_no,
                     fault_code, severity, part_no
    hybrid: RRF dense ANN + identifier-filtered ANN)]

  user --> frontend
  frontend -->|HTTP| routers
  routers --> services
  services --> pipelines
  services --> dblayer
  dblayer -->|gRPC| actian
```

## Request lifecycle — `/api/diagnose`

```mermaid
sequenceDiagram
  participant T as Technician
  participant UI as Next.js UI
  participant API as FastAPI
  participant S as diagnose_service
  participant E as embedders
  participant DB as Actian VectorAI DB

  T->>UI: query + optional image + optional voice
  UI->>API: POST /api/diagnose (multipart)
  API->>S: route

  alt has voice
    S->>E: transcribe(whisper)
    S->>DB: search_hybrid(transcript, audio_vec, filter)
  end
  alt has image
    S->>E: embed_image(CLIP)
    S->>DB: search_image(image_vec, filter)
  end

  S->>DB: search_hybrid(query, text_vec, filter:doc_type=manual)
  DB-->>S: top manual chunk
  S->>DB: search_hybrid(query, text_vec, filter:doc_type=incident)
  DB-->>S: top similar incident
  S->>DB: search_hybrid(query, text_vec, filter:doc_type=part, model_no)
  DB-->>S: candidate part

  S->>S: build templated recommended_steps
  S-->>API: evidence + steps + confidence
  API-->>UI: JSON
  UI-->>T: DiagnosePanel
```

## Collection schema

```
collection: incidents

  named vectors
  ────────────────────────────────────────────────
    text_vec         384   cosine   Dense text embedding
    image_vec        512   cosine   CLIP image embedding
    audio_text_vec   384   cosine   Dense embedding of whisper transcript

  keyword-indexed metadata
  ────────────────────────────────────────────────
    doc_type         keyword   manual | incident | part | error_code | voice_note
    machine_type     keyword
    model_no         keyword   provided or backfilled from text
    fault_code       keyword   provided or backfilled from text
    severity         keyword   low | medium | high | critical
    part_no          keyword   provided or backfilled from text
    source_id        keyword

  payload fields (not indexed)
  ────────────────────────────────────────────────
    text_content     text      returned as auditable snippet / evidence payload
    created_at       datetime
    page             integer
    chunk_id         integer
    fix_applied      text
    downtime_min     integer
    parts_used       text
    doc_id           text      human-readable id (the point id itself is uuid5(doc_id))
```

## Hybrid fusion detail

```
query: "E04 motor overload"

          ┌────────────────────────────────┐       ┌───────────────────────────────┐
          │ text_vec ANN top-50            │       │ identifier-filtered ANN top-50 │
          │  (bge-small embedding)         │       │  (fault/model/part exact)      │
          └────────────────┬───────────────┘       └──────────────┬────────────────┘
                           │                                      │
                           └──────────────────┬───────────────────┘
                                              ▼
                                    RRF merge (k=60)
                                   score = Σ 1/(60 + rank)
                                              │
                                              ▼
                                        top-k returned
```

Rare tokens like error codes (`E04`) and identifiers like `CX-200` or `OL-E04-R` are promoted through the identifier-filtered branch, while symptom phrases ("motor tripped on overload") are dense-retrievable. RRF covers both without scrolling payloads in Python.

---

## For the Excalidraw handoff

Use the Mermaid diagrams above as the source of truth. In Excalidraw:

1. Import the first mermaid block via "Mermaid to Excalidraw" (Excalidraw has this built-in).
2. Recolor to match slide template if you have one — otherwise the default is fine.
3. Export PNG at 2× for submission.

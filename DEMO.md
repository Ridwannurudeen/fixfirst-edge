# Demo Script — FixFirst Edge

**Target length**: 2:30 (under 3 min)
**Resolution**: 1920×1080, 30 fps, H.264 MP4
**Audio**: voiceover via built-in mic, no background music (demo is about the product, not vibes)
**Recording tool**: OBS Studio or Windows Game Bar
**Upload**: YouTube unlisted, link in DoraHacks submission

---

## Pre-recording checklist

- [ ] WiFi disconnected (airplane mode on laptop)
- [ ] Actian container running: `docker ps` shows `vectoraidb Up`
- [ ] Backend up: `curl http://localhost:8000/api/health` → `db:true`
- [ ] Frontend up: http://localhost:3000 loads, or http://localhost:3001 if port 3000 is already occupied
- [ ] `data/raw/` has real seed data ingested (`bulk_ingest.py` run once)
- [ ] Test image ready: `data/raw/images/schematic_01_conveyor_E04.png`
- [ ] Test voice note ready: `data/raw/voice/voice_01_conveyor_e04.wav`
- [ ] Browser in dark mode, 100% zoom, dev tools closed
- [ ] Close everything else — no Slack/email notifications

---

## Script

### [00:00 – 00:15] Cold open

**Visual**: camera on laptop showing the airplane icon in the taskbar → cut to the local app with the green "OFFLINE — Ready locally" pill.

**VO**:
> "This laptop has no internet. No cloud APIs. Everything you're about to see — text search, image search, voice transcription, vector retrieval — runs locally. This is FixFirst Edge."

### [00:15 – 00:35] The problem

**Visual**: split screen — a 400-page PDF manual on one side, a photo of a damaged conveyor part on the other.

**VO**:
> "Industrial technicians spend hours searching PDFs and spreadsheets for fixes to machines that are costing money every minute they're down. The information exists — it's just impossible to find in the moment. And plant floors rarely have good connectivity."

### [00:35 – 00:55] Text query

**Visual**: click the search bar, type `E04 motor overload on CX-200 thermal overload relay`, then run diagnosis.

**VO**:
> "Type an error code. FixFirst Edge runs a hybrid search — dense vector ANN over embeddings, plus a second Actian retrieval lane filtered by exact identifiers like fault codes and model numbers — fused with reciprocal rank fusion. That matters because 'E04' or 'CX-200' are identifiers dense alone can underweight."

**Visual highlight**: the Diagnose panel fills — manual section, similar incident, candidate part, evidence coverage, recommended steps.

### [00:55 – 01:20] Filtered search

**Visual**: open the severity filter → pick `critical`. Show the results narrow.

**VO**:
> "In the live UI, the tech can narrow by machine type or severity. Under the hood, the retrieval path still uses indexed model and fault-code metadata inside Actian — not post-filtering in Python. That's how you make a 200-document collection useful."

### [01:20 – 01:40] Image query

**Visual**: drag a photo of a damaged part into the upload zone.

**VO**:
> "Drop a photo. CLIP embeds it locally on the same machine. The result is a 512-dimensional vector searched against every image vector in the same collection — named vectors means one database, three embedding spaces."

**Visual highlight**: top-matching incident appears.

### [01:40 – 02:00] Voice query

**Visual**: drag a WAV file in. Show the transcript appearing in the right panel.

**VO**:
> "Upload a voice note. Faster-whisper transcribes locally — no audio leaves the machine. The transcript is embedded and searched against voice-note vectors, again in the same collection. That's the named-vectors pattern."

### [02:00 – 02:15] Save as new incident

**Visual**: click "Save as new incident". Confirmation toast. Immediately search for something related — show the newly-saved record appearing in results.

**VO**:
> "Every query the tech resolves becomes training data. Save as a new incident, it's indexed live — the next person searching for a similar symptom finds the fix."

### [02:15 – 02:30] Why Actian / close

**Visual**: full-screen the offline pill.

**VO**:
> "Three Actian features made this possible: named vectors for true multimodal in one collection, keyword-indexed filtered search, and hybrid RRF fusion. All on a laptop, all offline. Thanks for watching."

---

## Post-production

- Trim head/tail silence.
- Normalize audio to -14 LUFS.
- Add title card at t=0 ("FixFirst Edge — Offline Multimodal Maintenance Copilot") 1.5 s.
- Add end card at t=02:28 (GitHub URL) 2 s.
- Export: MP4, CRF 20, AAC 192 kbps audio.

---

## Cover image

- Screenshot of the app at resolution the DoraHacks submission form requires.
- Show the "OFFLINE — Running locally" pill, the Diagnose panel filled with a realistic query, and the evidence cards populated.
- Overlay the wordmark "FixFirst Edge" in the top-left.
- Export PNG.

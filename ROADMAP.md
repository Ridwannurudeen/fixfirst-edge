# FixFirst Edge — Roadmap

A multi-phase plan to transform FixFirst Edge from a hackathon entry into a viable product in the offline industrial maintenance AI category.

**Status**: draft · post-hackathon strategic plan
**Last updated**: 2026-04-23

---

## TL;DR

Ship a three-layer product: **OSS core** (acquisition), **self-hosted Commercial** (revenue), **specialized vertical** (moat). Target **pharma / medical first** — highest willingness-to-pay for compliance-grade offline AI, smallest number of competing incumbents. **Bootstrap through month 9** using Actian credits, hackathon prize money, and design-partner revenue. **Hire co-founder (sales / GTM) at month 6**, not before. **Decide at month 9** whether to raise, stay bootstrapped, or kill it.

Time to "category-visible": ~18 months. Time to "venture-scale" (if that path is chosen): 3–4 years.

---

## Phase map

| Phase | Timeframe | Goal | Exit criteria |
|---|---|---|---|
| **0. Hackathon close** | Apr 23 – May 7 2026 | Submit, gather feedback, decide | Go / No-Go commit |
| **1. Hardening** | May – Jun 2026 (8 wk) | Production-ready OSS | A stranger installs and uses it without help |
| **2. Design partners** | Jul – Sep 2026 (12 wk) | 3 pilots, real feedback | ≥ 1 signed commercial intent letter |
| **3. Commercial v1** | Oct – Dec 2026 (12 wk) | $100K ARR, 3 paying sites | 3 renewed contracts |
| **4. Product scale** | 2027 Q1 – Q2 | $500K ARR, 10+ sites | Churn < 5%, NPS > 40 |
| **5. Category move** | 2027 Q3 – 2028 | $2M ARR / acquisition / raise | Board decision |

---

## Phase 0 — Hackathon close (now → May 7 2026)

### Work
- Submit to Actian hackathon (Apr 25)
- Record demo video; post demo thread on X; cross-post LinkedIn
- Respond to judge feedback (if any)
- Write a 600-word "why I built this" post on X + LinkedIn — narrate the journey, drive the first ~50 GitHub stars

### Decision point
By **May 7**, evaluate:
- Is the signal real? (GitHub stars, inbound DMs, judge reaction)
- Did anyone from the Actian team / industrial-AI Twitter notice?
- Do I actually want to spend 18 months on this?

If no clear signal → **shelve**. Use as a portfolio piece. Move on.
If signal → **commit**, announce publicly, enter Phase 1.

### Output
A single Go / No-Go decision, and a public commitment post if Go.

---

## Phase 1 — Hardening (May – Jun 2026, 8 weeks)

**Goal**: make it so a stranger can install, ingest, and use the product without help.

### Engineering
- **Auth + multi-user**: email + password, session management. No SSO yet.
- **Non-Docker installer**: `.dmg` for macOS, `.exe` for Windows — a single-file bundle with the Python backend, Actian container, and Next.js build. Tauri or Electron shell.
- **Admin console**: upload docs via UI, not CLI. Ingestion progress bar. Corpus stats dashboard.
- **Observability**: structured logs, optional opt-in metrics endpoint (off by default).
- **Backup + restore**: `fixfirst export / import` CLI. Critical for compliance buyers.
- **Windows-native embed path**: fix the model cache stall on Windows.
- **Upgrade flow**: clean path from v0.1 to v0.2 without re-ingesting.
- **Security hardening**: CSRF, input validation at every boundary, dependency audit, secret scanning in CI.
- **Scale benchmarks**: 10K, 100K, 1M docs. Publish results.

### Docs + marketing
- Real `/docs`: Getting Started, Architecture, Ingestion, Operations, Security, FAQ
- Three case-study templates (empty, awaiting pilots)
- Pricing page (even if hypothetical — "commercial v1 coming Q4")
- Changelog page — builds trust

### Community
- Open GitHub Discussions with a pinned thread: "What are you trying to build? Tell me your corpus."
- Reply to every issue within 24 hours
- First 5–10 external contributors: cultivate personally

### Resources
- 8 weeks solo, ~$500/month infra. Prize money or personal funding.

### Risk
Solo-dev burnout. Mitigate: strict weekly scope, no weekend work, weekly journal.

### Exit criteria
One stranger (not a friend) installs, ingests, and queries their own docs without asking for help.

---

## Phase 2 — Design partners (Jul – Sep 2026, 12 weeks)

**Goal**: 3 pilot deployments in 3 verticals. Hard feedback. Early revenue signal.

### Recruit
- **1 pharma / GxP**: contract manufacturer (CDMO, 50–200 FTE). LinkedIn outreach to Heads of Manufacturing / OpEx.
- **1 defense contractor** (mid-size) or **1 utility** (water treatment, power co-op) — places where cloud is blocked.
- **1 manufacturing SMB** — broader market test, easier to reach. Local chambers of commerce, manufacturing associations.

### Commercial structure
Free 90-day pilot in exchange for:
- Logo + testimonial + case study
- Warm intro to 2 other buyers at pilot end
- Right-of-first-refusal on a paid contract

Signed pilot agreement (lawyer: ~$800 for a reusable template).

### Measure
- Time-to-first-query on their real corpus
- Weekly technician queries
- Specific moments where the product helped vs failed
- Feature gaps that matter vs don't

### Product work
- Build what pilots actually need, not what the roadmap said
- Kill features they don't use
- Fix exactly what's in their way

### Resources
~$2K/month (infra + legal + travel for 1–2 on-site visits per pilot). From prize + personal.

### Risk
**Zero pilots sign.** Most likely single failure point. Mitigation: 50+ cold conversations to land 3.

### Exit criteria
At least 1 pilot signs a written commercial intent: "yes, we'll pay $X/year for this after the pilot."

---

## Phase 3 — Commercial v1 (Oct – Dec 2026, 12 weeks)

**Goal**: first paid customers, $100K ARR, commercial viability proven.

### Product
- **Enterprise SKU**: SSO (SAML or OIDC via WorkOS), audit log export, admin RBAC, priority support channel, uptime contract
- **Pricing**: $2,500/site/month + $500 per concurrent user above baseline. Compliance-heavy verticals: $5K/site/month base.
- **Paid support**: $1K/month add-on for SLA
- **Legal templates**: MSA, DPA, security questionnaire responses ready

### Go-to-market
- **Launch site**: `fixfirst.com` or `fixfirst.ai` — product domain, not edge.gudman.xyz
- Product Hunt launch
- Hacker News "Show HN" timed with a technical deep-dive
- Two industrial / manufacturing podcast appearances (Manufacturing Tomorrow, Factory Floor)
- One paid conference (Automation Fair or IoT Solutions World Congress) — $8–15K booth

### Revenue target
- 3 paid customers at avg $33K/year = **$100K ARR**
- Each paying 3–6 months in advance (common in industrial B2B)

### Resources
$15–25K this phase (domain, legal, conference, paid ads). Revenue from pilots + personal.

### Hire (optional, month 6)
**Co-founder or first hire — GTM / sales background.** Ideal: someone who has sold to plant managers. Equity-heavy comp, minimal cash.

### Exit criteria
3 contracts signed, 3 months retention each. If customer #1 or #2 doesn't renew at the 3mo mark, pause and diagnose before adding more.

---

## Phase 4 — Product scale (Q1 – Q2 2027)

**Goal**: $500K ARR, 10+ sites, repeatable sales motion.

### Product
- **CMMS integrations**: webhooks / APIs for Limble, Fiix, MaintainX, IBM Maximo. You don't replace the CMMS — you plug in.
- **Mobile app**: tablet-optimized for plant-floor technicians. React Native or Tauri.
- **Predictive alerts**: nightly cron surfacing "these 3 pieces of equipment have rising incident frequency" — soft predictive layer, no full ML.
- **Multi-site management**: one pane of glass for chains with multiple plants.
- **Industry-specific ingest**: pharma (batch records), defense (FMECA docs), manufacturing (PLC logs).

### Team
- **2nd engineer** (full-stack, industrial domain bonus)
- **Part-time technical writer** — docs are a competitive moat in this category
- **Fractional CFO** (~$2K/month) for financial modeling + fundraise prep

### Metrics
- $500K ARR (10 customers × $50K avg)
- Gross margin > 80% (self-hosted — infra is minimal)
- Net retention > 110%

### Decision point (end of Phase 4)
Three paths diverge:

1. **Keep bootstrapping** — profitable, slow, sustainable. 15–20 customers in year 3, ~$1.5M ARR, small team.
2. **Raise $3–5M seed** — VC-backed sprint to category leadership. 100 customers in 3 years. Harder but bigger exit.
3. **Acquisition** — a Rockwell / Honeywell / Siemens may offer $15–30M at $500K ARR to kill or shelve. Accept only if the alternative path looks unlikely.

**Default recommendation: #1 unless a real strategic buyer (not tier-3 VC) shows up.** Reason: this category is unsexy enough that VCs will undervalue. Bootstrapped compounding works.

### Exit criteria
Clear answer to the three paths.

---

## Phase 5 — Category leadership (Q3 2027 – 2028+)

### If bootstrapped
- $2M ARR by end of 2028
- 25–35 customers, strong reference base
- Team of 5–6
- Start a second adjacent product (regulated-industry AI assistant?)
- Exit in year 5–7 at $15–30M (2–4× ARR, industrial software multiples)

### If VC-raised
- 100 customers, $5M+ ARR
- Team of 15–20
- Category-defining marketing spend
- Series A at month 18 ($10–15M)
- Exit path: strategic acquisition at $100M+ or IPO path (unlikely at this scale)

### Vertical expansion
Once the horizontal product is stable:
- **FixFirst Edge for Pharma** — SOC 2 + ISO 13485 + pre-built GxP manual templates
- **FixFirst Edge for Aviation** — MRO-specific, line maintenance integration
- **FixFirst Edge for Naval Engineering** — shipboard deployment, ruggedized hardware bundles

Each vertical: higher ACV, lower churn, different buyer, different sales motion.

---

## Cross-cutting: open source strategy

**Keep the core open source. Permanently. Non-negotiable.**

Reasons:
1. **Acquisition flywheel** — OSS is how you get the first 100 installs
2. **Trust signal** for compliance buyers — they can audit the code
3. **Community contributors** — free product improvement
4. **Moat** against proprietary competitors who will try to out-market you

### What's commercial
- SSO / SAML / advanced auth
- Multi-site management console
- CMMS integrations
- Priority support + SLA
- Compliance bundles (GxP templates, SOC 2 attestation)
- Mobile app

### Pattern
**Open Core.** GitLab, Mattermost, PostHog run this model successfully. Do not dual-license the core (Elastic / MongoDB lost trust doing that).

### Community investment
- **20% of engineering time on OSS, non-negotiable**
- Sponsor 1–2 top external contributors after year 1
- Speak at open-source-in-industry conferences (FOSDEM, OSSummit, All Things Open)

---

## Cross-cutting: business / legal

### Incorporate (Month 1 of Phase 1)
- **Delaware C-corp** if planning to fundraise, **LLC** if bootstrapping
- Cost: $500–$1,500 via Clerky / Stripe Atlas
- Provides: legal entity, bank account, contracting ability

### Banking
Mercury or Brex (avoid big banks — they'll ignore you at this stage).

### Accounting
Pilot.com at ~$350/month from month 6. Don't DIY past $50K revenue.

### Legal
Don't hire a firm initially. Use templates from Clerky + Mosaic + LawDepot in year 1. At $250K ARR, retain a real startup lawyer (Cooley, Wilson Sonsini) at ~$2K/month.

### IP
File one provisional patent on the RRF + identifier-filtered fusion approach early in Phase 1 ($150 USPTO + ~$2K lawyer = $2,150). Likely never enforced — defensive value + acquisition optics.

### Insurance
E&O + cyber liability by Phase 3 (first paying customer). Hiscox or Embroker, ~$3K/year.

### Trademarks
"FixFirst Edge" wordmark + logo in industrial / software classes. ~$500 TEAS filing.

---

## Cross-cutting: fundraise path (if chosen)

### Don't raise until you have
- 3 paid customers (proof it sells)
- 6+ months of retention data (proof it sticks)
- A clear "why now" narrative (post-ChatGPT industrial-AI window is the tailwind)
- Co-founder or first hire (VCs penalize solo founders)

### Right round structure
- **Seed: $3–5M @ $15–25M post-money**
- **Dilution: 20–25%**
- **Investors**: industrial-focused funds (Eclipse, IA Ventures deep-tech arm, Emergence Capital industrial) over generalist VCs. Avoid tier-3 funds — they drag reporting burden without value.
- **No SAFEs if avoidable** — priced rounds yield better investor quality.

### Wrong investors (say no if any show up)
- Anyone asking for board control pre-Series A
- Anyone who wants cloud-first "for scale reasons"
- Family offices with no industrial expertise
- Corporate VCs that would rather acquire than fund

---

## Risks — ranked by severity

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Can't land 3 pilots | High | Fatal | Outreach starts Phase 1 week 1; 50 cold DMs to land 3 |
| Incumbent ships offline feature | Medium | High | Move faster; vertical specialization |
| Actian VectorAI DB deprecated / license change | Low | High | Abstract the vector layer now — swap to Qdrant/Weaviate in 2 weeks if needed |
| Pilot customer data breach | Low | Fatal | Pen test at end of Phase 2 (~$8K); cyber insurance in Phase 3 |
| Solo burnout | High | Fatal | Co-founder by month 6; cap at 50h/week; weekly reflection |
| LLM competitors argue "hallucination is fine now" | Medium | Medium | Lean into audit trail + compliance as a moat |
| No one actually cares about offline | Low | Fatal | This is the core bet. If pilots reject it, pivot within Phase 2 |

---

## What to do *this week*

1. **Submit the hackathon** by Apr 25
2. **Record the demo video** — blocker for submission and landing
3. **Draft the 600-word "why I built this" post** — hold until submission is in
4. **Create an email list** — Mailchimp / Beehiiv free tier — capture any inbound interest
5. **Don't commit long-term until May 7.** Let signal come in. Resist premature roadmap lock-in.

---

## The honest sentence

> Most founders building a product like this would be 18 months and $500K in before they have what exists after this 10-day hackathon. The next 18 months aren't about building more — they're about finding the 30 buyers who actually feel the pain already modeled here.

That's the job.

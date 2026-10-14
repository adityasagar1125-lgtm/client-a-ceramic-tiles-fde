# Tessera — Shade-Transfer Engine for Digital Ceramic Printing
### Forward Deployed Engineer case study · Client A (ceramic tiles, UAE / India / Bangladesh)
*Status: proposal v1, before the next client call. All figures marked (A) are assumptions to be validated with the client, listed in Appendix B. Main body ≤ 6 pages; PRD and ledger in appendices.*

---

## 1. Problem understanding

**What they asked for:** a vision/video-analytics system that compares the master tile with the current production tile and tells QC what to change in the printer's input file, in 5–6 minutes instead of 6–7 hours.

**What they actually need.** Three things are different from the request.

| They said | What the evidence says | Consequence |
|---|---|---|
| "Vision / video analytics" | They already *measure* the difference (spectrophotometer: ΔL, Δa, Δb). Their words: "they still don't know how much to change the input file." | The gap is **not perception. It is the missing map from a measured colour error to an ink-channel change.** No camera is needed to close it. |
| "Minutes, not hours" | The 6–7 h is mostly print → dry → **fire** → cool → lab, repeated 6–7 variants at a time. A kiln cycle cannot be removed by software. | We can make the *decision* take minutes and cut the *rounds* from many to ~1. Realistic wall-clock to an approved file: **~1.5 h (one fire cycle + queue)**, not 6 min. We say so now. |
| "Compare master with current tile" | Their own comment: a 2021 reference "could be way off." Each fix is anchored to the *last run*, so error accumulates like a photocopy of a photocopy. Also: "99% match, let it go," and different people pick different edits. | Anchor to the **master, never to the last run**; make the answer repeatable across people. |

Other things the notes tell us:
- The pain occurs **at batch change only**. "Once the first sample is right, the whole batch is fine." So no continuous in-line system is needed, and we should not build one.
- Root-cause (kiln time, raw material) is explicitly out of scope for them ("not realistic"). We respect that but capture drift data as a by-product.
- They said gloss (Δgloss) matters. A printer's colour file mostly cannot change gloss. See §3.
- The 6 "primary colours" are, we assume, 6 ink channels (A).

**Stakeholders**

| Who | Wants | Fear / constraint |
|---|---|---|
| Procurement lead (buyer) | Clear price, low risk, fast visible result, hardware plan | Being sold "AI" with no proof |
| Head of IT & OT | Plant-safe deployment, no printer/kiln tampering, hardware/OEM answers | Network exposure, unsupported hardware |
| Plant QC / colour technicians (daily users, *not on the call*) | Fewer fired rounds, an answer they can defend | Being second-guessed or replaced; losing control of the file |
| Print/design team (owns the Photoshop files) | Pattern integrity preserved | A tool that damages vein/texture detail |
| Line / plant managers | Fewer m² in the wrong shade | Line stops for experiments |
| Sales / key accounts | Same shade in every shipment across 190 countries | Claims and returns |

**As-is process (as we understand it)**
`Production target set → printer loads reference image (last run's file) → 1 sample printed → fired → lab check (ΔLab by spectro, plus eye) → [pass: run batch] / [fail: edit file in Photoshop by eye, 6–7 variants → print → fire → lab → repeat]`, while the line keeps running: ~5,000–10,000 m² in the wrong shade by the time the file is fixed.

---

## 2. What we don't know yet (ranked) and what we assume meanwhile

Ranked by how much the answer could change go/no-go or design.

| # | Question for next call | Why it matters | Assumption until answered |
|---|---|---|---|
| 1 | What is the pass tolerance? ΔE (which formula), per tile or per zone, plus gloss? | Defines "works" | CIEDE2000: mean ≤1.0, worst zone ≤1.5; ΔGloss ±3 GU @60° |
| 2 | Do records exist of **(edited file → measured Lab)** pairs, and for how long? | The training data. Without it, we start with a designed experiment. | Partial: 12–24 months in lab software/Excel; Photoshop files for some |
| 3 | What exactly goes into the printer: format, channels, RIP/ICC step, can we read per-pixel channel values? | Decides how we write the corrected file | 6 ink channels, TIFF into a RIP, no colour management in the loop |
| 4 | Where do the 6–7 hours go (print / dry / fire / queue / lab)? Kiln cycle time? Is the sample fired in the production kiln or a lab kiln? | Sets the achievable target (our 1.5 h figure) | ~50 min kiln cycle, shared production kiln; ~3 h of the 6.5 h is queue + kiln |
| 5 | How many SKUs, how many changeovers per month need shade correction, and what happens to off-shade tiles (scrap, downgrade, resell)? | Value case | 36 corrections/month across 3 plants; off-shade tile downgraded, $2/m² loss |
| 6 | Pattern type: flat colours, or veined/stone-look with dense detail? | Zone method vs. spatial method | Mostly ≤8 dominant colour zones |
| 7 | Does a given SKU run on one printer/line or many? Printer-to-printer differences? | Whether process state is per-line or per-plant | Any SKU can run on 2–3 lines |
| 8 | The master: one physical tile? Age? Was it ever measured and stored digitally? | The anchor | One physical master; no stored spectral data |
| 9 | Which instruments (model, aperture, geometry), and are they calibrated against a reference? | Measurement error can exceed tolerance | Handheld 8 mm aperture, annual calibration |
| 10 | Any logs: ink lot, kiln profile, humidity, head maintenance? | Drift signal (value-add) | Ink lot and kiln profile exist, not linked to SKU runs |
| 11 | Gloss: is there a glaze/clear channel the file controls? | Whether we can *correct* gloss or only *report* it | No: report only |
| 12 | Network / data residency, who signs off a changed file, shift patterns | Deployment | Offline on-site PC, QC supervisor signs off |

---

## 3. Solution

### Options considered
| Option | Verdict |
|---|---|
| A. In-line camera or hyperspectral closed loop on the line | **Rejected.** They told us it doesn't need to run continuously; the kiln sits between print and any view of the final shade; capex and OT-risk high. |
| B. Rule-of-thumb lookup ("brown lighter → +5% brown") | Rejected as the product. This is what QC does today; ink→colour is nonlinear and channels interact. |
| C. Black-box ML on history | Rejected as the *core*. Little, confounded data per SKU; extrapolates badly. Used only as a residual correction. |
| D. **Tessera: calibrated correction model + shared process-state estimation + uncertainty-aware experiment design, human-signed** | **Recommended.** |
| E. Root-cause model of kiln/raw-material drift | Deliberately not built (their own call). |

### Recommendation: Tessera
Individual techniques below are established in colour science and process control. The claim is not that each part is new. It is that this *combination*, applied to the changeover problem in digital ceramic printing, does something their current loop and a plain "compare two tiles" tool cannot.

**Key idea (hypothesis, to be validated in pilot) — treat the drift as a *process state*, not a per-SKU mystery.** If the brown ink is effectively 4% weaker today (new ink lot, head wear, kiln), *every* SKU that uses brown shifts — this is our working hypothesis; the pilot must verify that drift on the same printer's channels is genuinely shared across SKUs. Today each SKU is re-learned by hand. Tessera estimates a small shared state per line (one effective gain/offset per ink channel) from the measured tile, and applies it to *all* SKUs in the queue.

Five ideas merged into one pipeline:
1. **Spectro-anchored capture** — a few accurate spectro readings per colour zone (truth, sparse). Optionally, a calibrated flatbed/lightbox image of the whole tile (dense, approximate) can be fused so the camera is corrected by the spectro. The MVP starts with existing spectrophotometer only; whether additional imaging is needed will be determined in the feasibility study.
2. **Zone ↔ ink mapping straight from the print file** — we have the file, so we know each zone's ink mix. Segment the master into dominant colour zones in Lab; each zone gets its channel recipe. Six zones are assumed (A); real patterned tiles may require more zones, and spatial variation / zone coverage must be validated in Phase 0.
3. **Calibrated forward model** — the production build proposes a physics-informed spectral model (Neugebauer / Yule–Nielsen style) with a Bayesian (Gaussian-process) residual learned from plant history. These are *proposed future components*, not existing prototype capabilities. The current prototype uses a deliberately simplified channel-drift model to test the correction mechanism.
4. **Kalman-style process-state estimator** — every measurement, including each past correction in the archive, updates the shared per-channel state (hypothesis — shared drift must be validated per-plant in Phase 0), with a prior (drift is usually a few %).
5. **Uncertainty-aware experiment design** — the output is not just a file but a confidence. *Confident → print one confirmation tile.* *Uncertain → print 2–3 variants chosen to be maximally informative, not 6–7 blind guesses.*

Two supporting ideas:
- **Shade Passport** — each SKU gets a versioned record: master spectral map, every correction as a signed delta *from the master*, the final curves, who approved. It kills the "2021 reference" problem.
- **Metamerism check** — ΔE00 computed under D65, A and F11 from spectral data, because a tile that matches in the lab can mismatch in a customer's room.

**What the output looks like.** Per-channel monotone *tone curves* (not pixel edits), exported as (a) the corrected file in the printer's format and (b) a Photoshop curves file (.acv), so QC can open, inspect and tweak in the tool they already use. Plus a one-screen report: per-zone ΔE00 now → predicted after, confidence, and the max change per channel.

**Where a person signs off.** The QC supervisor approves every file before it touches the printer. Overrides are logged and become training data. Tessera never writes to the printer or kiln.

**What we would deliberately not build:** in-line cameras; kiln or printer control; a replacement RIP; root-cause AI; automatic gloss correction; a fully automatic "push to printer" button; a custom spectrophotometer.

**Gloss.** Report-only in the initial version: ΔGloss with a pass/fail flag, logged to the passport. We assume it cannot be corrected through the colour file (Q11). If a clear/glaze channel exists, a future version could treat it as a seventh channel in the model, but this is out of scope for the pilot.

**Hardware / OEM (Head of IT's question).** We are a software and data company. We do not sell hardware. The MVP requires no new measurement hardware beyond what the client already owns (spectrophotometer, gloss meter). An optional capture station per plant (lightbox + calibrated flatbed + a reference ceramic standard set + a small edge PC) may be recommended after the feasibility study, procured at cost through a local integrator in the UAE/India.

---

## 4. Solution engineering (end to end)

```
 Master tile ──► spectro (grid) + flatbed ──► Shade Passport (digital master, zones, spectral Lab)
 Current production sample (fired) ──► same capture ──► ΔLab/ΔE00 per zone, ΔGloss, metamerism
 Print file (6-ch) ──► zone ↔ channel recipe
 [Line state] ◄── Kalman estimator ◄── all measurements + sentinel wedge
 Inverse solver (min ΔE00 across zones, ink limits, ±15% max per channel, monotone curves)
 ──► corrected file + .acv + report + confidence ──► QC supervisor approve ──► printer
 ──► 1 confirmation tile (or 2–3 designed variants) ──► fire ──► capture ──► log, learn
```

**Inputs and data**
| Data | Source | How collected |
|---|---|---|
| Master spectral/Lab map per SKU | Master tile | 10–20 spectro points per zone + flatbed, once; stored in the Passport |
| Current sample Lab/gloss | Fired sample | Same protocol, ~5 min at the capture station |
| Print file channel values | Printer input file | Read by Tessera at changeover |
| History (file edit → Lab) | Lab software, Photoshop archive | One-off import in Phase 0; gaps filled by experiments |
| Sentinel wedge | Printed at ink-lot change/changeover | A small 6-channel step ladder strip on the confirmation tile; gives the process state in one fire |
| Context (ink lot, kiln profile) | Existing logs, if any | Optional; used only for drift analytics |

**Sentinel wedge.** Because the process state is shared across SKUs, one printed wedge per changeover can pre-correct the *next several SKUs in the queue* before they are even printed.

**Model and logic.** Prior forward model f(ink) → Lab; state estimate by regularised nonlinear least squares (drift prior ≈ 8%); inverse by Gauss-Newton on CIEDE2000 across zones, weighted by area and visual saliency; monotonic curve constraint; ink-total limit; uncertainty from the posterior. Per-SKU GP residual added once ≥3 points exist.

**Fit with existing tools and routine**
- Runs on one on-site PC, offline-capable (UAE/India/Bangladesh connectivity and data residency); optional sync to a central model for cross-plant learning. **Cross-plant deployment note:** a successful calibration at one plant does *not* automatically transfer to UAE, India or Bangladesh facilities. Each plant requires its own validation gate in Phase 3, because printers, inks, kilns and environmental conditions differ.
- The user does what they do today (print → fire → measure), but in 1 round rather than 6–7 variants. The new steps are: scan the sample, review the screen, press approve.
- Photoshop remains in the loop (.acv export). Existing instrument software exports are read as CSV.
- QC owns the decision. Operators, not engineers, are the primary users: one screen, a traffic-light, plain words.

**Prototype (synthetic, `tessera_prototype.py`).** This synthetic experiment tests whether a *simplified channel-drift model* can reduce median colour error under noisy measurements and model mismatch. It does **not** implement the advanced spectral model (Neugebauer / Yule–Nielsen + GP residual) described above — those are proposed for the production build. The metric is **ΔE76** (Euclidean Lab distance), *not* the CIEDE2000 proposed for production acceptance; thresholds are not interchangeable between the two formulae.

300 random trials: 6 colour zones, 6 inks, random per-channel drift (σ=8%), meter noise 0.3 per Lab axis, forward model deliberately 15% wrong.
- Start error ≈ **2.12 ΔE76** (median).
- After **one** correction: median **0.91 ΔE76**; after two: **0.80 ΔE76**.
- **Tail is heavy: p90 ≈ 2.5–3.0 ΔE76** and only **54–59%** of trials reached < 1.0 ΔE76.

**Interpretation.** The result is encouraging: one measurement is enough to cut the median error by more than half, even with a wrong model. But the remaining tail errors demonstrate why confidence gating and physical confirmation are required. This experiment does **not** establish real-world performance or prove a speed advantage over actual QC technicians. A reference trial-and-error loop was also simulated for internal development; it is not calibrated to client QC behaviour and is not cited as evidence.

---

## 5. Evaluation

**Baseline (measured in Phase 0, not assumed):** for 30+ historic or shadowed changeovers: rounds to pass; wall-clock to approved file; ΔE00 of the first sample; m² produced off-shade; **inter-operator spread** (same tile, different technicians' edits).

**Metrics and thresholds**
| Metric | Threshold to pass pilot |
|---|---|
| Prediction accuracy: |predicted − measured| ΔE00 on the confirmation tile | median ≤0.5, p90 ≤1.0 |
| First-confirmation pass rate | ≥ 70% (≥ 90% within 2 prints) |
| Time to approved file | median ≤ 90 min vs. baseline ~6.5 h |
| Off-shade m² per changeover | ≥ 60% reduction vs. baseline |
| Repeatability across operators | same tile → same recommended file within tolerance |
| Gauge R&R of the measurement | ≤ 30% of the tolerance band (else tolerance isn't measurable) |

**Test protocol**
1. **Backtest** (offline): leave-one-SKU-out on history; no plant time.
2. **Shadow mode** (≥3 weeks): QC runs the normal loop; Tessera recommends blind; we compare. Zero production risk.
3. **Live paired A/B**: alternate changeovers between current method and Tessera at one plant; ≥30 pairs; Wilcoxon signed-rank on time and off-shade m². Includes a pre-registered list of SKU families, including the hardest.

**Stop conditions.** Stop or re-scope if: (a) measurement repeatability makes the tolerance unmeasurable (gauge R&R > 30%) — then the fix is metrology, not AI; (b) backtest p90 error > 2.0 ΔE00 across ≥15 SKUs after the sentinel wedge is added; (c) first-pass rate < 40% after live pilot; (d) QC supervisors override > 50% of recommendations and don't trust the explanation.

---

## 6. Build plan and timeline (24 weeks)

| Phase | Weeks | Output | Gate / milestone | Depends on client |
|---|---|---|---|---|
| **0 Feasibility** | 1–2 | Site visit, baseline, instrument R&R, import history, fit model on the master + variant tiles they offered | **G0**: R&R OK + model signal visible → proceed | Site access, QC time, master + variants + the file edits that made them, history export |
| **1 Build + backtest** | 3–8 | Capture station, zone engine, estimator, solver, UI, backtest; shadow mode from wk 7 | **G1**: backtest meets thresholds | 10–20 SKUs of tiles, a named QC owner, a PC on the plant network |
| **2 Live pilot (plant 1)** | 9–14 | Paired A/B on ≥30 changeovers | **G2**: pilot metrics pass | Kiln/line slots for confirmation tiles |
| **3 Rollout (plants 2, 3)** | 15–24 | Install, calibrate, train, Shade Passport for all active SKUs | **G3**: each plant passes a 10-changeover check | Local champion per plant, integrator access |

Result visible to procurement: **week 2** (baseline + feasibility verdict), **week 8** (shadow-mode numbers), **week 14** (live A/B result).

---

## 7. Cost and value

**Team and effort (person-weeks, pw)**
| Phase | FDE | ML/colour eng. | Software eng. | Total |
|---|---|---|---|---|
| 0 (2 wk) | 2 | 2 | 0.5 | 4.5 |
| 1 (6 wk) | 6 | 6 | 3 | 15 |
| 2 (6 wk) | 6 | 3 | 3 | 12 |
| 3 (10 wk) | 5 | 5 | 5 | 15 |
| **Total** | | | | **46.5 pw** |

- Delivery cost (A): 46.5 pw × $4,500 loaded = **$209,250**; travel 4 trips × 2 people × $3,500 = **$28,000**. Total **$237,250**.
- Hardware (optional, pending feasibility outcome): up to 3 capture stations × $6,000 = **$18,000** (client-owned, at cost).

**Running cost per year (3 plants):** cloud sync/monitoring $400 × 12 = $4,800; support 0.2 pw/week × $4,500 × 52 = $46,800; reference-standard recalibration 3 × $2,000 = $6,000. **≈ $57,600.**

**Proposed price and payment (Option A — feasibility credit applied)**

The $30,000 feasibility fee is credited toward the build + pilot phase if the client proceeds past G0. This means the client's effective payment for Phases 1–2 is $150,000 − $30,000 = **$120,000 net new**, bringing the total build cost to **$250,000** (not $280,000).

| Item | Price | Credit / net | Payment |
|---|---|---|---|
| Phase 0 feasibility | $30,000 | — | 100% on start. If G0 fails, client stops here. |
| Phases 1–2 (build + pilot) | $150,000 | −$30,000 feasibility credit = **$120,000 net new** | 40% ($48,000) at G1, 60% ($72,000) at G2 |
| Phase 3 rollout | $50,000 per additional plant (×2) | — | $100,000, on each plant's G3 |
| Hardware (if needed) | ≤ $18,000 at cost | — | On order |
| Annual subscription + support (from first go-live) | $90,000 / year | — | Quarterly |

**Total build spend (with credit): $250,000.** Total year-1 spend including hardware and support: $250,000 + $18,000 + $90,000 = **$358,000.**

Build price $250,000 vs. delivery cost $237,250 → ~5% margin on build, deliberately thin; the recurring $90k vs. $57.6k running cost is where we earn, and only if the client keeps using it.

**Forecast value to the client (all figures are assumptions, not guarantees)**

⚠ *The ROI below is a forecast based on assumed values. It becomes valid only if (a) approval-time reduction proportionally reduces off-shade production, and (b) $2/m² reflects actual economic loss. Both must be confirmed with the client in Phase 0.*

- Off-shade m² per correction: 5,000 (low end of their 5,000–10,000) (A).
- Time cut: 6.5 h → 1.5 h → exposure falls **1 − 1.5/6.5 ≈ 77%** → 3,846 m² saved per correction.
- Loss per off-shade m²: $2 (downgrade) (A) → **$7,692 per correction**.
- Corrections: 36/month (A) → 432/year → $3.32M; haircut 40% for adoption/partial success → **≈ $1.99M / year**.
- **Conservative case:** 10 corrections/month (120/yr) × $7,692 × 60% = **≈ $554k / year**.
- Not counted: lab labour, variant tiles, kiln slots, fewer customer claims, less rework, drift analytics.
- Year-1 client spend: **$358,000** (with feasibility credit). Base-case forecast ≈ 5.6× return; payback ≈ 2.2 months of steady-state saving. Conservative forecast ≈ 1.5×, payback ≈ 7.8 months.

**Phase 0 commitment: validate** actual loss per m², monthly changeover count, and off-shade disposition to turn these forecasts into defensible figures.

---

## 8. Risks

| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| Measurement noise exceeds tolerance (small-aperture spectro on patterned tile) | M / H | Phase-0 gauge R&R; multi-point averaging; flatbed fusion; stop condition (a) |
| Ink→colour is less "shared" than we assume (drift is SKU-specific) | M / H | Per-SKU GP residual; designed-variant fallback; backtest gate G1 |
| Kiln time dominates; users expect "5 minutes" | H / M | State 1.5 h target now; show decision-time of minutes; one fire is physical |
| QC distrust / shadow IT workarounds | M / H | QC co-design, explanations per channel, override logging, .acv export |
| Little or no historical data | M / M | Designed experiments from Phase 0; sentinel wedge generates data every changeover |
| Printer file/RIP can't be edited as assumed | L-M / H | Q3 on next call; fall back to a RIP-side curve file |
| Gloss can't be controlled | H / L | Reported only; flagged early |
| Metamerism or lighting differences across plants | M / M | Spectral data; D65/A/F11 checks; cross-plant reference standards |
| Master tile ages / damaged | L / H | Store digital master; periodic re-measure; reference standard |
| Hardware/site logistics across 3 countries | M / M | Local integrator; plant champion; phased rollout |

---

## Appendix A — Product requirements (PRD)

**Users:** QC technician (runs capture, reviews), QC supervisor (approves), print/design lead (inspects curves), plant manager (dashboard), IT/OT (admin).

**Functional requirements**
| ID | Requirement | Priority |
|---|---|---|
| F1 | Register a SKU with a master: spectro grid + image → zones + Shade Passport | P0 |
| F2 | Capture a sample; compute per-zone ΔL/Δa/Δb, ΔE00, ΔGloss; metamerism under 3 illuminants | P0 |
| F3 | Read the print file's channel values; map zones ↔ recipes | P0 |
| F4 | Estimate line process state; update from every measurement and wedge | P0 |
| F5 | Solve and export corrected per-channel curves (file in printer format + .acv) | P0 |
| F6 | Show confidence; if low, propose 2–3 designed variants | P0 |
| F7 | Approval workflow, audit log, override reason | P0 |
| F8 | Import history from lab exports/Photoshop archive | P1 |
| F9 | Sentinel-wedge generation and cross-SKU pre-correction | P1 |
| F10 | Drift dashboard (channel drift vs. ink lot/kiln log) | P2 |

**Non-functional:** offline operation; < 5 min compute from capture to proposal; no write access to the printer/kiln; local data residency; full versioned audit trail; ≥ 2 years of Passport retention; English UI (Arabic/Bengali labels later).

**Out of scope:** see §3.

## Appendix B — Assumptions ledger
(A) = assumed until the next call. Values: tolerance ΔE00 ≤1.0 mean / ≤1.5 worst zone; ΔGloss ±3 GU; 6 ink channels; TIFF + RIP; ~50 min kiln cycle, ~6.5 h baseline split ~3 h queue/kiln; 36 corrections/month; $2/m² off-shade loss; $4,500/pw loaded; hardware $6k/plant; pilot plant = the UAE site (client suggested a visit there).

## Appendix C — Decisions made where the notes were unclear
1. Interpreted "primary colours" as ink channels, not CMY colour space.
2. Chose the UAE site for the pilot because the client proposed a visit there.
3. Took "5,000–10,000 m²" at the low end because the recording is unclear.
4. Did not promise 5–6 minutes wall-clock; promised minutes for the decision and ~1.5 h to a confirmed shade.
5. Treated gloss as report-only.
6. Used CIEDE2000 (not ΔE76) as the production metric, ΔE76 only in the prototype.

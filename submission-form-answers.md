# Client A — FDE Submission Form Answers

## Question 1
**In two sentences: what is the client's real problem, and how is it different from what they asked for?**

The client asked for a computer-vision analytics system to compare tiles and tell operators what to adjust in 5–6 minutes. Their real problem is an **inverse-mapping gap, not a perception gap**: their lab already measures colour error precisely with spectrophotometers, but lacks a calibrated model to map measured ΔLab errors into printer ink-channel curves, while physical firing cycles make a 6-minute turnaround physically impossible.

---

## Question 2
**Who are the people in this deal, and what does each of them need to hear from you?**

* **Procurement Lead (Buyer):** Needs commercial transparency, capped initial risk ($30,000 feasibility credited against build), a visible go/no-go gate at Week 2, and realistic payback within months rather than vague AI promises.
* **Head of IT & OT:** Needs operational safety assurance — Tessera is an offline, on-premise application requiring zero write-access or network tampering with digital printers or production kilns.
* **Plant QC & Colour Technicians (Daily Operators):** Need to hear that the software assists rather than replaces them: it eliminates frustrating 6–7 trial rounds, exports standard Photoshop `.acv` curves they can inspect and tweak, and leaves final approval in supervisor hands.
* **Print & Design Team:** Needs assurance that tone curves preserve delicate stone/vein pattern textures without clipping channels or distorting master file integrity.
* **Plant & Line Managers:** Need confirmation that the software targets batch changeover bottlenecks to eliminate ~77% of off-shade tile production without disrupting continuous kiln schedules.

---

## Question 3
**The five questions you would ask on the next call, ranked. For each one: why it matters, and what you assumed while you wait for the answer.**

1. **What is the formal pass tolerance across the tile (which ΔE formula, mean/peak per zone, and gloss limits)?**
   * *Why it matters:* Dictates the mathematical objective function of our inverse solver and defines contractual pilot success.
   * *Assumed meanwhile:* CIEDE2000 with mean ≤ 1.0, worst zone ≤ 1.5, and gloss within ±3 GU at 60°.
2. **Do historical records exist pairing modified print files with resulting lab spectrophotometer readings?**
   * *Why it matters:* Determines whether Phase 1 begins by training on plant history or requires running designed calibration test tiles.
   * *Assumed meanwhile:* Partial history (12–24 months in lab spreadsheets and Photoshop archives) supplemented by designed sentinel wedges.
3. **What is the exact printer workflow, input file format, and RIP/ICC colour configuration?**
   * *Why it matters:* Determines how Tessera outputs curves (TIFF channel curves vs. external `.acv` profiles) without breaking the RIP pipeline.
   * *Assumed meanwhile:* 6-channel TIFF images fed into an OEM RIP with no automated colour management in the loop.
4. **What is the exact time breakdown of the 6.5-hour changeover (print, dry, kiln cycle, cooling, measurement)?**
   * *Why it matters:* Establishes the physical floor for wall-clock file approval and proves software decision time vs. physical kiln time.
   * *Assumed meanwhile:* ~50-minute kiln cycle plus queue/cooling times; ~1.5 hours achievable for a single-round confirmed file.
5. **How many batch changeovers require shade correction per month, and what is the actual financial loss per off-shade square metre?**
   * *Why it matters:* Turns our ROI forecast into an economically verified business case.
   * *Assumed meanwhile:* 36 corrections/month across 3 plants; off-shade tiles downgraded at an economic loss of $2/m².

---

## Question 4
**Which options did you consider, and why did you pick the one you did? What did you rule out, and why?**

* **Considered & Picked:** **Tessera (Hybrid Physics Prior + Channel-State Estimation + Uncertainty-Aware Confirmation).** We chose this because ceramic printing combines strong physical ink non-linearities with low-sample operational data. A calibrated channel-gain model regularized with plant priors converges reliably in 1–2 prints under noise.
* **Ruled Out:**
  1. *In-line cameras / video analytics:* Ruled out because the client does not need continuous inspection, cameras cannot see through the firing kiln, and optical sensors require continuous recalibration in harsh factory dust.
  2. *Heuristic rule-of-thumb lookup tables:* Ruled out because ink-to-colour transfer on fired ceramic glazes is highly non-linear with significant multi-channel interactions.
  3. *Pure black-box deep learning:* Ruled out due to extreme data sparsity per SKU and poor out-of-distribution extrapolation.
  4. *Kiln/raw-material root-cause modeling:* Explicitly ruled out at the client's direction as impractical and cost-prohibitive.

---

## Question 5
**How will the client know the pilot worked? Metric, baseline, threshold, how many runs, who measures, and what result would make you stop.**

* **Primary Metric:** CIEDE2000 colour difference between the fired confirmation tile and digital master.
* **Baseline (Phase 0):** Measured across ≥30 historical changeovers: ~6.5 hours turnaround, ~5,000 m² off-shade production, and multiple manual Photoshop iterations.
* **Pilot Thresholds:**
  * First-confirmation pass rate ≥ 70% (≥ 90% within 2 prints).
  * Median wall-clock approval time ≤ 90 minutes.
  * Off-shade square metres reduced by ≥ 60%.
  * Model prediction accuracy: $| \text{predicted} - \text{measured} | \le 0.5$ CIEDE2000 median, $\le 1.0$ p90.
* **Test Protocol & Evaluator:** Paired A/B testing on ≥30 live changeovers at the UAE plant, alternating between Tessera and standard manual QC, evaluated jointly by Plant QC and our FDE.
* **Stop Conditions:** Stop or re-scope if (a) measurement Gauge R&R exceeds 30% of tolerance, (b) live first-print pass rate is < 40%, or (c) QC supervisors override > 50% of software recommendations.

---

## Question 6
**What does this cost the client, and what does it cost us to deliver? Show the arithmetic and name the pricing structure. What value does the client get, in their money?**

* **Client Pricing (Option A — Feasibility Credited):**
  * Phase 0 (Feasibility): $30,000 (100% credited toward build upon proceeding past Gate 0).
  * Phases 1–2 (Build & Pilot): $150,000 gross − $30,000 credit = **$120,000 net new** (40% at G1, 60% at G2).
  * Phase 3 (Rollout to 2 plants): $100,000 ($50,000/plant).
  * Hardware (optional capture stations): Up to $18,000 at cost.
  * Annual Support/Subscription: $90,000/year.
  * **Total Build Cost: $250,000.** **Year-1 Total Spend: $358,000.**
* **Our Delivery Cost:** 46.5 person-weeks @ $4,500 loaded rate ($209,250) + 4 on-site travel trips ($28,000) = **$237,250**, giving a deliberate ~5% build margin with sustainable recurring SaaS margin ($90k vs. $57.6k maintenance).
* **Client Value Arithmetic (Forecast):** Cutting turnaround from 6.5 h to 1.5 h reduces off-shade exposure by ~77% ($3,846\text{ m}^2 \times \$2 = \$7,692$ saved per correction). At 36 corrections/month (40% haircut), gross annual benefit is **~$1.99M/year** (~5.6× year-1 ROI, 2.2 months payback). Even in a conservative 10-correction case, annual benefit is **~$554k/year** (7.8 months payback).

---

## Question 7
**Timeline. What is the first result the client sees, and when? Which steps depend on the client rather than on us?**

* **Timeline (24 Weeks Total):**
  * Phase 0 (Weeks 1–2): Feasibility & Metrology Audit.
  * Phase 1 (Weeks 3–8): Model Build, Sentinel Engine & Shadow Mode.
  * Phase 2 (Weeks 9–14): Live Paired A/B Pilot at UAE Plant.
  * Phase 3 (Weeks 15–24): Rollout & Calibration across Plants 2 & 3.
* **First Visible Result:** **End of Week 2** (Gate 0 report containing instrument Gauge R&R validation, baseline metrics, and feasibility verdict). Shadow-mode accuracy results visible at **Week 8**.
* **Client-Dependent Steps:**
  1. Week 1: Plant access, QC technician shadowing, and export of historical run logs.
  2. Week 3: Provisioning of dedicated on-site edge PC and named QC lead.
  3. Week 9–14: Kiln slots and production line access for confirmation test tiles during live A/B trials.

---

## Question 8
**Where did you push back on the client, narrow their ask, or tell them not to do something?**

1. **Pushed back on 5–6 minute wall-clock expectation:** Clarified that physical tile firing in a ceramic kiln takes ~50 minutes; software solves the computation in minutes, reducing total turnaround to ~1.5 hours (1 firing cycle vs. 6–7 cycles).
2. **Rejected in-line cameras and continuous monitoring:** Advised against expensive overhead computer vision, as shade drift occurs strictly at batch changeovers.
3. **Pushed back on gloss correction:** Clarified that ink-channel curves cannot compensate for glaze and kiln-induced gloss shifts; gloss is kept strictly as report-only.
4. **Refused automated printer integration:** Refused closed-loop automatic file writes to printers or kilns; mandated QC supervisor sign-off and `.acv` curve inspection.
5. **Rejected anchoring to the last run:** Stopped their practice of matching against previous batch files (which creates cumulative drift) and enforced anchoring strictly to the original master tile.

---

## Question 9
**What is most likely to go wrong with your plan, and what in these notes did you not trust?**

* **Most Likely to Go Wrong:**
  1. *Measurement Repeatability on Textured Tiles:* Small-aperture spectrophotometers on textured, non-uniform stone designs may exhibit noise that exceeds the pass tolerance band. (Mitigated by multi-point averaging and early Gauge R&R stop condition).
  2. *Non-Shared Channel Drift:* The assumption that channel drift is uniform across different SKUs may break down if ink-head temperature or glaze interaction varies by coverage. (Mitigated by per-SKU Gaussian Process residuals and 2–3 variant fallback prints).
* **What in the Notes We Did Not Trust:**
  1. The "5–6 minute" promise (conflated software runtime with thermodynamic kiln reality).
  2. The claim that "vision analytics" was needed when spectrophotometric data already existed.
  3. The phrase "6 primary colours" (which represented physical ink channels, not CMYK/RGB primaries).
  4. The 5,000–10,000 m² off-shade estimate (we assumed the lowest bound of 5,000 m² and marked it as an unverified forecast).

---

## Question 10
**What did you use AI for? Which tools, where they helped, where they misled you, and what you threw away.**

* **Tools Used:** Large Language Models (Claude / Gemini) via IDE coding agent.
* **Where They Helped:** Structuring the comprehensive PRD framework, drafting the single-page executive procurement brief, rapidly generating synthetic data simulation fixtures (`tessera_prototype.py`), and verifying numerical cross-document consistency.
* **Where They Misled:**
  1. Early drafts generated inflated marketing claims (e.g., claiming the prototype proved superiority over human QC technicians, when the baseline was an uncalibrated synthetic loop).
  2. Conflated prototype ΔE76 Euclidean metrics with formal production CIEDE2000 standards.
  3. Created an arithmetic discrepancy by forgetting to credit the $30k feasibility fee toward the build total ($280k vs. $250k).
  4. Attempted to claim the prototype implemented the full physics-based Neugebauer/GP model, when it only used a simplified channel-drift approximation.
* **What We Threw Away:** We discarded all claims of proven real-world performance, stripped out uncalibrated human-comparison benchmarks, removed uncredited pricing numbers, and rewrote the technical sections to honestly frame the prototype as a synthetic mechanism test.

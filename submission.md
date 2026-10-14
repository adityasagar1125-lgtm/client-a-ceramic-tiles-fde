# Client A — Ceramic Tiles FDE Case Study

## Submission Contents

1. **Case Study:** [`case-study.md`](case-study.md) — Problem analysis, proposed solution, pilot plan, risks, timeline, and business value. Main body ≤ 6 pages; PRD and assumptions in appendices.
2. **Client Procurement Note:** [`note-to-procurement.md`](note-to-procurement.md) — Non-technical one-page summary of the proposed solution, costs, and pilot engagement.
3. **Optional Prototype:** [`tessera_prototype.py`](tessera_prototype.py) — A synthetic-data prototype demonstrating the proposed colour-correction approach on a simplified channel-drift model. It does **not** establish performance on real production tiles, does not implement the advanced spectral model described in the case study, and reports results in ΔE76 (not the CIEDE2000 metric proposed for production acceptance).
4. **Form Answers:** `submission-form-answers.pdf` — Answers to questions 1–10 in the submission form.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Feasibility fee ($30k) credited on proceeding | De-risks the client; total build cost is $250k (not $280k). |
| ROI labelled as "forecast," not "guarantee" | Underlying assumptions ($2/m² loss, 10–36 corrections/month) are unvalidated. Phase 0 will confirm. |
| Prototype claims labelled "synthetic" | Results prove a correction *mechanism*, not production performance. |
| Human comparison not cited | The simulated reference loop is not calibrated to real QC technician behaviour. |
| ΔE76 in prototype, CIEDE2000 in production | Thresholds are not interchangeable between the two colour-difference formulae. |
| Shared drift treated as hypothesis | Must be validated per-plant in Phase 0; not stated as fact. |
| Cross-plant deployment needs per-plant validation | Printers, inks, kilns and environments differ across UAE, India and Bangladesh. |
| Gloss is report-only | Cannot be corrected through the colour file; flagged as a known limitation. |
| Camera/flatbed optional in MVP | MVP starts with existing spectrophotometer; imaging need determined in feasibility. |

---

## Important Notes

- All cost, ROI, and performance estimates are assumptions to be validated with the client during Phase 0 (feasibility).
- The prototype uses synthetic data and a simplified model; it is not production-ready.
- Recommendations require QC review and human approval before use — Tessera never writes to the printer or kiln.
- The advanced spectral model (Neugebauer / Yule–Nielsen + GP residual) is proposed for the production build, not implemented in the prototype.
- Confidential submission: do not publish publicly.

---

## AI Tool Disclosure

AI coding assistants were used during the preparation of this submission for:
- Drafting and structuring the case study and procurement note.
- Generating and debugging the synthetic prototype code.
- Reviewing numerical consistency across deliverables.
- Copyediting and formatting.

All technical claims, architecture decisions, pricing, and risk assessments were reviewed and validated by the submitting engineer. The AI tools did not have access to client production data.

---

## Submission Readiness Checklist

- [x] Case study: maximum 6 main pages, appendices separate
- [x] Prototype claims accurately labelled as synthetic (ΔE76, not CIEDE2000)
- [x] Pricing, credit terms and ROI consistent across both documents ($250k build, $358k year-1)
- [x] Evaluation distinguishes ΔE76 prototype results from CIEDE2000 production targets
- [x] Assumptions clearly marked (A) and no invented client facts
- [x] Procurement note is one page and non-technical
- [x] AI-tool disclosure included above
- [ ] All deliverables uploaded before the deadline

---

## Private Repository

GitHub URL: `[Add your private repository URL here after creating the repo]`

*Upload all four files to the repository root. Ensure the repo is set to Private.*

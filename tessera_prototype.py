"""
Tessera prototype — SYNTHETIC DATA ONLY

Purpose
-------
This script tests a single hypothesis on simulated data:

    If drift in a digital ceramic print line is mostly a shared per-ink-channel
    gain change, can ONE measurement of ~6 colour zones estimate the drift and
    produce a corrected file — even when the forward model is deliberately 15 %
    wrong?

What it does NOT establish
--------------------------
- Real-world performance on production tiles.
- A speed or quality advantage over actual QC technicians (no calibrated
  human-performance baseline is available).
- Behaviour of the advanced spectral (Neugebauer / Yule–Nielsen) model
  proposed in the case study; the model here is a simplified channel-drift
  model only.

Metric: dE76 (Euclidean distance in CIE L*a*b*).  The case study proposes
CIEDE2000 for production acceptance.  Results here should NOT be compared
against CIEDE2000 thresholds.

Simulation parameters
---------------------
- 6 colour zones, 6 ink channels.
- Per-channel drift: sigma = 8 %.
- Measurement noise: 0.3 ΔE per Lab axis.
- Forward-model mismatch: 15 % random perturbation of model coefficients.
- 300 independent random trials.

Interpretation guidance
-----------------------
The remaining tail errors (p90 ~ 2.5–3.0 dE76; only 54–59 % of trials pass
< 1.0 dE76) demonstrate why the production design includes confidence gating,
a designed-variant fallback, and a mandatory human-approved confirmation print.
"""

import numpy as np
from scipy.optimize import least_squares

rng = np.random.default_rng(7)

# ---------- constants ----------
NZ, NC = 6, 6                     # colour zones, ink channels
L0 = np.array([92., 0., 4.])      # paper white (Lab)
M  = np.array([                    # ink absorption matrix (simplified)
    [55, 40, 50, 35, 45, 30],
    [ 6,-20, 25, 15,-10, 20],
    [-10, 30, -5, 35, 25,-15.]])
K  = np.array([2.5, 3.0, 2.2, 3.5, 2.8, 3.1])   # absorption steepness


def lab(e, M=M, K=K):
    """Simplified forward model: ink coverage → Lab."""
    e = np.atleast_2d(e)
    return L0 - (1 - np.exp(-K * e)) @ M.T


def dE76(a, b):
    """dE76 — Euclidean distance in Lab (NOT CIEDE2000)."""
    return np.linalg.norm(a - b, axis=-1)


# ---------- single trial ----------
def trial(noise=0.3, model_err=0.15):
    """Run one simulated changeover: Tessera correction + uncalibrated reference loop."""

    # Random zone ink mixes
    c = np.clip(
        rng.dirichlet(np.ones(NC) * 0.6, NZ) * rng.uniform(1.2, 2.0, (NZ, 1)),
        0, 0.95)

    # Unknown true process drift
    g_true = 1 + rng.normal(0, 0.08, NC)

    # Measured master (with meter noise)
    master = lab(c) + rng.normal(0, noise, (NZ, 3))

    # True process + meter noise
    def proc(ci):
        return lab(g_true * ci) + rng.normal(0, noise, (NZ, 3))

    # Deliberately WRONG model (15 % perturbation)
    Kb = K * (1 + rng.normal(0, model_err, NC))
    Mb = M * (1 + rng.normal(0, model_err, M.shape))
    def mod(e):
        return lab(e, Mb, Kb)

    # --- Tessera: estimate shared gains, then solve per-channel scale ---
    s_tot = np.ones(NC)
    tessera_errors = []

    for rnd in range(3):
        ci = c * s_tot
        meas = proc(ci)
        # Error vs TRUE master shade (no measurement noise in ground truth)
        tessera_errors.append(
            dE76(lab(g_true * ci), lab(c)).mean())

        # Step 1: estimate drift gains from measured tile
        gh = least_squares(
            lambda g: np.r_[
                (mod(g * ci) - meas).ravel(),
                (g - 1) * noise / 0.08],          # drift prior sigma = 8 %
            np.ones(NC), bounds=(0.5, 1.5)).x

        # Step 2: solve per-channel scale to match master
        s = least_squares(
            lambda s: np.r_[
                (mod(gh * s * ci) - master).ravel(),
                (s - 1) * noise / 0.08],
            np.ones(NC), bounds=(0.7, 1.3)).x

        s_tot = s_tot * s

    # --- Reference loop (uncalibrated, NOT a validated human baseline) ---
    # This loop simulates a naïve trial-and-error approach.  It is NOT
    # calibrated to real QC technician behaviour and must NOT be used
    # to claim "Tessera is faster/better than humans."
    ch = c.copy()
    ref_rounds = []
    for rnd in range(10):
        e0 = dE76(lab(g_true * ch), lab(c)).mean()
        if e0 < 1.0:
            break
        best = (1e9, ch)
        for v in range(7):
            cand = ch.copy()
            idx = rng.choice(NC, rng.integers(1, 3), replace=False)
            cand[:, idx] *= 1 + rng.choice([-0.05, 0.05], len(idx))
            seen = dE76(proc(cand), lab(c)).mean() + rng.normal(0, 1.0)
            best = min(best, (seen, cand), key=lambda t: t[0])
        ch = best[1]
        ref_rounds.append(1)

    return tessera_errors, len(ref_rounds)


# ---------- run all trials ----------
R = [trial() for _ in range(300)]
errors = np.array([x[0] for x in R])
ref = np.array([x[1] for x in R])

# ---------- report ----------
print("=" * 70)
print("TESSERA SYNTHETIC PROTOTYPE -- RESULTS (dE76, NOT CIEDE2000)")
print("=" * 70)
print()
print("NOTE: These results are from a SIMPLIFIED channel-drift model on")
print("SYNTHETIC data.  They do not establish real-world performance or")
print("prove a speed advantage over actual QC technicians.")
print()
print("Initial median colour error (before any correction):   %.2f dE76"
      % np.median(errors[:, 0]))
print()
for i in (1, 2):
    med = np.median(errors[:, i])
    p90 = np.percentile(errors[:, i], 90)
    pct = 100 * (errors[:, i] < 1.0).mean()
    print("After correction #%d:  median %.2f | p90 %.2f | "
          "pass (< 1.0 dE76) %.0f%%" % (i, med, p90, pct))

print()
print("Tail-error note: p90 ~ %.1f-%.1f dE76 and only %d-%d%% of trials"
      % (np.percentile(errors[:, 1], 90),
         np.percentile(errors[:, 2], 90),
         int(100 * (errors[:, 1] < 1.0).mean()),
         int(100 * (errors[:, 2] < 1.0).mean())))
print("pass < 1.0.  This confirms the need for confidence gating,")
print("designed-variant fallback, and mandatory confirmation prints.")
print()
print("-" * 70)
print("Reference loop (UNCALIBRATED -- not a human-performance baseline):")
print("  median rounds to converge = %.0f  |  never passed in 10 rounds: %.0f%%"
      % (np.median(ref), 100 * (ref >= 10).mean()))
print("  WARNING: Do not cite as evidence of speed advantage over QC technicians.")
print("-" * 70)

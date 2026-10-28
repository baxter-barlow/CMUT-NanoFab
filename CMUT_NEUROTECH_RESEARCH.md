---
course: "6.2540 — Nanotechnology: From Atoms to Systems (MIT EECS)"
artifact: cmut-neurotech-research
companion_to: REQUIREMENTS.md
prepared: 2026-10-26
method: "Multi-agent literature research with per-claim fact-checking, an analytic CMUT design-space model with an independent re-derivation, 4 competing project concepts scored by 3 judges, and a final critic pass"
model_code: cmut_model/
---

# CMUT Arrays for Neurotech: State of the Art and 6.2540 Fit

*Prepared 2026-10-26 for a 6.2540 (Fall 2026) final-project group; revised the same day by a second-round refinement pass (v2, §6.12). Readers: the group, course staff and future AI agents. Bracketed numbers point to §10. Requirement IDs (C1–C5, D1–D6) refer to [REQUIREMENTS.md](REQUIREMENTS.md).*

*Every cited fact passed a separate fact-check against its source, sometimes with a correction. Claims the checkers could not support were removed. "Model" means the Python CMUT model in [cmut_model/](cmut_model/). It uses small-deflection plate theory, was validated against two published devices, and was re-derived independently (§8). Any number labelled "model" or "my estimate" is a calculation, not a literature measurement.*

*Model files (run with `python3`; numpy and scipy are required):*
- *[cmut_model/model/design_space.py](cmut_model/model/design_space.py)*: all design tables (output in `model/results/`)
- *[cmut_model/model/validate.py](cmut_model/model/validate.py)*: checks against published devices
- *[cmut_model/designs/nanogap_design.py](cmut_model/designs/nanogap_design.py)*: the recommended measurement ladder (§11 of `nanogap_results.txt` was added by a separate stress-readout check)
- *[cmut_model/report_checks/baseline.py](cmut_model/report_checks/baseline.py)*: the baseline die and cross-checks
- *[cmut_model/check/](cmut_model/check/)*: the independent physics re-derivation
- *[cmut_model/designs/round2_gap_matched_arrays.py](cmut_model/designs/round2_gap_matched_arrays.py)* and *[cmut_model/report_checks/free_capacitance.py](cmut_model/report_checks/free_capacitance.py)*: the round-2 (v2) numbers and the free-capacitance erratum (§6.12)

---

## 0. Bottom line

*Abbreviations:*
- *V_PI = pull-in voltage; g_eff = air gap + insulator thickness/ε_r*
- *MIM = metal-insulator-metal test capacitor*
- *PAN = phosphoric-acetic-nitric Al etchant; NMP = N-methyl-2-pyrrolidone; QCM = quartz-crystal thickness monitor*
- *SMU = source-measure unit; LDV = laser Doppler vibrometer*
- *MI = mechanical index; BBB = blood-brain barrier; NHP = non-human primate*
- *fUS = functional ultrasound imaging*
- *In §8, R1–R7 are the model's recommended designs ([recommended.json](cmut_model/model/results/recommended.json)), not the capillary ratio R.*

- **Does it fit? Yes, with conditions.**
  - A surface-micromachined CMUT cell is the Lecture-4/Pset-4 released electrostatic beam made circular: bottom electrode, insulator, sacrificial gap, metal membrane.
  - If the insulator is patterned by lift-off instead of RIE, every core step uses an allowed technique (C3): evaporation, sputtering, spin coating, MLA lithography and wet etching.
  - **C2 statement for the proposal (structure):** the 50–100 nm resist-defined gap is the sub-100 nm feature. It is evidenced by reflectance of witnesses run through the identical sequence and by SEM of cleaved unreleased witness stacks. The 50 nm SiO2 insulator on every die is a guaranteed backup in case the sub-100 nm resist films, which are still unverified, fail.
  - **Conditions:**
    1. Present it as a CMUT *building block* (vented cells plus small 1D arrays, characterized in air), not as a neural interface.
    2. Keep core electrical tests at 40 V or below. Confirm with staff whether the I-V instrument needs an interlocked fixture on the range used: on many source-measure units, anything above 20 V runs on a 200 V range, which triggers the 42 V safety rule [67].
    3. Confirm a short list of items with staff.
- **Recommended concept, "NanoGap CMUT":** circular Al-membrane CMUT cells and three gap-matched copies of an 8-element, 100 µm-pitch linear array (a = 7.75 / 9.5 / 11 µm, one matched to each gap, all on every die), built over 50, 75 and 100 nm spin-coated sacrificial gaps, plus a ~1 µm Lecture-4 baseline die. They are used to measure how pull-in voltage (∝ g_eff^1.5) and the wet-release stiction radius (∝ g^0.5) scale below 100 nm.
  - Why this matters for neurotech: small gaps are the standard route to lower CMUT bias. Commercial CMUT-on-CMOS uses a 200 nm gap at 1–10 MHz [40].
  - fUS brain imaging used a 15.6 MHz linear array in macaques [57] (not stated to be a CMUT). Human fUSI through acoustic windows runs at 5–6 MHz [89,90], below the ~8.3 MHz floor the model gives for sealed, wet-released sub-100 nm 1 µm-Al cells.
  - No CMUT-based fUS brain imaging has been published, so the project measures the scaling physics such a device would rely on. It does not demonstrate the device.
- **Round-2 refinement (§6.12):** of 14 distinct candidate improvements, three passed every check and were adopted. All three are drawing or wiring changes, with no added layer, session, chemical or approval item:
  - wide SiO2-free wells around the bare test cells;
  - guarded two-channel ramp C-V;
  - three gap-matched array copies. Expected usable arrays per 6-die run rise from ~2–3 to ~5–6 (model, heuristic stiction criterion). v1 already had at least one usable array in most runs.
  - Freeze-drying, a grounded top plane and nine other ideas were rejected. The gain is robustness, not a new capability. The round also corrected an error: ramp C-V reads the free capacitance, which rises ~+23% at 0.7 V_PI, not the +6% quoted earlier.
- **Why not a neurostimulator:**
  - Published CMUT neuromodulators fall into two groups. Most work at 0.18–0.8 MHz, with sub-µm to µm gaps, wafer-bonded Si plates and sealed cavities, driven at ~100 V DC, AC-only or in collapse mode [46,47,50,51]. The others work at 3.4–5 MHz on high-voltage pulser ASICs [48,49].
  - All of them rely on bonding, sealing or DRIE steps that are not on the course list.
  - Human transcranial stimulation runs mostly at 0.2–0.65 MHz (one tabulated study reaches 0.86 MHz) [75,76]. That is largely within the 200–800 kHz range covered by the ITRUSST safety consensus (MI ≤ 1.9) [77].
  - Apertures range from a 64 mm single element [83] to a head-sized 256-element helmet [81]. The 30 cm, 1024-element Exablate hemisphere [100] is an ablation system, not a stimulator.
  - With focusing, the per-element surface pressure is modest: ~0.01–0.17 MPa, depending on whether reported pressures are in situ (§4.1). So the obstacle is fabrication and drive, not physics.
  - In the model, wet-released, sealed sub-100 nm cells go no lower than ~8.3 MHz immersed for 1 µm Al (~4.6 MHz for 10 µm SU-8). The vented cells built here cannot be tested immersed at all (§8).
  - The project makes this trade-off its scientific story instead of hiding it.
- **Three biggest risks:**
  1. **Release.** Capillary stiction without critical-point drying, and incomplete resist removal from 50-100 nm slits.
  2. **Dielectric.** 50 nm of deposited SiO2 cannot survive touchdown (8.5 MV/cm), and bare nanogaps may arc or weld before pull-in.
  3. **Sacrificial film.** Diluted-AZ3312 films below 100 nm are unverified. A pinhole or particle larger than the gap shorts or pins a cell, and ±10% thickness error means ±15% in pull-in.
- **REQUIRES-STAFF-APPROVAL:**
  - heated NMP-based remover (release fallback)
  - critical-point dryer (run-2 option)
  - an enclosed, interlocked probe fixture for any bias above 42 V, and possibly for 21–40 V tests (instrument-dependent: the rule applies whenever the selected range can source >42 V [67])
  - LCR meter or impedance analyzer
  - a solvent-rated oven below 82 °C for IPA drying (optional; the default is room-temperature drying)
  - function generator, oscilloscope, high-voltage bias tee, fast photodiode or LDV (stretch)
  - Parylene-C CVD (stretch)
  - O2 descum (optional)
  - ellipsometer, profilometer or FIB cross-section (optional) [72]
- **Confirm only (already within course categories):** SiO2 sputter target or e-beam source; PGMEA resist thinner; 1 µm Al evaporation; oxidized-Si substrates; the I-V setup's maximum voltage, picoamp resolution, number of pA channels sharing a common LO and chuck terminal (for guarded ramp C-V); MLA overlay accuracy.
- **Tomorrow's one-page proposal (2026-10-27) must contain** (follow the density of Example 2):
  - names and date; title and a one-sentence aim
  - one cross-section figure: Cr/Au bottom electrode, 50 nm SiO2, 50-100 nm gap, 1 µm Al membrane with release hole
  - 3-4 measurable objectives (§6.1)
  - a step list mapping each of the 4 device MLA layers (plus one MIM-witness layer) to an allowed technique
  - materials and tools
  - a characterization paragraph naming the tool for each question
  - an explicit C2 statement
  - one line on risks and one line on requests to staff
  - 2-3 references: [15], [1], and [57] or [40]
  - submit it as one PDF per group on Gradescope
- **Logistics this week:**
  - One member signs the group up for the instructor meeting through the Canvas link. The guideline says "Wednesday October 29th", but 10-29 is a Thursday, so check the actual day on Canvas and have the §9 questions ready.
  - By 11-01 (D3), sign up with the assigned TA for lab hours and send staff the §6.8 list.
- **What the prototype will NOT show:** acoustic output, immersion, tissue, beamforming, or any neural effect. The link to neurotech is an extrapolation from the model (§6.11).

---

## 1. How a CMUT works

A CMUT cell is a parallel-plate capacitor whose top plate is a clamped membrane over a sealed or vented cavity [1].
- **Transmit:** a DC bias pulls the membrane toward the bottom electrode, and an AC drive on top makes it vibrate and radiate.
- **Receive:** incoming pressure modulates the capacitance, which produces a current at fixed bias.

The plate is light and compliant, so the fluid's radiation resistance damps it heavily. Immersed CMUTs are therefore broadband, with fractional bandwidth (FBW) around 100% [2,35].

**Key design equations.** g0 = air gap, a = cell radius, t = plate thickness, D = flexural rigidity.

| Quantity | Expression | Source |
|---|---|---|
| Effective gap | g_eff = g0 + Σ t_i/ε_r,i (every dielectric between the electrodes) | [1] |
| Capacitance (piston) | C = ε0A/(g_eff − x) | [1] |
| Flexural rigidity | D = Et³/[12(1−ν²)] | plate theory |
| Resonance, clamped plate, vacuum | f0 = (10.2158/2πa²)·√(D/ρt) | plate theory (constant reproduced numerically) |
| Fluid loading (Lamb) | f_fluid = f0/√(1+β), β = 0.6689·ρ_f·a/(ρt) | [14] |
| Spring softening | k_s = ε0AV²/(g_eff − x)³; f(V) ≈ f0·√(1 − k_s/k) | [1] |
| Pull-in, piston | x = g_eff/3; V_PI = √(8k·g_eff³/27ε0A) | [1] |
| Pull-in, clamped plate | mean deflection 0.154 g_eff (centre ≈ 0.46 g_eff); V_PI = √(0.148·k·g_eff³/ε0A) ≈ 5.33·√(D·g_eff³/ε0a⁴), with k = 192πD/a² | [2]; k from plate theory |
| 1-atm sag of a sealed cell | w_c = P_atm·a⁴/(64D) | plate theory |
| Transformer ratio, transmit bound | n = ε0AV/(g_eff − x)²; p/V ≤ ε0·V_DC/(g_eff − x)² | [1] |
| Coupling | k_T² = 1 − C_S/C_T, tends to 1 at collapse; parallel parasitic capacitance lowers it | [4] |
| Stroke-limited surface pressure | p ≲ FF·ρc·2πf·ū, with ū ≲ 0.5 × 0.154·g_eff | [30], model |
| Capillary collapse while drying | R = (2γ/g)/(64Dg/a⁴) ≲ 0.25 (heuristic); Tas critical length ∝ (Et³g²/γ)^¼ | [13], model |

**Do not use the piston formula for plates.** Compared with the plate model (confirmed by a 6-term Galerkin solution and an independent FE check), it reads 17% low with k = 64πD/a² and 41-43% high with k = 192πD/a². Reviews of analytical collapse-voltage models [10] and nonlinear lumped-element circuit models [9] give more refined alternatives.

Two scaling facts drive everything that follows:
- V_PI ∝ g_eff^1.5.
- Transmit stroke, and therefore maximum pressure, ∝ g_eff.

**Typical parameter ranges.**

| Parameter | Range | Examples |
|---|---|---|
| Gap | 40 nm – 1.75 µm | 40 ± 2 nm LOCOS [18]; 200 nm Butterfly [40]; 300 nm polyCMUT [15]; 0.43–1.75 µm neuro devices [50,47] |
| Plate thickness | 0.8–50 µm | 0.8 µm poly-Si [30]; 2.2 µm SiN [22]; 3 µm Si [47]; 5 µm Si [5,40]; 50 µm Si [50] |
| Cell radius | ~10–410 µm | 22 µm [30]; 50 µm [15]; 90 µm [47]; 410 µm [50] |
| Immersed centre frequency | 0.18–15 MHz (devices cited here) | 183 kHz [46]; 1–12 MHz [42]; 15 MHz IVUS [39] |
| DC bias | ~10–200 V | 10 V [15]; 100 V [47,51]; 172 V [52] |
| Field in the gap | ~10⁸ V/m | [1,12] |
| FBW in liquid | 80–135% | [35,36,15,30] |
| k_T² | ~0.3 typical; 0.85–0.95 best | [4,5] |
| Fill factor | ~50% to >90% | [3] |
| Transmit sensitivity | 7–65 kPa/V | [30,7,5] |
| Receive sensitivity | 623–938 µV/kPa (best single-membrane) | [5] |
| Q in air | ~2–40 | [70,15] |

---

## 2. State of the art in CMUT design (2019–2026)

### 2.1 Operating modes

| Mode | Principle | Representative numbers | Cost |
|---|---|---|---|
| Conventional | Bias at ~0.8–0.9 V_PI, AC drive on top | 12.7 kPa/V and 111% FBW at 10 MHz [7]; multi-membrane devices typically reach only k_T² ≈ 0.3 [5] | Output capped by the gap |
| Collapse | Plate biased into contact with the insulator, driven between snap-back and collapse | 26.4 kPa/V; 1.19 MPa max vs 0.44 MPa conventional [7]; 3.2×10⁹ cycles without significant degradation (thermal oxide) [7]; Philips CM5 at 100 V used for rat BBB opening [51] | Harmonics, charging [6,7] |
| Deep collapse | Large pulses applied to a collapsed plate | 3.5 MPa pp at 6.8 MHz, 106% FBW (160 V pulse on a device that collapses at 35 V) [8] | Stress on the insulator |
| Pre-charged | Trapped charge replaces the external bias | Al2O3 trap layer ~0.02 C/m², 8.8 kPa/V, >2.5 years at 37 °C in accelerated life tests [16]; SU-8 charging gave 8.9–30 V built-in bias [15] | Long-term charge stability |
| AC-only, half-frequency | Drive at f/2; the force ∝ V² lands at f | ~1.8 MPa at the surface, 125 V peak, no DC [17]; 190 kPa PNP at the surface from a 340 kHz, 130–137 V-peak AC-only drive, so output at ~680 kHz on an 800 kHz-centre element, with the drive close to its 131 V FEM collapse voltage [50] | Needs a large AC swing |

**Charging is what limits reliability.**
- Slow traps in the insulator drift the operating point. Patterning the insulator into posts covering 1.2% of the cavity removed a ~35 V shift in the capacitance-voltage (C-V) curve [3].
- Electrode-post designs showed no significant charging after 5×10⁵ collapse cycles. Breakdown at bond pads and at particles remains [5].
- Wong et al. attributed output below their simulation to oxide charging, and their array tests ended when oxide defects broke down [52].

### 2.2 Fabrication routes

| Route | Gap set by | Peak temperature | Gap control | Strength | Weakness | Refs |
|---|---|---|---|---|---|---|
| Classic sacrificial release (LPCVD SiN / poly-Si) | Sacrificial film | ~785 °C | CVD thickness | Simple | Stiction. Poly-Si at −400 to −500 MPa breaks membranes larger than ~100 µm. LPCVD sealing leaves only ~⅓ of the height under the etch channels | [3] |
| Low-temperature sacrificial release (Cu, Cr, Ni, polymer) | Evaporated metal or spun polymer | 150–250 °C | 10–15% (evaporated Cr [23]) | Works after CMOS and on flexible substrates | Wet-release stiction, film stress, weaker dielectrics | [22,23,25,15] |
| SOI fusion bonding | Thermal oxide | ~1100 °C | 0.64% on-wafer | Single-crystal plate; k_T² up to 0.953 | High temperature, CMP and DRIE | [3,5] |
| LOCOS plus direct bonding | Local oxidation | Thermal oxidation | 40 ± 2 nm | Smallest gaps, no CMP | High temperature | [18] |
| Anodic bonding to glass | Glass cavity plus metal | 350 °C | 120 nm with <2% variation | Low parasitics, through-glass vias | Outgassed O2 must be vented and the cavity resealed | [19,20] |
| CMUT-on-CMOS | Bonding or post-processing | CMOS budget ≤400–450 °C | — | 200× lower parasitics than wire bonds; thousands of channels | Integration complexity | [39,40] |

### 2.3 Array architectures

| Architecture | Channels | Examples | Key numbers |
|---|---|---|---|
| 1D linear or phased | N | 64–128 elements [35]; 16 elements [48] | 100% yield; first CMUT phased-array B-scans [35] |
| Fully addressed 2D plus ASIC | N² | 16×16 flip-chip [36]; 32×32 on a pulser ASIC [49]; 140×64 CMUT-on-CMOS [40] | 99–100% yield, up to 125% FBW [36] |
| Row-column / TOBE | 2N | DTU 62+62 [37]; DTU 190+190 [38] | 102% FBW, ghost echo −15.8 dB [37]; only ~55% of elements good [38] |
| 2D on glass with through-glass vias | N² | NCSU 16×16 at 250 µm [20] | ~2 Ω and ~20 fF per via; motivated by patterned neural stimulation |

**Butterfly's chip** [40]:
- 140×64 = 8,960 elements at 208 µm pitch.
- 5 µm doped-Si plate over a 200 nm gap; 1–10 MHz.
- About 9,000 seven-level ±25 V pulsers, more than 11,000 amplifiers and 1,120 10-bit ADCs; ≤3 W; 0.13 µm BCD CMOS.
- Cavities are sealed by an anneal above 450 °C, then the MEMS wafer is metal-bonded to the CMOS at low temperature.
- Yield and charging mitigation are not reported.

### 2.4 Commercial status

- A 2025 systematic review counts 19 commercial ultrasound-imaging CMUT products from 7 companies. Only 4 are clinically approved: Hitachi Mappie (discontinued), Hitachi SML44, Butterfly iQ/iQ+ and Butterfly iQ3 [44].
- **Butterfly iQ3:** FDA 510(k) K232808, decided 2024-01-04, 1.0–12 MHz [42]. A Yole teardown reports the process went from 17 masks and 2 SOI wafers (first iQ) to 10 masks and 1 SOI wafer [41]. Butterfly's January 2026 investor deck lists a "9,000 element 2D Matrix Array" and "Neuromodulation & BCI" among its target markets [43].
- **Others:** Philips collapse-mode CM5 devices were used in the 2026 BBB preprint [51]. Exo's Iris handheld uses pMUTs, not CMUTs [45].

### 2.5 Record performance (context, not targets)

| Device | Result | Ref |
|---|---|---|
| Single-membrane SOI element, 2022 | k_T² up to 0.953; 10.4 MPa pp at the surface (back-corrected); 61.2 kPa/V vs 23.7 kPa/V for a P4-2 PZT element; 938 µV/kPa | [5] |
| Piston-plate poly-Si cell, 120 nm gap, 2022 | Pull-in 7.4 V; surface pressure rises from 44.7 to 502 kPa with a 25 µm piston; 107–135% FBW in oil | [30] |
| 5 MHz wearable neurostimulator, 2021 | 2.1 MPa pp at 3.5 mm depth, 0.6 mm beam width, 60 V pulsers, 17 mg head unit | [48] |
| Therapeutic CMUT, 2010 | 1.4 MPa pp at the surface at 172 V DC; 1.7 MPa pp continuous wave for 1 h | [52] |
| 32×32 HIFU array with integrated IC | 16 MPa pp at 5 MHz, 1 cm depth | [1] |

### 2.6 CMUT vs PMUT vs bulk PZT

| | CMUT | PMUT (thin film) | Bulk PZT |
|---|---|---|---|
| Drive | DC bias near pull-in (typically 50–200 V) plus AC; or pre-charged / AC-only | Low-voltage unipolar: 0.44 MPa pp at 14.6 V, 1.4 MHz [54] | High voltage: 1.15 MPa at 150 Vpp (cited in [54]) |
| Bandwidth in liquid | ~100–135% FBW [35,36,30] | Not compared in the verified sources | Narrowband in tFUS systems [51] |
| Coupling | ~0.3 typical, up to 0.95 [5] | Low; sensitive to residual stress [55] | PZT/PMN-PT composites ≤ ~0.73 [5] |
| Self-heating | Si ≈ 130 W/m·K [52] | Si substrate | PZT-4 ≈ 1.25 W/m·K [52] |
| MRI | Bare device: no measurable change in 3T EPI images or B0 map [46]; CMUT barely disturbed EPI where a PZT disk badly obscured it [47] | Not reported here | Strong artifact [47] |
| Arrays and CMOS | Lithographic; 8,960-element commercial CMUT-on-CMOS [40] | Lithographic; a 26×26 PZT-on-CMOS array is cited in [54]; commercial handheld [45] | Diced; cabled probes limited to a few hundred channels [40] |
| Main weakness | Bias; charging and breakdown at ~10⁸ V/m [12]; large stroke needed below 1 MHz | Low coupling; PZT deposition and plasma etch | Narrowband, heating, MR artifact |
| Feasible in 6.2540? | The sacrificial-release route is (§3) | Not in the core plan. Sputtering and perovskites are allowed, but PZT needs a >600 °C crystallization anneal and poling, which are not available. A sputtered ZnO or AlN PMUT would be REQUIRES-STAFF-APPROVAL | No |

---

## 3. Low-temperature / accessible CMUT fabrication

### 3.1 From the Lecture-4 cantilever to a CMUT cell

| Lecture-4/Pset-4 step | CMUT equivalent | Course-allowed implementation |
|---|---|---|
| Cr bottom electrode (evaporation + lift-off) | Bottom-electrode disk per element | Evaporation + MLA lift-off ✓ |
| Si3N4 insulator patterned by RIE | Insulator (sets g_eff, prevents shorts) | Sputtered or evaporated SiO2 patterned by **lift-off** ✓ (RIE is not allowed) |
| Spin-coated sacrificial resist with anchor openings | Gap-defining sacrificial layer | Spin coating + MLA ✓; dilute the resist for 50–100 nm |
| Sputtered Al beam, lithography + etch | Al membrane that is also the top electrode, with release holes | Evaporation or sputtering + MLA + PAN wet etch ✓ |
| Remove sacrificial resist to release | Release and dry | Acetone wet release ✓; critical-point drying needs approval |
| (none) | Vacuum seal for immersion | PECVD, LPCVD or Parylene need approval. Spin-coated SU-8 (on-list) has sealed µm-gap cells [26], but it would wick into a 50–100 nm gap through the holes and seals at 1 atm of air, not vacuum. So the plan uses vented cells, a recognized airborne CMUT class [69] |

### 3.2 Published processes closest to the course tools

| Work | Gap (sacrificial) | Membrane | Peak T | Release / drying | Result | Course mapping |
|---|---|---|---|---|---|---|
| UBC polyCMUT [15] | 300 nm concentrated Omnicoat, spun | SU-8 (0.67 + 2.40 µm) with embedded 0.57 µm evaporated Cr | 150 °C | MF319 (TMAH) 3 h, DI rinse, IPA, then critical-point drying; 3.67 µm Parylene seal | 64-element array imaged wires to 85 mm; 1.525 MHz and 101.6% FBW in oil; pull-in 65 V (220 V with the electrode on top); >2×10⁸ cycles; ~17 h build | All allowed except O2 plasma, critical-point drying and Parylene |
| Pirouz & Degertekin [22] | 110 nm evaporated Cu, giving a 95 nm gap | 2.2 µm PECVD SiN with Al electrode | 250 °C | Cu etchant; critical-point drying **or an 85–90 °C oven for ~1 h** | ~9 MHz arrays; >2×10¹¹ cycles with evaporated-SiO2 lift-off supports deposited below 110 °C | Metals and lift-off allowed; PECVD and CHF3 RIE need approval |
| imec / KU Leuven [23,24] | 100 nm evaporated Cr (lift-off) | ICPCVD SiN with Ti/Au/Ti | 450 °C (polyimide cure) | Cr etchant 3.5 h, critical-point drying; SiN + ALD seal | 16 V pull-in at 42 µm diameter; compressive sag of −90 nm left a 20 nm gap; only 62% detectable at 44 µm; Cr thickness varied 10–15% | Metals allowed; ICPCVD, RIE, critical-point drying and ALD need approval |
| Roma Tre [26] | Evaporated Cu (later Al, ~10× smoother) | 3 µm SU-8 on 5 µm polyimide | Low | Wet metal etch through 3 holes per cell | No stiction at 50–150 µm diameter; 6.5 MHz in air | Essentially all allowed |
| Bahette et al. [25] | Ni | 200 °C PECVD SiN | <400 °C | Wet | Low charging | PECVD needs approval |
| Tawfik et al. [27] (process, not a CMUT) | 500 nm S1805, hard-baked up to 170 °C | Sputtered Ti/Al/SiC | <180 °C | Remover 1165 at 70 °C with ultrasound; critical-point drying | Resist that is not hard-baked outgasses and flakes during sputtering | Spin, sputter and wet steps allowed; remover needs approval |
| Pang & Chang [29] | 2 µm SU-8 walls with a roll-laminated SU-8 top | 4 µm SU-8 with AgNW electrode | <100 °C | None (laminated) | 880 kHz in air; ITO and AZO electrodes cracked within 5 min, AgNW survived | Lamination needs approval |
| Joseph et al. [31] | Not stated (abstract only) | SU-8 | 140 °C | All wet, 3 masks | 835 kHz in air; 1.8–5.2 MHz across 30–54 µm radii | Probably all allowed |

I found neither a teaching-lab CMUT project nor a peer-reviewed CMUT whose cavities were sealed with sputtered or evaporated metal.

### 3.3 What changes outside a state-of-the-art cleanroom

- **Drying is the first gate.**
  - Capillary collapse during evaporative drying is usually irreversible. The remedies are freeze drying, supercritical CO2 or dry release [3,13]. Sandia measured 0% stiction-free yield after air drying vs 78% after supercritical CO2 [28].
  - The Tas critical length scales as (Et³g²/γ)^¼, so cutting surface tension 4× (water to hexane) gains only ~1.4× in length [13].
  - Without critical-point drying, the model puts the wet-release-safe radius of a 1 µm Al plate at ~9–12 µm for 50–100 nm gaps and ~39 µm for a 1 µm gap (§6.2).
  - Cyclohexane freeze-sublimation at about −5 °C has released 1 mm cantilevers over 2 µm gaps [13]. It needs a cold plate, which needs approval.
- **Sealing is the second gate.**
  - An unsealed cavity floods in liquid, and squeeze-film damping then destroys efficiency [3].
  - Published low-temperature seals use PECVD or ICPCVD SiN, Parylene, ALD or spin-coated SU-8 [15,23,26].
  - A sputtered seal would trap gas at mTorr pressure and closes small holes poorly; neither effect is quantified.
  - Hence the plan uses vented cells tested in air.
- **Insulator by lift-off.** Evaporated-SiO2 lift-off below 110 °C has been published [22]. Deposited oxides should be weaker and more trap-rich than thermal oxide: 0.15 µm thermal oxide measured 870 V/µm, while extrinsic breakdown is 100–200 V/µm [3].
- **Gap control.** Thermal oxide reaches 0.64% [3]. The anodic-bonding process of [19] held a 120 nm gap to <2%. Evaporated Cr varied 10–15% in imec's flow [23]. Spin-coated films below 100 nm are unverified. Each 10% of gap error moves pull-in by ~15%.
- **Stress.** Annealed Al can reach ~500 MPa tensile [3]. Compressive stress pre-deflected imec's cells and collapsed some during fabrication [23]. Leaving out thermal stress is one reason FEA over-predicts collapse voltage: 58 V calculated vs 20 V measured [11].

---

## 4. Ultrasound neurotech and where CMUTs fit

### 4.1 Applications and acoustic requirements

| Application | Frequency | Pressure / intensity | Aperture | Pitch | Elements | Transducer in cited work | Ref |
|---|---|---|---|---|---|---|---|
| Rodent transcranial neuromodulation | 183–460 kHz | 27–52 kPa as stated in [46] (its pressure–intensity pairs imply rms values, so peak ≈ 38–74 kPa) and 55 kPa peak in [47]; I_SPTA 34–174 mW/cm² ([46] labels the same axis I_SPPA in one figure) | 8.1 mm ring or disk | — | 32 (ring); 1 disk of 384 cells | CMUT | [46,47] |
| Small-animal high-resolution stimulation | 3.4–5 MHz | 2.1 MPa pp (I_SPPA 33.5 W/cm²) at 3.5 mm; 33.1 W/cm² at 3.4 MHz | 2.4 mm (1D) | 150 µm (λ/2); 250 µm (2D) | 16; 32×32 | CMUT plus ASIC | [48,49] |
| NHP / human transcranial stimulation | ~0.8 MHz | NHP range stated as 25–35 W/cm² (~0.87–1 MPa PNP) | 15 mm elements | — | 128-element helmet projected to give 950 kPa, MI 1.1 | CMUT (element measured, array simulated) | [50] |
| Rat BBB opening | 0.7 MHz | ~400–800 kPa PNP, free field | 5 cm focus | — | 5 transmit + 1 receive | Collapse-mode CMUT | [51] |
| fUS brain-machine interface (macaque) | 15.6 MHz | Regulatory envelope: FDA Track 3 (MI ≤ 1.9, derated I_SPTA ≤ 720 mW/cm²) [60]; the actual output of [57] was not verified | 12.8 mm | 100 µm | 128 | Conventional linear array (paper does not say CMUT) | [57,60] |
| Human fUS through a cranial window | — | — | — | — | — | ~200 µm resolution through a window over a skull defect | [58] |
| Retinal stimulation (ex vivo) | 43 MHz | Thresholds 250–754 mW/cm²; saturation at 10–30 W/cm² | 90 µm focal spot | — | 1 | LiNbO3 (not CMUT) | [53] |

fUS imaging was introduced by Macé et al. [56]. Legon et al. showed transcranial focused ultrasound modulates human somatosensory cortex [59].

#### Transcranial stimulation: parameters and safety

| Quantity | Published range or limit | Ref |
|---|---|---|
| Human fundamental frequency | 220–650 kHz in the 18 focused-TUS studies of [75] (its 35 studies also include non-focused TUS and transcranial pulse stimulation); 0.21–0.86 MHz across the 34 motor/sensory studies of [76], most at 0.5 MHz | [75,76] |
| Human peak rarefactional pressure | 0.21–0.80 MPa; MI 0.20–1.13. The basis is not stated: [76] does not say whether its values are free-field, derated or in situ. [81,83] are explicitly in situ, at 0.775 and ≤ 0.6 MPa | [76,81,83] |
| Human I_SPPA | ~1–35 W/cm² in motor/sensory studies; deep-target studies up to 80 W/cm² (Exablate, 220 kHz) | [75,76] |
| Pulsing | Duty cycle 1–70%; PRF 5 Hz–1 kHz; trains of 0.1–1 s (online) or 40–120 s (theta-burst); sessions up to 600 s | [75,76] |
| Mouse | 0.18–10 MHz at I_SPPA 0.14–5.4 W/cm². Between 0.3 and 2.9 MHz the threshold intensity rises ~f² | [84,85] |
| Rodent skull reverberation | At 320 kHz, the in-situ peak pressure is ~1.8× the free-field calibration | [98] |
| ITRUSST safety consensus (valid for 200–800 kHz only) | **Mechanical:** MI or transcranial MItc ≤ 1.9 with no contrast agents; no separate I_SPPA or I_SPTA limit. **Thermal:** any one of ΔT ≤ 2 °C, T ≤ 39 °C, a thermal dose ≤ 2 CEM43 in brain (16 in bone, 21 in skin), or a time-limited thermal-index table | [77] |
| Skull transmission (human calvaria, 7.4 mm mean thickness) | Energy transmission 0.40 at 270 kHz, 0.10 at 836 kHz and 0.04 at 1.4 MHz. 95th-percentile maximum *pressure* transmission is 40–78% over 0.1–1.5 MHz | [79,80] |
| Device formats | 64 mm single element at 500 kHz, ≤ 0.6 MPa in situ [83]; 128-element random sparse cap at 650 kHz with 46% coverage, giving 28% of free-field amplitude behind a macaque skull [82]; 256-element helmet at 555 kHz with a 1.3 × 3.4 mm focus at 775 kPa in situ [81]; 1024-element, 660 kHz, 30 cm hemispherical ablation helmet [100] | — |
| Auditory confound | Pulsed TUS is audible in humans (16 of 18 participants) [83]. In rodents, ultrasound evokes auditory-pathway activity [86,87]. Smoothing the envelope over 12 ms abolished auditory brainstem responses, and motor responses persisted in deaf mice [88] | — |

Before the consensus, a 2019 review found I_SPTA above the FDA diagnostic limit in 14 of the 20 studies where it could be computed, and no adverse effects in 30 of 33 studies [99]. The ITRUSST practical guide notes that diagnostic imaging transducers (~1–20 MHz) cannot push enough energy through the human skull [78].

**What this means for a CMUT stimulation array** (my estimates from the cited formulas):
- **Pitch.** λ/2 in tissue (c = 1540 m/s) is 3.1 mm at 250 kHz and 1.2 mm at 650 kHz. Each element is therefore a large gang of cells, or the layout is a random sparse cap [82].
- **Pressure.** The MI cap allows up to ~1.34 MPa in situ at 0.5 MHz (p = 1.9·√f).
  - Studies report 0.2–0.8 MPa, but the main review [76] does not say whether these values are free-field, derated or in situ; only [81,83] are explicitly in situ.
  - If they are in situ, 28–78% skull pressure transmission gives roughly 0.3–2.9 MPa free-field at the focus. The 28% figure is from one macaque skull piece [82]. The 40–78% figure is the 95th-percentile *maximum* for human skull [80], so it is an upper bound on transmission.
- **Surface requirement.** A 64 mm aperture focused at ~63 mm has a focusing gain of ~17 at 0.5 MHz (O'Neil approximation).
  - The required *surface* pressure is then only ~0.02–0.17 MPa, before element-coverage and phase losses. It is ~0.01–0.05 MPa if the reported values are already free-field.
  - CMUTs have already shown 190 kPa at the surface, at ~680 kHz (an 800 kHz-centre element driven AC-only at 340 kHz) [50].
  - The model's optimistic stroke ceiling at 0.5 MHz is ~260–310 kPa (§8), or roughly half that if Merbeler's measured-to-ceiling ratio applies. Partial element coverage raises the requirement in proportion.
  - So the barrier to a human-scale CMUT stimulator is fabrication and drive (µm gaps, thick sealed plates, ~100 V bias, reliability), not transduction physics. None of those barriers can be overcome with the course process.
- **Drive electronics.** The 200–800 kHz range covered by the ITRUSST consensus and the auditory confound both call for programmable, ms-scale amplitude envelopes rather than square gating.

#### Brain imaging and wearable formats

| System | Frequency | Array | Notes | Ref |
|---|---|---|---|---|
| Macaque fUS brain-machine interface | 15.6 MHz | 128 elements, 0.1 mm pitch, ~400 µm elevation slice | 11 plane waves at 5.5 kHz PRF, compounded at 500 Hz; one Doppler image every 0.5 s; no transmit pressure or MI reported | [57] |
| Neonatal fUS through the fontanelle | ~6 MHz | Miniaturized probe on a soft headset with EEG | MI 0.85 and I_SPTA 43.5 mW/cm² (~1/16 of the FDA ceiling); ~200 µm resolution to 8 cm | [89] |
| Mobile adult fUSI | 5.3 MHz | Commercial linear array | Through a 4 mm PEEK cranioplasty; ~200 µm resolution | [90] |
| Transcranial 4D fUS (rat) | ~7.8 MHz | 32 × 32 matrix (1,024 elements) | Through intact skull and scalp; 500 volumes/s | [91] |
| Human 4D fUSI (preprint) | — | 3,072 transceivers on custom ASICs | 450 Hz volume rate to 8 cm; sized for cortical placement | [92] |
| Wearable transcranial Doppler patch | 2 MHz | 16 × 16 piezocomposite, 750 µm pitch, 12 × 12 mm | 1.3 mm thick; derated MI ~0.7, I_SPTA 370 mW/cm²; matched a conventional TCD probe in 36 participants | [93] |
| Silicon-nanocolumn CMUT (snCMUT) flexible patch | 5 MHz design (4.25 MHz packaged) | 64 elements; each has 40 cells of 120 µm, each cell with a 3 × 3 grid of silicon nanocolumns | Imaged at 30–40 V DC; 74% pulse-echo FBW; ~0.93 mm thick. Its 220 kPa/V figure is a back-calculated surface value, not a direct measurement | [94] |

- **Acoustic windows.** Human fUSI has been published only through an acoustic window: a transparent cranial implant, a cranioplasty, a skull defect, or the neonatal fontanelle [58,90]. Through intact adult skull, monitoring drops to ~2 MHz Doppler [93].
- **Flexible CMUTs.** Published flexible CMUT arrays span 4–10.7 MHz, with 60–100 V DC bias and bend radii down to 0.45 mm [55].
- **CMUT vs PZT on receive.** In a photoacoustic head-to-head test, two CMUT probes showed 161–176% receive fractional bandwidth against 99–111% for PZT, and one CMUT probe was ~11.6 dB more sensitive than its matched PZT probe [95]. The CMUTs' measured receive centres (2.6 and 3.8 MHz) sat well below their 8.9 and 10 MHz nameplates, which inflates the percentage bandwidth.
- **Closest analog to this project.** The snCMUT patch [94] is the nearest published device to this project's theme: a CMUT whose design centres on nanostructured features, packaged as a wearable. It used bonded-silicon processing that is not on the course list.

#### Sonogenetics

- Published sonogenetic actuators span ~0.3–27 MHz and 0.044–3 MPa peak negative pressure [97].
- Example: human TRPA1 expressed in mouse brain was activated at 7 MHz and 0.35–1.05 MPa intracortical peak negative pressure through the intact skull, using a LiNbO3 transducer [96]. At 7 MHz that is MI ≈ 0.13–0.40; the paper's 0.37–0.95 MI range covers its experiments overall.
- **Relevance:** sonogenetics lets higher-frequency, smaller-aperture arrays act on genetically targeted cells. That is closer to the imaging-corner frequencies a nanogap CMUT reaches naturally. In vivo pressures are typically ~0.3–1 MPa, though engineered MscL variants respond to ~0.05 MPa [97].

### 4.2 CMUT-specific neuro demonstrations

| Work | Device | Result | Caveats |
|---|---|---|---|
| Kim et al. 2019 [46] | 32-element ring, 183 kHz, 0.035 g | Motor responses in mice: >70% success at I_SPTA 34.1 mW/cm², against 0–7% for sham controls; bare device MR-compatible | First CMUT/array-based demonstration in freely moving mice, not the first overall; 10/10 trials in one freely moving mouse |
| Jo et al. 2022 [47] | 8.1 mm disk of 384 cells: a = 90 µm, 3 µm Si, 1.75 µm gap, 460 kHz | 55 kPa; chronic closed-loop stimulation during NREM sleep restored Y-maze performance; 87 mice; no EEG artifact | Wafer-bonded; 100 V DC (~80% of pull-in) |
| Seok et al. 2021 [48,49] | 16-element 5 MHz 1D array on a 60 V ASIC; 32×32 array on a pulser ASIC | 1D: 2.1 MPa pp at 3.5 mm. 2D: I_SPPA 33.1 W/cm² at 3.4 MHz and 5 mm (12.4 W/cm² at 2 MHz), with mouse-skull phase correction adding ~10% pressure ([49], abstract only) | Bench and hydrophone data only |
| Ibn Minhaj et al. 2024 [50] | 15 mm element, 207 cells, 50 µm Si, ~430 nm gap, anodically bonded to glass, 800 kHz | 190 kPa PNP at the surface, driven AC-only at 340 kHz | Array result is simulated; no charging or heating data |
| Kilinc et al. 2026 [51] | Philips CM5 in collapse mode at 100 V, 700 kHz, 3D-printed housing | MRI-confirmed, pressure-dependent BBB opening in rats; a CMUT also served as passive cavitation detector; phase inversion suppressed the fundamental by ~58 dB and the third harmonic by ~36 dB | Preprint; rat count inconsistent (3 vs 2) |
| Wong et al. 2010 [52] | 2.5 MHz therapeutic CMUT | 1.4–1.7 MPa pp; MR artifact <1 mm beyond the device edge | MR-guided HIFU, not neuro |
| Saccher et al. 2023 [16] | Pre-charged collapse-mode CMUT | Works with no external bias; >2.5 years at 37 °C (accelerated test) | Aimed at powering implants |

I found no peer-reviewed CMUT retinal stimulator and no CMUT-based fUS brain imaging. The canonical retinal-stimulation work used LiNbO3 [53].

### 4.3 Industry landscape (verified facts only)

- **Butterfly Network** makes the CMUT-on-CMOS chip in §2.3. On 2023-10-24 it announced a 5-year co-development deal with Forest Neurotech for an ultrasound brain interface built on that chip: $20M total, $3.5M at signing, according to Butterfly's release [61].
- **Forest Neurotech is now Arbor Neuroscience**, a nonprofit focused research organization within Convergent Research [62].
  - "Forest 1" is listed as a wearable whole-brain ultrasound interface for functional imaging and neuromodulation [62].
  - It is in an ARIA-funded UK safety study enrolling up to 30 craniectomy patients over 3.5 years from March 2025 [63].
  - **No source says which transducer Forest 1 uses.** Do not claim it is a CMUT.
- **Merge Labs** was announced around 2026-01-16 with a $252M seed round (investors include OpenAI, Bain Capital and Gabe Newell), according to secondary news [64].
  - Secondary news [64] describes it, in its own narration rather than a company statement, as a non-implant BCI company using ultrasound and molecular approaches, spun off from Forest Neurotech. Founders include Mikhail Shapiro, Tyson Aflalo and Sumner Norman [64].
  - On 2026-09-01, Butterfly and Merge announced a multi-year license, through Butterfly Embedded, to Butterfly's "Poseidon" ultrasound-on-chip family [65,74]. Butterfly became Merge's exclusive CMOS-MEMS chip-based ultrasound partner, the value was not disclosed, and Butterfly may still license to other BCI companies.
  - This is the clearest public link between CMUT-on-CMOS hardware and a neurotech company. Treat claims of other licensees as unverified.
- **Butterfly's 2026 investor deck** lists neuromodulation and BCI as target markets [43].

### 4.4 Where CMUTs fit, and where a course project can sit

**For neurotech:**
- **Advantages:** wide bandwidth, low weight, lithographic arrays that integrate with CMOS, low self-heating, MR compatibility, and stimulation without EEG artifact [46,47,52,40].
- **Drawbacks:** a high DC bias near pull-in, dielectric charging and breakdown, and the large stroke needed at low frequency. 1 MPa needs ~10 nm of mean displacement at 10 MHz [12] but ~0.2 µm at 0.5 MHz (derived from p = ρc·2πf·ū).

**The design space splits into two corners:**
- **Stimulation (0.2–0.8 MHz, 0.05–1 MPa at the focus).** With large-aperture focusing, the surface requirement drops to ~0.01–0.17 MPa (§4.1), which is within demonstrated CMUT output. The devices that deliver it need µm gaps, thick plates, ~100 V and a vacuum seal, often with collapse mode or AC-only drive [46,47,50,51]. In the model, a 0.5 MHz immersed cell needs g ≈ 1.0–1.3 µm at ≤150 V, and its optimistic stroke-limited ceiling is ~260–310 kPa (§8).
- **Imaging and receive (5–20 MHz).** Favors small, stiff cells with small gaps.
  - Butterfly's CMUT-on-CMOS uses a 200 nm gap at 1–10 MHz with ±25 V on-chip pulsers; its DC bias is not reported [40].
  - Macaque fUS used a 15.6 MHz, 100 µm-pitch array [57], not stated to be a CMUT. Human fUSI through acoustic windows uses 5–6 MHz [89,90].
  - No CMUT-based fUS brain imaging has been published.

**What a course project can reach:**
- In the model, wet-released, sealed sub-100 nm cells go no lower than ~8.3 MHz immersed for 1 µm Al (~4.6 MHz for 10 µm SU-8; Table 4b in §8). That is the imaging corner, and the vented cells built here cannot be immersed at all.
- Cells with a ~1 µm resist gap reach the stimulation band, but they pull in at 90–120 V and cannot be sealed or tested acoustically.
- **Plan:** build the imaging-corner cell as the main device, build the stimulation-band cell as a baseline, and quantify the gap between them.

---

## 5. Fit against the 6.2540 requirements

| Req | Recommended NanoGap project | Verdict | Evidence | For comparison: a neuro-grade CMUT transmitter |
|---|---|---|---|---|
| C1 | 4 device MLA layers plus 1 MIM-witness layer, AZ3312 only; 2 runs; substrates banked after L1; run-1 release 11-16 to 11-18 | Meets (at risk if release fails or sessions are limited) | §6.6 | At risk: bonding, sealing, packaging |
| C2 | 50/75/100 nm gap-defining resist; 50 nm SiO2 as backup; ~8–14 nm bias-induced deflections measured on insulated array copies (≤0.7 V_PI; model 8.0 / 11.2 / 14.4 nm on the 50 / 75 / 100 nm matched copies) | Meets | Witness reflectance and SEM; pull-in scaling | Not natural (gaps 0.4–1.75 µm) |
| C3 | Evaporation, sputtering, spin coating, MLA, wet etching; insulator by lift-off | Meets. NMP remover and critical-point drying are fallbacks needing approval | §6.3 | Bonding, DRIE/RIE and PECVD sealing: REQUIRES-STAFF-APPROVAL |
| C4 | Cr, Au, Al, SiO2, AZ3312/PGMEA, oxidized Si | Meets | §6.4 | Single-crystal Si plates, glass bonding: approval |
| C5 | Optical microscope, SEM, I-V setup, optical reflectance | Meets for the core plan, *provided the I-V setup can be used at 21–40 V*. Every stiction-safe bare cell pulls in above 20 V: 25.7–38.4 V in the model, and the IPA capillary floor is ~21 V even at 50 nm. If the instrument's >20 V range triggers the 42 V interlock rule [67], O2 needs the interlocked fixture (REQUIRES-STAFF-APPROVAL); ask on 10-29. LCR meter, impedance analyzer and vibrometer (stretch) need approval | §6.5 | Hydrophone, impedance analyzer: approval |
| D1 | One page with all four required elements; one PDF per group on Gradescope | Meets if the checklist in §0 is followed | — | — |
| D2 | Instructor meeting; one member signs up via the Canvas link (the guideline says "Wednesday October 29th", but 10-29 is a Thursday, so confirm the day) | Action needed now | §6.6, §9 | — |
| D3 | By 11-01: approach finalized with staff, supplies and tools list sent (§6.8), TA lab-hours sign-up | Planned | §6.6, §6.8 | — |
| D4 | 11-05 proposal talk, 5 + 2 min, with first spin-curve data | Planned | §6.6 | — |
| D5 | 11-24 update talk, 5 + 2 min, with run-1 data | Planned (run-1 release 11-16 to 11-18) | §6.6 | — |
| D6 | 12-10 final presentation (format to be set by staff) | Planned (run 2 optional) | §6.6 | — |

**Strongest options for the sub-100 nm feature:**

| Option | Form | How it is evidenced | Role |
|---|---|---|---|
| 50–100 nm resist-defined air gap | Structure | (a) Reflectance of the 75/100 nm resist on bare-Si witnesses run through the identical expose/develop/bake sequence. (b) SEM of cleaved *unreleased* witness stacks (Si/SiO2/resist/Al) plus resist-only witnesses. imec resolved a 100 nm gap at 22k× [23], but under a SiN membrane; cleaving a released, ductile 1 µm Al plate is unproven. (c) Pull-in data collapse, V·a² ∝ g^1.5 | Primary |
| 50 nm SiO2 insulator | Structure | SEM of cleaved SiO2-only witnesses. Reflectance works only by fitting the absolute spectrum against a bare-Si reference, because 50 nm SiO2 has no visible-range minimum. The C-V slope cannot independently evidence the 12.8 nm insulator term unless the air gap is known to a few nm | Guaranteed backup on every die |
| Electrostatic deflection of ~8–14 nm (insulated cells at ≤0.7 × V_PI; the larger deflection at bare-cell pull-in is inferred, not measured) | Measured quantity | C-V (free capacitance ≈+23% at 0.7 V_PI; static change ≈+6%); Michelson interferometer, where 1 nm ≈ 1% of the fringe peak-to-peak at 633 nm [71] | Supporting |
| 80–100 nm evaporated-metal sacrificial layer (QCM-controlled) | Structure | QCM plus SEM; precedents with Cr [23] and Cu [22] | Contingency only with changed electrode metallurgy. Cr etchant would attack the Cr adhesion and cap layers of the Cr/Au/Cr electrode; imec encapsulated its electrodes in SiN for this reason [23]. Needs electrodes with no exposed Cr (e.g., Ti/Au after a Ti soak check), no insulator-free cells, and week-1 soak coupons. Selectivity against Al is unverified |
| Colloidal AgNW electrode | Material | TEM diameter histogram; precedent [29] | Not used: incidental to the transduction |
| Graphene or graphene-polymer membrane | 2D material | Precedents [32,33] | Not viable as an immersed membrane (model: collapses under 1 atm unless tension ≥ ~1 N/m and a ≤ ~2 µm) |
| Atmospheric sag of a sealed cell (82 nm [15], 28 nm [19,21]) | Measured quantity | Interferometry | Requires sealing, which requires approval |

---

## 6. Recommended project: NanoGap CMUT (merged)

**Base concept:** C, which scored 22.5/30 and ranked first on both the compliance and the merit lens.

**Ideas grafted in, as the judges suggested:**
- **From A (22.0):**
  - a 2 µm release hole at the centre of each cell, with a mild bake and acetone release
  - a ~1 µm Lecture-4 baseline die
  - insulated and insulator-free twin cells
  - stress gauges (buckled Al bridges for compressive stress, plus ring-and-beam or pointer gauges for tensile stress)
  - MIM breakdown tests on separate witness pieces before any device is biased
  - a 3D-printed chip carrier
  - an MVP defined using on-list tools only
- **From B (17.5):**
  - an fUS spec table with separate "demonstrated" and "extrapolated" columns
  - a beamforming Monte Carlo fed with the measured element spread
  - Si witnesses through every step
  - a contingency using a QCM-controlled evaporated metal sacrificial layer
  - 1 × 1 mm C-V pads
- **From D (9.0):**
  - chemical-soak test coupons in week 1
  - etch-front monitor (dummy) cells
- **Judges' fixes:**
  - tag the NMP remover as REQUIRES-STAFF-APPROVAL
  - drop the 200 nm split from the ≤42 V dataset, because its stiction-safe cells pull in at 46–51 V (model)
  - put redundant copies of the bare cells on the die, since each is single-use
  - ask staff for the I-V instrument's voltage limit
- **Round-2 refinements (§6.12):**
  - wide SiO2-free wells for every bare test cell
  - guarded two-channel ramp C-V
  - three gap-matched copies of the array on every nanogap die

### 6.1 Objectives

- **O1.** Release Al-membrane CMUT cells over 50, 75 and 100 nm gaps (plus a ~1 µm baseline). Confirm the gap-defining films by reflectance and by SEM of cleaved witness stacks. The witness includes a bare-twin-geometry area, so "bare gap = insulated gap" is measured, not assumed.
- **O2.** Measure pull-in versus radius and gap on insulator-free cells at ≤40 V, and test V_PI·a² ∝ g_eff^1.5. Bare cells sit on thermal oxide in wide SiO2-free wells, so their gap equals the measured above-electrode witness gap.
- **O3.** Map wet-release stiction versus radius on four gaps, and test a_crit ∝ g^0.5. The bare twins of all three array copies add array-scale stiction data.
- **O4.** Build 8-element, 100 µm-pitch arrays (the fUS-probe pitch) at three gap-matched radii, a = 7.75, 9.5 and 11 µm, all on every nanogap die.
  - On each die, choose by measurement the copy matched to its gap (§6.5).
  - For that copy, report element yield; the uniformity of C0 and of the bias-induced free-capacitance change at ≤0.7 × its calibrated V_PI, by guarded ramp C-V; and the pull-in spread of its bare twins, at ≤40 V.
  - Array elements are insulated and are never pulled in.
  - Convert the measured spread into a simulated beamforming loss. Where matched arrays exist on more than one gap, also report uniformity against gap.

### 6.2 Device specification (model)

| Item | Value | Notes |
|---|---|---|
| Membrane | 1.0 µm evaporated Al, also the top electrode | Fallback: 0.8 µm sputtered Al, with a = 8.0 µm giving 31.9 MHz, 42.8 V insulated / 33.8 V bare, R = 0.15 |
| Release path | 1.5–2 µm drawn centre hole (~3–4 µm after PAN undercut) plus 2 channel breaks in the anchor ring | Hole not modelled; expect a few % to ~10% shift in V_PI (my estimate). The ladder includes channel-only cells as a control |
| Bottom electrode | Cr/Au/Cr 5/25/3 nm disk, radius 0.85a, routed through the anchor breaks | **Routing rule:** no landed Al (anchors, webs, element sheet, top leads) may sit over any bottom electrode, bus or lead with only the 50 nm SiO2 between them. At ~30 V that SiO2 would see ~6 MV/cm, the range where the MIMs may fail. Run disk-to-disk buses only inside released channels through the two anchor breaks, which is the routing the model assumes. Carry each channel past the end of the element's Al into an L4 opening, which also makes it a release path. Never let a top-Al lead cross a bottom bus except over a channel. Insulated-cell anchors sit on the 50 nm SiO2 over the thick thermal oxide. Bare-cell anchors, electrodes and buses sit directly on thermal oxide in the wide SiO2-free wells (§6.3 step 5), with no SiO2 edge crossing a bare bus. All anchors stay away from all bottom metal, and the anchor-break clearance rule below also covers the uncovered bare buses; bottom pads sit in L2 openings on thermal oxide. **Overlay:** the electrode-to-anchor margin is 0.15a, which is 0.9, 1.05, 1.16, 1.2, 1.35, 1.43 and 1.65 µm at a = 6, 7, 7.75, 8, 9, 9.5 and 11 µm. The 7.75 µm copy's fallback 5.75 µm electrode raises V_PI ~2% and lowers C0 by ~24%. Each anchor break must clear its lead by at least twice the overlay error. If staff cannot confirm L3-to-L1 overlay below ~0.9 µm, draw electrodes at radius min(0.85a, a − 2 µm); in the model this raises V_PI by ~1–3% (~5% at a = 6 µm) and lowers C0 by ~14% at the design point. The 33 nm step is not small next to a 50–100 nm gap, so g is defined as the resist thickness *above the electrode* (§6.3 step 4) |
| Insulator | 50 nm SiO2 (sputtered or e-beam), patterned by lift-off and omitted on insulator-free twin cells | g_eff = g + 12.8 nm |
| Gap splits | 50, 75, 100 nm (diluted AZ3312); ~1 µm baseline (undiluted AZ3312) | 200 nm only if the >42 V interlock is approved |
| Design-point cell (75 nm gap, a = 9.5 µm) | f_vac 28.3 MHz; 25.7 MHz at 0.7 V_PI (24.3 MHz at 0.8 V_PI). If sealed: 15.4 MHz by the Lamb estimate, 15–23 MHz expected | Squeeze-film stiffening in the vented 75 nm gap ≈ 1% |
| Pull-in | 42.4 V insulated (Galerkin 41.8 V; 41.4 V if sealed); 33.5 V insulator-free; ±200 MPa stress gives 38.6–45.8 V | Buckles only at −1081 MPa |
| Stiction ratio | R = 0.157 dried from IPA; 0.49 from water | Dry from IPA only |
| Operating point | At the ≤0.7 × V_PI limit (~30 V nominal): 11.2 nm centre deflection, k_T² ≈ 0.13 (0.85a partial electrode), static capacitance +6% (the ramp C-V reads the free capacitance dQ/dV, which rises +23%), 1.0 MV/cm in the insulator and 3.9 MV/cm in the air gap, f ≈ 25.7 MHz in vacuum. For reference, 0.8 × modelled V_PI (34 V) would give 15.7 nm, k_T² = 0.20 (0.16 for full coverage), +9%, 1.2 MV/cm and 24.3 MHz | **Never apply a fixed bias blind.** The model matched one published pull-in within 5% but over-predicted the SU-8 device [15] by 34–52% (§8). Calibrate each die and array copy instead, never transferring between copies: (1) Measure bare-twin pull-in. (2) Multiply it by (g_eff/g)^1.5, computed from that die's measured gap and SiO2 thickness, to estimate the insulated V_PI. Nominal factors are 1.41 / 1.27 / 1.20 for the 50 / 75 / 100 nm gaps and 1.02 for the 1 µm baseline. (3) Start at ≤0.6× that estimate. Step up toward 0.7× only while the measured free capacitance tracks the model's softening curve, scaled to that copy's calibrated V_PI. The curve is the same for every copy: about +14% at 0.6× and +23% at 0.7×. At 20 V it is +9.9% / +7.8% / +6.5% on the 7.75 / 9.5 / 11 µm copies. Stop at any jump or hysteresis. The transfer assumes the bare twin's air gap equals the insulated cell's, so the bare twins sit in wide SiO2-free wells (§6.3 step 5). In the planarization model this leaves a residual twin-gap offset of ≤0.3 nm. Without the wells, a bare gap just 10–20 nm larger (75 nm die) would put a 0.7× bias at 0.85–1.0× the true insulated V_PI. Tests above 20 V may need the interlocked fixture (§6.7) [67] |
| Touchdown | 8.5 MV/cm across the 50 nm SiO2 | Pull in insulated cells only as a destructive test on designated spare ladder groups, never on any array copy |
| Arrays | Three copies on every nanogap die, each 8 elements × 100 µm pitch (10 µm kerf) × 2 mm, with a = 7.75 / 9.5 / 11 µm matched to the 50 / 75 / 100 nm gaps (table below). The design-point copy (a = 9.5 µm) has 240 cells per element, fill factor 0.34 and C0 = 4.96 pF per element. Each copy has its own bare twins, pads, dummy and metal radius label | Same pitch as the Griggs probe [57]. Calibrations are never transferred between copies |
| C-V pad | 1 × 1 mm, ~1,600 cells, ~33 pF (my estimate) | Gives ~33 pA at 1 V/s |
| Baseline die (1 µm gap) | a = 35 µm: f_air 2.08 MHz (2.20–2.25 MHz with the trapped-gas spring); 0.67 MHz Lamb estimate if sealed; V_PI 122 V; R = 0.16 | The stimulation-band analog; measuring its pull-in needs the interlock |

**Measurement ladder (model; vented; IPA drying).**

| Gap (nm) | a (µm) | V_PI insulator-free (V) | V_PI insulated (V) | R | Predicted state |
|---|---|---|---|---|---|
| 50 | 7 | 33.5 | 47.2 | 0.10 | free |
| 50 | 8 | 25.7 | 36.2 | 0.18 | free |
| 50 | 9 | 20.3 | 28.6 | 0.28 | likely stuck |
| 75 | 9 | 37.3 | 47.2 | 0.13 | free |
| 75 | 9.5 | 33.5 | 42.4 | 0.16 | free (design point) |
| 75 | 10 | 30.2 | 38.3 | 0.19 | marginal |
| 75 | 11 | 25.0 | 31.6 | 0.28 | likely stuck |
| 100 | 11 | 38.4 | 46.0 | 0.16 | free |
| 100 | 12 | 32.3 | 38.7 | 0.22 | marginal |
| 100 | 14 | 23.7 | 28.4 | 0.42 | likely stuck |
| 1000 | 35 | 120.0 | 122.3 | 0.16 | free (pull-in needs the interlock) |
| 1000 | 40 | 91.9 | 93.6 | 0.28 | likely stuck |
| 1000 | 45 | 72.6 | 74.0 | 0.44 | likely stuck |

**Predicted critical radius** (R = 0.25 criterion / Tas 1.7× criterion):

| Gap | Critical radius |
|---|---|
| 50 nm | 8.7 / 10.5 µm |
| 75 nm | 10.7 / 12.8 µm |
| 100 nm | 12.3 / 14.8 µm |
| 1000 nm | ~39 / ~47 µm (scaled as g^0.5) |

The ladder runs from a = 6 to 50 µm on every die.

**Gap-matched array copies** (model; each at its target gap; R uses γ_IPA = 23 mN/m):

| Copy | Cells per element | C0 | R | V_PI bare / insulated | 0.7 × insulated V_PI | f_vac (at 0.7 V_PI) | Electrode-to-anchor margin |
|---|---|---|---|---|---|---|---|
| 7.75 µm on 50 nm | 372 | 7.15 pF | 0.156 | 27.4 / 38.5 V | 27.0 V | 42.5 (38.5) MHz | 1.16 µm (fallback electrode 5.75 µm) |
| 9.5 µm on 75 nm | 240 | 4.96 pF | 0.157 | 33.5 / 42.4 V | 29.7 V | 28.3 (25.7) MHz | 1.43 µm |
| 11 µm on 100 nm | 213 | 4.59 pF | 0.158 | 38.4 / 46.0 V | 32.2 V | 21.1 (19.1) MHz | 1.65 µm |

**Off-target copies:**
- The 9.5 µm copy on a 50 nm die (R = 0.35) and the 11 µm copy on a 50 or 75 nm die are predicted stuck.
- The 7.75 µm copy on 75 or 100 nm dies, and the 9.5 µm copy on a 100 nm die (bare 51.5 V), exceed 40 V and are never biased.
- The lowest bare V_PI of any copy on any die is 13.6 V, so unselected copies are screened only at ≤±2 V.

**Checks and caveats:**
- The insulator-free data obey V·a² ∝ g^1.5 exactly in the model. Two points at 50 and 100 nm with ±15% error pin the exponent only to about ±0.3.
- If the interlock is approved, the 1 µm baseline die could tighten that to about ±0.1 (my estimate), but only with independent stress data. At a = 35 µm, +100 MPa of tension raises V_PI by ~47%, because the tension term 12πN equals the bending term 192πD/a² at only ~87 MPa. Fit V_PI(a) with k = 192πD/a² + 12πN, using the bare-cell radius-ratio method (§11 of `cmut_model/designs/nanogap_results.txt`).
- In bare nanogaps the mean field at pull-in is 3–7 MV/cm, rising to ~12 MV/cm locally at the centre (50 nm gap, a = 7 µm). Arcing or welding is therefore possible (independent check).
- Insulated cells also see ~3.9 MV/cm across the remaining air gap at ~30 V (0.7 V_PI). Any discharge would charge the SiO2, so monitor the C-V shift.

### 6.3 Process flow

| # | Step | Technique | Material / thickness | Allowed-list mapping | Notes |
|---|---|---|---|---|---|
| 1 | Substrate prep | Solvent clean (acetone, IPA), dehydration bake | Si with ~1 µm thermal SiO2: ~14 device pieces of 2 × 2 cm (7 per run: 50/75/100 nm × 2 plus 1 baseline), plus MIM, spin-curve and SEM witness pieces | Wet bench | Use oxidized Si (not glass) for anything that will be cleaved for SEM |
| 2 | Week-1 coupons | Spin coating; reflectance; soaks | AZ3312 diluted in PGMEA at 4–5 ratios; Al, SiO2 and Cr/Au/Cr coupons | Spin coating, wet etching, optical characterization | Measure the spin curve to ±3 nm (model estimate). Soak each film in AZ300 MIF, PAN and acetone for the full release time. **Bake-under-Al strip test:** resist → bake at 115–125 °C → 1 µm Al with openings (Al through a stencil, or 2 µm holes opened by an L4-style litho and PAN) → lateral clearing distance against time in acetone. Under blanket Al, acetone enters only at the piece edge. **Anchor-adhesion coupon:** Al on cleared SiO2 and on bare thermal oxide (the bare-cell anchor surface in the wells), in acetone for the full release time, deposited in the existing session-2b Al run. **Pinhole/short test:** diluted resist on a Cr/Au/Cr witness, given the same develop and mild bake, then Al dots evaporated through a stencil, then probe for shorts before any release. Do not use L-MIM lift-off here: a second AZ3312 coat redissolves the thin film, the exposure and develop clear it under every dot, and the acetone lift-off removes it. Confirm that a stencil (shadow mask) is available for the evaporator |
| 3 | L1: bottom electrodes | AZ3312, MLA exposure, AZ300 MIF develop | Disks, buses, pads, MIM bottom plates, alignment marks and verniers; the radius ladder and three 8-element array copies (a = 7.75 / 9.5 / 11 µm, each with its own bare twins, pads, dummy and metal radius label), identical on every piece, placed side by side in the central, uniform-thickness area of the spin coat | Lithography (MLA), spin coating | The electrode-to-anchor margin is 0.15a (0.9 µm at a = 6 µm; 1.16 / 1.43 / 1.65 µm on the 7.75 / 9.5 / 11 µm array copies), so the L3-to-L1 overlay must be confirmed (§6.2 overlay rule). Put the full radius ladder, including any radii run 2 might need, on L1, because run 2 cannot redraw electrodes |
| 4 | Deposit electrodes | Evaporation, then acetone lift-off | Cr/Au/Cr 5/25/3 nm | Evaporation, wet bench | The 33 nm step is *not* small next to a 50–100 nm gap: spun resist is thinner over the electrode than on a planar witness. Measure resist thickness on electrode-patterned witness areas (reflectance against a Cr/Au reference, or SEM), and consider thinning the Au, which carries only DC and pA currents. **Bank ~7 pieces here, after L1, for run 2,** so run 2 can use a revised SiO2 thickness |
| 5 | L2: insulator pattern | AZ3312 + MLA | Openings over pads, plus wide SiO2-free wells around every insulator-free (bare) cell | Lithography (MLA) | Lift-off replaces the lecture's RIE. **Wells:** each L2 opening reaches ≥30 µm beyond the bare cell's anchor ring, and 50 µm where room allows [102]. Use one shared well per array end zone (~800 × 94–140 µm per copy, beyond the 2 mm element ends) and one or a few wells per ladder bare group. Bare electrodes, buses and anchors then all sit on thermal oxide, giving the same local topography as insulated cells. Insulated anchors stay ≥30 µm from any well edge. Each L2 opening runs along its bare bus to that twin's pad, or the bus ends in an L4 opening inside the well, so no SiO2 edge crosses a bare bus under Al. Bare-twin buses are 1–2 µm wide in channels ≤4 µm. That leaves ~32 µm of extra bare bus under each twin's released roof (+12–47% of electrode area, largest on the 7.75 µm copy), so a few more pinhole shorts are expected; the 1 V short test precedes every pull-in ramp. This removes v1's zero-margin 0.5 µm L2-to-L1 rule and keeps every SiO2 lift-off edge out of the cavities. The wells do **not** protect against shorts. Whenever the L1-to-L3 overlay error exceeds the 0.15a electrode-to-anchor margin, the anchor reaches the electrode whatever L2 does. That gives a dead short in bare cells, and a 50 nm MIM at full bias under the anchor in insulated cells. The overlay rule in §6.2 is the real protection. Check verniers before L3 exposure |
| 6 | Insulator | E-beam evaporation (sputtering as fallback), then lift-off | 50 nm SiO2, with witness pieces in the same run | Evaporation or sputtering | E-beam is preferred: sputtered SiO2 coats resist sidewalls and can harden AZ3312, giving hard lift-off and edge "fences". Evaporated-SiO2 lift-off below 110 °C has precedent [22]. Lift-off edges lie only at pad openings and the bare-cell wells, ≥30 µm outside every active membrane (step 5), never inside a cavity; inspect a witness edge by SEM |
| 7 | MIM witness capacitors (separate witness pieces, not device pieces) | Cr/Au/Cr bottom plates and contact pads from L1 (step 3; not blanket); SiO2 by L2 lift-off in the same run as step 6, with openings over the bottom-plate contacts; extra MLA lift-off layer (L-MIM) for the top dots | Al dots of 100–400 µm diameter and ~100–200 nm thickness (thin enough to lift off cleanly from ~1.2 µm AZ3312) on the 50 nm SiO2 | Lithography, evaporation | Breakdown measured before any membrane exists. Kept off device pieces because AZ300 MIF (step 8) and PAN (step 11) attack exposed Al |
| 8 | L3: sacrificial layer | Spin, MLA exposure of anchor rings (with 2 breaks) and surrounding area, short develop, **mild bake at 115–125 °C** | 50/75/100 nm diluted AZ3312 (2 pieces each) or ~1 µm undiluted | Spin coating, lithography | Do not hard-bake at 170 °C (that resists acetone [27]). Filter the diluted resist (≤0.2 µm); two half-thickness coats against pinholes are optional (soft-bake between coats, and check on witnesses that the second coat does not redissolve the first). Overexpose and overdevelop the anchor regions, and check clearing optically on witnesses: there is no O2 descum without approval, and any scum left in the anchors dissolves during release. Run the reflectance witnesses through this identical expose/develop/bake sequence, so dark erosion and bake shrinkage are in the measured gap. The electrode-patterned witness carries both an insulated-geometry area and a bare-twin-geometry area (electrode on thermal oxide in a wide well) |
| 9 | Membrane | Thermal evaporation if available | 1.0 µm Al, with an Si witness | Evaporation (sputtered 0.8 µm as fallback) | Evaporation is *assumed* to heat the resist less than sputtering. This is unverified, and a long 1 µm evaporation also heats radiatively. Rely on the bake-under-Al strip test, put a temperature-indicator label on a dummy piece, and deposit in segments. On the baseline die, check continuity over the 1 µm step |
| 10 | L4: membrane pattern | AZ3312 + MLA, short AZ300 MIF develop | Release holes, 10 µm element trenches (trench isolation as in [68]), pad isolation, post-process MIM monitors | Lithography | TMAH attacks Al, so keep development short. **Alignment:** after step 9 the L1 marks lie under 1 µm of blanket Al and show only ~0.03–0.2 µm of topography. Put L1 marks on the session-2 strip-test witness and check that the MLA camera finds them through 1 µm Al. If it cannot, build marks from stacked L1 metal + L2 SiO2 + L3 resist, or keep the mark fields free of Al during step 9 (stencil or staff-approved masking) |
| 11 | Pattern Al | PAN etchant at 35–40 °C | Etch stops on resist and SiO2 | Wet etching | Expect ~1 µm undercut. Rinse thoroughly in DI water before any acetone, with separate glassware and waste streams (PAN contains nitric acid) |
| 12 | Release | Acetone soak 2–4 h, then overnight, with 2 fresh changes; no ultrasound. Use a covered dish or closed glass jar with ample volume, labelled, in a location staff approve for unattended solvent. An open dish in a fume hood can evaporate dry within hours, leaving cells dried from acetone with dissolved resist in the gaps | — | Wet etching (solvent) | Track progress through the holes and on dummy cells. Fallback: heated NMP remover at 60–70 °C (**REQUIRES-STAFF-APPROVAL**) |
| 13 | Dry | Acetone to IPA ×3 without letting it dry; drain, then let the IPA evaporate at room temperature under a cover or gentle N2 | — | Wet bench | Never dry from water. Never heat IPA on an open hotplate: 90 °C is above its ~82 °C boiling point, and boiling in the cavities can lift membranes. [22] used an 85–90 °C oven, which would need staff approval. Optional critical-point drying of half the run-2 pieces (**REQUIRES-STAFF-APPROVAL**) |
| 14 | SEM witnesses | Cleave unreleased witness stacks (primary C2 evidence) and released witnesses (opportunistic; ductile Al may smear or tear); thin conductive coat if needed | — | Sputtering (coat) | Cleave lanes cross the ladder, all three array copies and one bare-twin well |
| 15 | Carrier and probe jig | Elegoo Mars resin print, IPA wash, UV cure | Resin | 3D printing | Printed between cleanroom sessions |
| 16 | Run 2 | Repeat steps 5–13 on the pieces banked after L1 | Revised SiO2 thickness (from the MIM data; keep it ≤100 nm, since above ~118 nm no matched array copy stays at 0.7 × V_PI ≤40 V), dilution and drying. Radii cannot be redrawn: the banked pieces' electrodes are fixed at L1, and L3 can only enlarge an anchor around a fixed electrode, never shrink it. So run 2 chooses among the radii already on L1 | As above | L2 + SiO2 can share session 4 with the run-1 release, so run 2 adds only 2 more sessions |

### 6.4 Materials

| Material | Role | Course category | Approval |
|---|---|---|---|
| Si pieces with ~1 µm thermal SiO2 | Substrate; cleavable SEM witnesses | Common semiconductor/insulator (purchased) | Confirm stock |
| Cr, Au (evaporated) | Bottom electrode and adhesion layers | Common metals, evaporation | — |
| SiO2 (sputter target or e-beam source) | 50 nm insulator; MIM dielectric | Common insulator | Confirm source |
| Al (evaporation; sputter target as fallback) | Membrane, top electrode, MIM top plates | Common metal | Confirm that 1 µm is feasible |
| AZ3312, AZ300 MIF | All 5 lithography layers (4 device + 1 MIM witness); sacrificial layer | Organic material; course chemicals | — |
| PGMEA / AZ EBR thinner | Diluting the resist for 50–100 nm films | Organic solvent | Confirm |
| PAN Al etchant | Opening holes and trenches in the Al | Wet etchant | Confirm stock |
| Acetone, IPA | Lift-off, release, solvent exchange | Solvents | — |
| Heated NMP-based remover (Remover PG / 1165) | Fallback release | Chemical not used in class | **REQUIRES-STAFF-APPROVAL** |
| Liquid CO2 (critical-point dryer) | Optional stiction-free release | Tool outside the course list | **REQUIRES-STAFF-APPROVAL** |
| Elegoo resin | Carrier and jigs | Organic material (3D printing) | — |
| Parylene-C | Stretch seal for oil immersion | CVD polymer | **REQUIRES-STAFF-APPROVAL** |

### 6.5 Characterization plan

| Measurement | Tool | On course list? | Question answered | Expected result (model) |
|---|---|---|---|---|
| Thickness of sacrificial and SiO2 films | Optical characterization setup (reflectance on bare-Si witnesses, plus electrode-patterned witness areas) + SEM | Yes | Are the gaps really 50/75/100 nm *above the electrode*? | 75–100 nm resist: a spectral minimum in the visible, ~±3 nm (model). 50 nm films show no visible minimum, so fit the absolute spectrum against a bare-Si reference with stated n, or use SEM |
| Cross-section | SEM of cleaved unreleased witness stacks and SiO2-only witnesses; released cells opportunistically | Yes (FIB or ellipsometer would be REQUIRES-STAFF-APPROVAL [72]) | C2 evidence: gap, insulator, membrane, resist residue | 75 ± 10 nm resist, 50 nm SiO2, 1 µm Al |
| Stiction map versus radius and gap | Bare cells (the ladder plus the bare twins of all three array copies, which adds array-scale data): 1 V short test with nA compliance and a full I-V curve (Al/Cr native oxides can hide contact at 0.1 V). Insulated cells: a C-V step per element, since the opaque 1 µm Al hides a 50–100 nm stuck deflection in brightfield. DIC or interferometric microscopy if available (confirm) | Yes (DIC to confirm) | Does a_crit ∝ g^0.5? | Critical radii as in §6.2, possibly off by tens of percent |
| MIM leakage and breakdown | I-V | Yes | Is touchdown survivable? | Survival needs ≥8.5 MV/cm; extrinsic breakdown of deposited oxides is far lower [3] |
| Pull-in of insulator-free cells | I-V: 1–10 nA compliance, 0.2–0.5 V/s, sweeps up and down | Yes (≤40 V; the interlock may apply above 20 V, §6.7) | Does V_PI·a² ∝ g^1.5? What are the stiffness and stress? | 25.7–38.4 V (§6.2); report gradual current rise and sharp contact step separately |
| Quasi-static C-V (ramp method, C = I/(dV/dt) = dQ/dV, the free capacitance) | **Guarded two-channel wiring:** two pA current channels sharing a common LO (two SMUs with preamps, a dual-channel SMU, or an SMU plus a picoammeter). The chuck is tied at one point to Force LO, never to a separate building earth and never to the force SMU's guard (which follows the ramp and adds ~2.95 pF). The piece is held flat under vacuum. With no chuck terminal, use clean Cu or Al foil clipped to LO, with no pastes or paints. Keep illumination constant during sweeps. Force the ramp on the element's top Al and measure at virtual ground on its bottom pad, at 1 V/s with CVal ≈ C0 + C_T on a Keithley 4200 (meas_qscv documents 0.1–1 V/s [66]). On other SMUs, use up to the instrument's documented ramp rate (5–10 V/s gives 5–10× more current), and average up and down sweeps [66,103] | Yes, if two pA channels exist. Otherwise fall back to v1: one SMU with the measured node on HI and the chuck floating or on that SMU's guard, never on LO (which adds ~5 pF), plus dummy subtraction. Single-SMU I-V tests (bare-cell pull-in, 1 V short test, MIM leakage) always keep the chuck floating | Element capacitance; g_eff from the slope dC/dA; softening; charging under bipolar sweeps | Element C0 4.96 pF on the design copy (7.15 / 4.59 pF on the others), 5 pA at 1 V/s. Free capacitance on the design copy: +7.8% at 20 V and +22.7% (~1.1 pF) at the ≤0.7 V_PI limit. Every matched copy rises +22.7% at 0.7 V_PI; at 20 V the 7.75 and 11 µm copies rise +9.9% and +6.5%. The static Q/V change is only +6.2% (+9% at 0.8 V_PI). 1 mm² pad ~33 pF. With the chuck tied to LO, the substrate path is suppressed to ~0.001–0.02 pF (back air gap ≤5 µm; <0.05 pF), not eliminated. An isolated floating chuck would add up to ~1.85 pF (37% of C0) and a bias-dependent MOS swing [104]. Measure one element per die both tied and floated as a check. Float any element shorted to its top. The bare twins share their element's top Al: during an element ramp to 0.7× they sit at ~0.99× (50 nm die, 7.75 µm copy), ~0.89× (75 nm) and ~0.84× (100 nm) of their own bare V_PI. So measure twin pull-in first and treat the twins as sacrificial. Floating their pads gives little protection, because the pads couple strongly to the grounded substrate. If a twin must survive, tie its bottom pad to the element's top during the ramp. Keep the open/dummy structures for the bus-to-top overlap (~0.3 pF), which grounding does not remove. These need the same pads, buses, channels and cavities, but no bottom disks: a dummy without cavities lands the Al on 50 nm SiO2 over its buses and measures a MIM instead of the parasitic. Use bipolar ramps, and record the substrate resistivity from the wafer box. Use several smaller C-V pads, because one shorted cell kills a parallel group |
| Copy selection, then array yield and uniformity | (1) Rank copies by witness gap and model R. (2) Pull in the bare twins only of copies predicted at ≤40 V that passed the short test (floating chuck). (3) Insulated V_PI = bare V_PI × (g_eff/g)^1.5. (4) The design copy is the one with 0.7× that value at ≤40 V and the lowest R. It gets full guarded C-V at ≤0.7 × its calibrated V_PI. Other copies get the short test and a ≤±2 V C0 screen only (optional, ~1 h per die) | Yes | Can course tools make a uniform nanogap array, and on which gaps? | ≥6 of 8 elements good on the matched copy; ±15% spread; matched arrays on ≥2 gaps per run (target) |
| Insulated vs bare twin pull-in (destructive) | I-V charge spike on multi-cell groups (≥50 cells; a single 21 fF cell gives only ~0.5–1 pC (ΔQ ≈ V_PI·ΔC with ΔC ≈ 10–20 fF at collapse; the model's estimate is ~0.95 pC per cell and 228 pC per 240-cell element)); >42 V interlock | Partly | Electrical measure of the insulator's equivalent gap | Ratio 42.4 / 33.5 = 1.27 |
| Baseline-die pull-in | Interlocked high-voltage fixture | No (**REQUIRES-STAFF-APPROVAL**) | Extend the gap range 20× | 92–122 V |
| C-V at 100 kHz, dissipation factor | LCR meter | No (**REQUIRES-STAFF-APPROVAL**) | Cleaner C-V; the dissipation factor rises at collapse [24]; note the E4980A limits AC+DC to 42 V peak [24] | Same capacitances as above |
| Resonance in air versus bias | Impedance analyzer, LDV, or home-built Michelson [71] with function generator and scope | No (**REQUIRES-STAFF-APPROVAL**) | Spring softening | 28.3 → 25.7 MHz at 0.7 V_PI (nanogap; 24.3 MHz at 0.8 V_PI); ~2.1–2.25 MHz (baseline die is the easier optical target) |
| Beamforming Monte Carlo | Python (adapt `designs/fus_array.py`) | n/a | Turn the measured C0 / C-V-softening spread (plus the bare-twin V_PI spread) into gain and sidelobe loss | Reference: B's 16-element case (12 working, 20% amplitude, 0.1 rad phase) lost ~2.6 dB, peak sidelobe ~−9 dB |

### 6.6 Timeline

| Date | Milestone |
|---|---|
| Mon 10-26 – Tue 10-27 | Write and submit the one-page proposal (Gradescope, one per group) |
| Wed 10-28 | Script the MLA layout: 4 device layers plus the MIM-witness layer (ladder, three gap-matched array copies with radius labels and per-copy dummies, twin cells in SiO2-free wells, MIM, compressive and tensile stress gauges, open/dummy structures, cleave lanes, C-V pads); prepare the §9 questions |
| Thu 10-29 | Instructor meeting (confirm the day on Canvas) |
| Fri 10-30 – Sun 11-01 | Freeze the layout; send staff the supplies and tools list; sign up for TA lab hours (D3) |
| 11-02/03 (session 1) | Only steps that use known-stocked items: L1 Cr/Au/Cr lift-off on ~14 device pieces plus MIM witnesses; a spin curve with whatever thinner is stocked; resist soak coupons. Bank ~7 L1 pieces |
| Thu 11-05 | Proposal presentation (5 + 2 min) with the first spin-curve data |
| 11-06 (session 2) | L2 SiO2 lift-off on run-1 pieces and MIM witnesses, plus the SiO2 soak coupons in the same run |
| Mon 11-09 (session 2b) | The steps that need two more Al depositions after the lift-off: L-MIM dots (thin Al) on the witnesses; stencil Al dots for the pinhole/short test; 1 µm Al for the strip test, Al soak coupons and the L4 mark-visibility check. Alternative: drop L-MIM and evaporate all dots through one stencil in a single run (then update the 5-layer count) |
| Tue 11-10 | MIM breakdown tests set the touchdown policy; fix the split thicknesses (Wed 11-11 is Veterans Day, an MIT holiday; confirm lab access) |
| 11-12/13 (session 3) | Run 1: sacrificial splits, L3, mild bake, 1 µm Al |
| 11-16 – 11-18 (session 4) | Run 1: L4, PAN etch, acetone release, room-temperature IPA dry. Run-2 pieces: L2 + SiO2 lift-off, with the thickness revised from the MIM data |
| 11-18 – 11-23 | Characterize run 1: stiction map (ladder and all array twins), SEM, bare-cell pull-in, selection of each die's gap-matched copy, guarded ramp C-V on it, optional screen of the other copies; choose run-2 changes |
| Tue 11-24 | Update presentation |
| Wed 11-25 or Mon 11-30 (session 5) | Run 2: sacrificial layer and Al on the banked pieces (Thanksgiving is 11-26/27) |
| 12-01 – 12-03 (session 6) | Run 2: L4, etch, release; critical-point drying on half if approved |
| 12-02 – 12-08 | Characterize run 2; data collapse; Monte Carlo; neuro-scaling slide; stretch measurements |
| 12-09 / Thu 12-10 | Freeze results / final presentation |

**Reduced plan.** If staff can offer only ~4 supervised sessions, drop run 2 and spend the time characterizing run 1. Run-1 data alone covers O1–O4 at lower statistics. Ask on 10-29 which supplies are in stock and how many sessions are available (§9).

### 6.7 Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Stiction without critical-point drying | Medium at the design radii (R ≤ 0.19). The R ≤ 0.25 criterion is a heuristic that ignores adhesion after contact, so the critical radii could be off by tens of percent. Sandia measured 0% stiction-free yield after air drying [28]. High beyond the design radii | The ladder deliberately spans the limit, so stiction becomes a measurement; IPA dry only; critical-point drying requested for run 2 |
| Resist left in the 50–100 nm slits | Medium | Mild bake; centre hole (diffusion path ≤ 11 µm on the array copies; the larger ladder cells already set the soak time); long acetone soaks; NMP fallback; check by SEM and C-V |
| Diluted resist has pinholes or non-uniform thickness | Medium | A pinhole, or a particle at least as large as the gap, lets the Al reach the layer below. The result is a post that pins the plate, or a direct Al-to-electrode short in insulator-free cells. Particles and defects also caused breakdown in [5]. Mitigations: the week-1 pre-release short test; ≤0.2 µm filtering and two half-thickness coats; several smaller C-V pads; reflectance calibration; the 100 nm split and the baseline die as fallbacks. C2 is still met by the SiO2. A short found after release cannot be told apart from a stuck cell |
| Resist scum in the anchor rings; dark erosion and bake shrinkage of thin AZ3312 | Medium | Scum left in the anchors dissolves during the multi-hour acetone release, and the Al anchors can then delaminate. Dark erosion in AZ300 MIF and shrinkage during the bake and the Al deposition make the final gap differ from the as-spun witness. Mitigations: overexpose and overdevelop the anchors; anchor-adhesion soak coupon; witnesses through the identical sequence; optional O2 descum (**REQUIRES-STAFF-APPROVAL**) |
| Resist outgasses, blisters or crosslinks under 1 µm Al | Medium | Thermal evaporation; deposit in segments; week-1 strip test (bake temperature trades outgassing against strippability) |
| Insulator breaks down or charges | High at touchdown | Never pull in insulated cells; bias only at ≤0.7 × the selected copy's calibrated V_PI; MIM witness tests first; no anchors over the insulator. Run 2 (banked after L1) can switch to 72–100 nm SiO2 if the MIMs show only 4–6 MV/cm (model). Beyond ~118 nm (e.g., the 139 nm option), no matched array copy stays at ≤40 V (see the run-2 SiO2 row) |
| Arcing, field emission or welding in bare gaps | Medium | 1–10 nA compliance; slow ramps; ≥4 copies of each radius |
| Gap error (±10% gives ±15% in V_PI) | Medium likelihood; impact on O4 now Low–Medium | Each die's measured gap is used in its own fit; report exponents and ratios. Three gap-matched array copies on every die raise P(usable matched array) per die at 50 / 75 / 100 nm from ~0 / 0.74–0.87 / 0.30–0.34 to 0.80–0.88 / 1.00 / 0.88–0.96 (Monte Carlo; heuristic R criterion, 10–15% gap spread; strict criterion 0.7× V_PI ≤ 40 V; under v1's start-at-0.6× policy, v1's 100 nm figure is 0.64–0.74) |
| Applying one copy's bias to another copy (e.g., 27 V on the 11 µm copy of a 50 nm die, whose insulated V_PI is ~19 V) | Low | Metal radius labels, a per-copy bias-limit table, unselected copies screened only at ≤±2 V, and calibrations never transferred between copies |
| More pinhole shorts in bare twins (the wells leave ~32–64 µm² more bare bus under each twin's roof, +12–47% of electrode area, largest on the 7.75 µm copy) | Low | Errs safe: the 1 V short test runs before any ramp. Keep bare buses 1–2 µm wide in channels ≤4 µm, and in-well segments short |
| Guarded C-V unavailable or compromised (only one pA channel, no chuck terminal, or leakage from the measure node to the grounded substrate) | Low | For leakage, first swap force and measure; if that fails, float the chuck on that die only. Otherwise fall back to the single-SMU method (measured node on HI, chuck floating or on that SMU's guard, never on LO) plus dummy subtraction. Record substrate resistivity: depleted-Si coupling can reach ~0.18 pF at 1e15 cm⁻³ |
| Layout workload before the 10-30 – 11-01 freeze (three copies, wells, labels, dummies) | Low | Generate the copies from the parametrized layout script. If time runs out, fall back to v1's single 9.5 µm array on every piece |
| Run-2 SiO2 thickened beyond 100 nm | Low | A 139 nm SiO2 leaves every gap without a usable matched copy at ≤40 V: 0.7 × insulated V_PI is 42.9 / 42.0 / 42.5 V for the 7.75 / 9.5 / 11 µm copies at 50 / 75 / 100 nm. The 11 µm copy on 75 nm reaches 31.3 V but is predicted stuck (R = 0.28). The limit is ~118–125 nm, so keep run-2 SiO2 ≤100 nm (35.6 / 36.4 / 37.9 V) |
| Absolute model error (±35–50%) | High | Treat scaling laws as the primary result; fit D and stress from the ladder |
| I-V setup cannot reach 40 V or cannot resolve pA | Unknown | Ask on 10-29; core results need only nA resolution; request an LCR meter |
| Al step coverage over the 1 µm baseline step | Medium | Reflow-sloped edges; continuity structures; sputtered Al for that die |
| Residual stress unknown (evaporated Al is often tensile; the baseline die is very stress-sensitive) | Medium | Buckled bridges read only compressive stress (≳40–575 MPa with 20–70 µm bridges; longer ones stick by a Tas estimate). Add tensile-reading ring-and-beam or rotating-pointer gauges on every die. Use the bare-cell V_PI ratio between two radii (§6.2) only where the radius span is wide. The worked example in §11 of `nanogap_results.txt` (100 nm, a = 9 vs 12 µm, ~3% per 100 MPa) needs a 57 V pull-in, and so the interlock. Within the ≤40 V, stiction-safe pairs (7/8, 9/10 and 11/12 µm), ±100 MPa moves the ratio by only ~1%, so on nanogap dies rely on the gauges |
| Schedule and Thanksgiving | Medium | Banked substrates; splits processed in parallel; run-1 data alone is enough for 11-24 |
| High-voltage exposure: any test on an instrument range that can source >42 V | Low with procedure | The cited Keithley guidance requires protection whenever the output exceeds 42 V *or* the selected range can source more than 42 V [67]. On common SMUs such as the 2400 and 2450, the range above 20 V is the 200 V range, so even 21–40 V tests may need the enclosed, interlocked fixture. Confirm the instrument model and its interlock behaviour on 10-29. The 11 µm copy's bare twins (38.4 V nominal) sit close to 40 V. With a 10–15% gap spread only ~50% of 100 nm dies keep them at ≤40 V in the Monte Carlo, and the unmodelled release hole (3–18% in V_PI) could push them to ~40–42 V, so plan on the existing interlock item for 100 nm dies. Current compliance is not a safety measure [67]. Set the source to 0 V and turn the output off before touching probes or the fixture; the devices store only ~26 nJ (33 pF at 40 V). Put bleed resistors only on external high-voltage hardware (bias-tee or filter capacitors), never across the device under test: even 1 GΩ draws 30 nA at 30 V, swamping the ~5 pA ramp C-V current and the <1 nA leakage criterion |

### 6.8 Supplies to request by 2026-11-01

- ~18 oxidized-Si pieces (2 × 2 cm): ~14 device pieces (L1 on all; run 1 uses 2 per nanogap split + 1 baseline = 7; bank ~7 for run 2), plus ≥4 for MIM and cleave witnesses; bare-Si reflectance witnesses. If stock is short, use 1 piece per split per run
- AZ3312, AZ300 MIF, PGMEA/EBR thinner, 0.2 µm syringe filters
- Evaporation sources: Cr, Au (a small charge for 25 nm), Al (1 µm × ~7 pieces × 2 runs, plus strip-test and soak witnesses; thin Al for MIM dots)
- SiO2 sputter target or e-beam source
- PAN Al etchant; acetone, IPA, glass dishes; a PTFE carrier for wet transfer
- Probe-station time on the I-V setup: two pA current channels sharing a common LO (two SMUs with preamps, a dual-channel SMU, or an SMU plus a picoammeter), triax cabling, and a vacuum chuck with a terminal (otherwise clean Cu or Al foil clipped to LO); 2–3 SEM sessions; MLA time for L1 once, L2–L4 twice, plus L-MIM (8 layer exposures in all); an evaporator stencil (shadow mask) for the pinhole-test dots
- Elegoo resin
- Needing approval: an enclosed, interlocked probe fixture (possibly required for any test above 20 V, depending on the instrument); optionally NMP remover, critical-point dryer time, LCR meter or impedance analyzer, O2 descum, a solvent-rated oven below 82 °C for IPA drying, and ellipsometer, profilometer or FIB time [72]; stretch: function generator, scope, fast photodiode or LDV, Parylene-C CVD; a high-voltage bias tee (off-the-shelf RF bias tees such as the ZFBT-4R2GW+ are rated to only 30 V DC [73])

### 6.9 Success criteria

- **MVP (on-list tools only):**
  - witness reflectance and SEM show a gap-defining film below 100 nm (backup: SiO2 below 100 nm), and bare-cell pull-in is consistent with that gap
  - stiction mapped on ≥3 gaps
  - bare-cell pull-in measured at ≥2 radii on ≥2 gaps, at ≤40 V
  - MIM breakdown measured
  - at least one gap-matched array per run with ≥6 of 8 elements free of shorts and leakage below 1 nA at 0.7 × its calibrated V_PI
- **Target:**
  - pull-in exponent 1.5 ± 0.3
  - stiction slope 0.5 ± 0.2
  - absolute V_PI within 1.5× of the model, or explained by fitted stress
  - a completed run 2 with a documented correction
  - matched arrays fully characterized on ≥2 of the 3 gaps
  - a quantitative neuro-scaling slide (§6.11)
- **Stretch:** see §6.10.

### 6.10 Stretch goals

- Critical-point-dried pieces, to show the stiction limit disappears. Model: 100 nm cells would reach ~2 MHz immersed at ~11 V if capillary forces were removed.
- Resonance and spring softening (impedance analyzer or Michelson).
- A charging study: track the C-V shift while holding at up to 0.7 × the calibrated V_PI of the die's selected array copy. Use 0.8–0.9× only on designated spare cells, since that sits within the ±15% calibration error of pull-in. This links to pre-charged implant CMUTs [16].
- Interlocked pull-in on the baseline die, extending the gap range 20×.
- A Parylene-sealed die immersed in oil, using only channel-only cells whose lateral release channels end well outside the active cell. Conformal Parylene entering a centre hole would close a 75 nm gap after ~40 nm of growth per surface and pin the plate at its point of maximum deflection; Ergun [3] reports that even LPCVD sealing leaves only ~⅓ of the height under the etch channels. Model the added Parylene mass and stiffness before predicting the sag (1.9 nm without them).
- A contingency die with a QCM-evaporated metal sacrificial layer. It needs electrodes with no exposed Cr (e.g., Ti/Au), no insulator-free cells, and coupons showing that the etchant spares Al, SiO2 and the electrode stack.

### 6.11 Neurotech framing: demonstrated vs extrapolated

| | fUS BMI probe [57] | Butterfly chip [40] | This prototype | Status |
|---|---|---|---|---|
| Transducer type | not stated (conventional linear array) | CMUT-on-CMOS | surface-micromachined CMUT | — |
| Frequency | 15.6 MHz | 1–10 MHz | 28 MHz at 0 V (~26 MHz at 0.7 V_PI), in air; 15–23 MHz estimated immersed, if sealed | Extrapolated |
| Pitch | 100 µm | 208 µm | 100 µm | Demonstrated (geometry) |
| Elements | 128 | 8,960 | 8 | Demonstrated (electrical yield) |
| Gap | n/a (transducer type not stated) | 200 nm | 50–100 nm | Demonstrated (witness reflectance/SEM + pull-in) |
| Drive | Verasonics Vantage 256 | ±25 V on-chip pulsers (DC bias not reported) | DC bias ≤0.7 × the selected copy's calibrated insulated V_PI, estimated from that copy's bare twins (27–32 V nominal across the three copies); no AC drive | Partly |
| Cavity | n/a (transducer type not stated) | sealed | vented | Not shown |
| Medium | dura, in a chronic chamber over a craniectomy | — | air | Not shown |

**What the prototype does NOT show:**
- acoustic pressure, or receive in liquid
- imaging, Doppler or beamforming
- a working seal
- integrated electronics
- biocompatibility or acoustic-output safety
- any effect on neurons

**Neuro-scaling (closing analysis for the final talk):**

| Target | Requirement | What a CMUT needs | Where the prototype stands |
|---|---|---|---|
| fUS-band receive array | 15.6 MHz at 100 µm pitch in macaques [57]; 5–6 MHz for human fUSI through acoustic windows [89,90]; 128+ elements, or 1,024–3,072 for volumetric fUS [91,92] | Sealed 50–200 nm cells (sealed sag 1.9 nm at the design point); tens of volts of bias in the model; per-element electronics | Cell plus an 8-element electrical array |
| Rodent stimulation | 0.18–0.46 MHz, 27–55 kPa [46,47] | ~1–1.75 µm gaps, ~100 V, vacuum seal. Model at 0.5 MHz: g ≈ 1.0–1.3 µm, sealed V_PI 71–103 V | The baseline-die cell (a = 35 µm; Lamb 0.67 MHz if sealed) sits *above* the rodent band. It would fall in the 0.7–0.8 MHz BBB/NHP band only if sealed (then ~357 nm atmospheric sag, V_PI ~77 V with the 50 nm SiO2), and a seal is not available here. As built it is vented and acoustically untested |
| NHP / human stimulation | ~0.5–0.8 MHz, ~0.9–1 MPa *at the focus* [50]. [50] projects 190 kPa at the element surface to ~950 kPa at the focus with 128 elements, so the per-element surface requirement is several times lower | For the §4.1 surface requirement (≤0.17 MPa at 0.5 MHz), conventional mode needs g_eff ≳ 0.5–0.7 µm (stroke ū ≤ 0.077 g_eff) and V_DC·v_ac ≳ 0.4–1.6 × 10⁴ V² (~65–130 V each, for fill factor 1 down to 0.64). That is the ~100 V class of the published devices (model-derived bounds). Delivering 1 MPa at the element surface would instead need g ≳ 2 µm and V_DC·v_ac ≳ 4.5 × 10⁵ V² (~670 V each), which focusing makes unnecessary. In practice: collapse mode [51], or thick plates with AC-only drive plus 128-element focusing [50] | Out of reach |

The 7.75 µm and 11 µm array copies (42.5 and 21.1 MHz in vacuum) are there for yield. They do not bracket 15.6 MHz, and the 9.5 µm / 75 nm array remains the fUS-matched point.

**Wording to avoid:**
- "CMOS-level voltages": the wet-release floor is ~40 V.
- A 15 MHz device "through skull": the work in [57,58] used a craniectomy or a cranial window.
- Calling the device a neural interface or an fUS probe.

### 6.12 Round-2 refinement record (2026-10-26)

**Rule applied.** A change was accepted only if it met all three conditions:
- It is an established fabrication method or CMUT optimization, or has an extremely high likelihood of improving the design.
- It adds no substantial complexity or manufacturing difficulty.
- It adds no uncertain research.

**Process.**
- Four independent generators (process and yield, CMUT design, neurotech relevance, measurement) proposed 13 candidates, and four orchestrator ideas were added. After merging duplicates, 14 distinct ideas remained; 2 were discarded at once and 12 went to verification.
- Each candidate faced three independent skeptics: literature, process integration, and quantitative re-computation with the model. It was accepted only if all three passed.
- The merged v2 was then judged against v1 by a cleanroom lead, a course-staff reviewer and a CMUT/neurotech domain expert. All three voted to accept, and none rated any criterion worse.

**Accepted.** All three are drawing or wiring changes. None adds a layer, session, deposition, chemical, tool or approval item.

| Change | What it fixes | Key numbers (model) | Basis | Fallback |
|---|---|---|---|---|
| Wide SiO2-free L2 wells around every bare test cell (≥30 µm beyond the anchor ring, 50 µm where room allows; shared end-zone wells per array copy) | v1's bare twins sat in a 50 nm-deep SiO2 opening, and any resist planarization makes the bare gap larger, so the bias transfer errs toward pull-in. It also removes v1's zero-margin 0.5 µm L2-to-L1 overlay rule (the published MLA150 front-side overlay is 500 nm [101]) and moves every SiO2 lift-off edge out of the cavities | Residual twin-gap offset ≤0.3 nm, against ~50·p nm in v1 (p = unknown degree of planarization). A +10 nm offset alone would put a "0.7×" bias at 0.85× (75 nm) or 0.92× (50 nm) of the true insulated V_PI | Enclosure and topography design rules for surface micromachining [102] | v1 layout |
| Guarded two-channel ramp C-V: chuck tied at one point to the common Force LO, ramp forced on the top Al, current measured at virtual ground on the bottom pad, 1 V/s | v1 left the substrate path to the fixture ("float or guard the chuck"). An isolated floating chuck adds up to ~1.85 pF (37% of C0) plus a bias-dependent MOS swing | Substrate contribution suppressed to ~0.001–0.02 pF (<0.05 pF) with the piece held flat under vacuum. The bus-to-top overlap (~0.3 pF) is still removed by the dummy | Guarded three-terminal capacitance measurement [103,66]; substrate coupling in CMUT arrays [104] | v1 single-SMU method with dummy subtraction |
| Three gap-matched copies of the 8-element array (a = 7.75 / 9.5 / 11 µm) on every nanogap die; each die's design array is chosen from measured bare-twin pull-in | v1's single 9.5 µm array is predicted stuck on 50 nm dies (R = 0.35), and its twins need 51.5 V on 100 nm dies | Matched copies: R 0.156 / 0.157 / 0.158; bare V_PI 27.4 / 33.5 / 38.4 V; insulated 38.5 / 42.4 / 46.0 V. Expected usable arrays per 6-die run rise from ~2.2–3.2 to ~5.4–5.8 (Monte Carlo using the heuristic R ≤ 0.20 criterion and a 10–15% gap spread; the sign holds for every criterion tested, the size does not) | Sizing cells below the stiction-critical radius, with several radii per chip [13] | v1's single 9.5 µm array |

Copy details are in §6.2. Calibrations are never transferred between copies. Unselected copies are never biased beyond a ±2 V C0 screen, since the lowest bare V_PI of any copy on any die is 13.6 V.

**Erratum found in this round.**
- The ramp method measures the free capacitance C_T = dQ/dV, not the static Q/V. Earlier versions of this report quoted the static values for the ramp C-V.
- At the 75 nm design point, C_T rises +7.8% at 20 V and +22.7% at 0.7 V_PI; the static values are +2.4% and +6.2%. This was independently re-computed.
- The expected C-V signal is therefore ~3.6× larger than stated, and the bias-stepping rule is now "track the model's softening curve", not "stay linear".
- Editorial: step 8's optional double coat now notes the inter-coat soft-bake and a witness check, to reconcile it with step 2's warning that a second coat can redissolve a thin first coat. This is not an adoption of the rejected single-coat candidate.
- Consistency pass: an independent review after the edits found one error from the round-2 output (the run-2 SiO2 limit, now ≤100 nm) and several unchanged v1 sentences, all corrected.

**Rejected, with the deciding reason:**

| Candidate | Why rejected |
|---|---|
| Tert-butanol freeze-sublimation drying on half the pieces, with a longer radius ladder | The method is established, but no published data show it helps at 50–100 nm gaps. It adds a new chemical, heated flammable-solvent handling and new failure modes (3–4 approval items). It also cannot lower the voltages of the 75 nm design point, which are fixed by geometry |
| Grounded continuous top plane, with elements defined by bottom electrodes | Not an established safety convention (common practice biases the top electrode), and its C-V benefit vanishes with the guarded wiring above |
| Reading the C-V curve as a non-destructive pull-in estimator | The erratum part was adopted; the estimator itself lacked literature support |
| Per-die electrical gap gauges from matched bare/insulated cell groups | Substrate coupling scales with cell count, so the de-embedding is biased; it adds uncertainty |
| Deleting the L-MIM layer by stencil-masking all witness dots | A real but small workload saving inside a session that still exists |
| Single-coat sacrificial recipe with 0.1 µm filtration and a pre-spin clean | Benefit too small to measure |
| Dual-end-fed element buses with A/B pads | Its benefit rests on an assumed open-link rate with no evidence behind it |
| Kerfless tiling, 4 cell columns per pitch | No measurable element-level gain, and it depended on the rejected grounded top plane |
| Area-scaled defect monitors and a cell-count yield ladder | Contradicts defect test-structure practice as specified and breaks the routing rule |
| Low-surface-tension final rinse (hexane or a hydrofluoroether) | The critical radius improves only ~5% (hexane) to ~12% (hydrofluoroether), since it scales as γ^-1/4. That is smaller than the effect of ±10% gap error, and it costs a new chemical that needs approval |
| An added 8+8 row-column 2D array | Scope growth with no measurable neurotech gain in this project |

**Honest size of the change.**
- v2 is more robust and its measurements are more trustworthy. The science question, process, gaps, design cell and neurotech framing are unchanged.
- Costs:
  - about 3× the array pads (~32 → ~96) and ~13 mm² of the 400 mm² piece;
  - a few hours of scripted layout before the freeze;
  - ~1 h per die of optional screening;
  - ~+12–47% more bare bus under each bare twin's roof (slightly more twin shorts, caught by the 1 V screen).
- The array gain is in numbers, not in a first array. In the same Monte Carlo, v1 already had P(≥1 usable array per run) ≈ 0.86–1.00. v2 gives ~1.8–2.8× more O4-grade arrays, or ≈1.5–1.7 → 4.2–4.6 if the bare twins must also pull in at ≤40 V. The gain comes mostly from 50 nm dies and from ≤40 V twins on 100 nm dies.
- No step change passed the no-new-uncertainty rule. The two levers that would change the device class remain approval-dependent stretch goals (§6.10): removing capillary forces (critical-point drying) and sealing the cavities for immersion.

---

## 7. Alternative concepts

**A. Risk-first Lecture-4 array (22.0/30: fabrication 8, compliance 8, merit 6).**
- **Design:** vented 0.8 µm sputtered-Al cells over a ~1 µm and an ~80 nm resist gap, 80 nm SiO2 insulator, and an 8-element array at 0.75 mm pitch sized for 0.7–1.06 MHz if sealed.
- **Strengths:** the most buildable concept, and the easiest release chemistry.
- **Why it ranked lower:**
  - Its neuro-band array pulls in at ~121 V. At 40 V it shows only a 1.2% capacitance change, so its transduction cannot be measured with on-list tools.
  - Its headline "~43 kPa at 100 V DC for a sealed cell" is inconsistent with the model: the sealed pull-in of that cell is ~74 V (my recheck; ~72 V by Galerkin). Staying below pull-in gives several times less, e.g. ~15 kPa at 59 V DC plus 30 V AC (my estimate).
  - A stuck cell puts 5 MV/cm across its 80 nm SiO2.
- Its process ideas were grafted into §6.

**B. fUS-Slice (17.5/30: 5, 6, 6.5).**
- **Design:** a 16-element, 100 µm-pitch array with an 80 nm gap set by QCM-evaporated Cr, an SU-8 membrane, and 150 nm of SiO2 in the gap.
- **Strengths:** the best-developed neuro story.
- **Why it ranked lower:**
  - The in-gap dielectric sets a capillary-limited pull-in floor of ~49 V (~44 V with hexane), so no stiction-safe cell can be pulled in at ≤42 V without an interlock.
  - SU-8 exposure on the MLA is unverified.
  - Its Al-plug seal is followed by wet lithography over cavities whose seal is untested.
  - It needs 12 approval items.
- Its spec table, Monte Carlo, witness pieces and Cr contingency were grafted in.

**D. Flexible SU-8/AgNW CMUT on polyimide (9.0/30: 2, 3.5, 3.5).**
- **Precedents:** flexible polymer CMUTs [34], transparent SU-8/AgNW CMUTs [29], and thin flexible-substrate CMUTs [26].
- **Strengths:** the insight that buckling strain is set by geometry rather than material, ε_cr ≈ 14.68(t/a)²/(12(1+ν)).
- **Why it ranked lower:**
  - Pull-in and operation sit at 100–130 V.
  - The headline bending shift is ~0.05% in capacitance at ≤40 V, which is unmeasurable.
  - It needs about 10 cleanroom sessions, with film mounting that may not be allowed in the vacuum tools.
  - The AgNW feature plays no role in the transduction.
  - At adult-head radius the 5.2 mm aperture is effectively flat (~12° phase error).
- Its coupon soaks and etch-front dummy cells were grafted in.

**Overall:** C and A were nearly tied. By lens, fabrication ranked A > C > B > D; compliance C > A > B > D; merit C > B > A > D.

---

## 8. Design-space model

### Validation

| Check | Model | Reference |
|---|---|---|
| Single-mode pull-in vs 6-term Galerkin | Within 1–2% | — |
| Clamped-plate pull-in constants | 0.148 and 0.154 | Wygant 2019 [2] |
| Merbeler 2022, poly-Si cell, 120 nm gap | f_air 6.59 MHz; sealed V_PI 7.4–7.8 V | 6.43 MHz; 7.4 V measured [30] |
| Gerardo 2018, SU-8 cell | f 2.27–2.52 MHz; 1-atm sag 56–68 nm; V_PI 87–99 V | 2.83 MHz; 82 nm; 65 V [15] |
| Immersed centre frequency | Lamb estimate | Measured 1.1–1.5× higher in both devices |

### Immersed designs (Table 1 extract)

Gap is the largest allowed with vented V_PI ≤ 150 V. k_T² = 0.16 at 0.8 V_PI for every row.

| f (MHz) | Stack | t (µm) | a (µm) | Gap (nm) | V_PI vented / sealed (V) | Cells per λ/2 element | Stroke ceiling (kPa, optimistic) |
|---|---|---|---|---|---|---|---|
| 0.5 | Al | 2.50* | 67.8 | 1030 | 150 / 99 | 100 | 262 |
| 0.5 | Au/SU-8 | 3.0 | 51.7 | 1150 | 150 / 89 | 169 | 286 |
| 1 | Al | 1.0 | 29.7 | 842 | 150 / 113 | 121 | 406 |
| 2 | Al | 0.8 | 19.6 | 578 | 150 / 129 | 64 | 536 |
| 5 | Al | 0.6 | 11.3 | 338 | 150 / 140 | 25 | 704 |
| 10 | Al | 0.6 | 8.5 | 200 | 150 / 144 | 9 | 774 |

\*Thicker than is practical in the course. The sealed column reads 2–6% low (see corrections). λ/2 in water is 1500 / 750 / 375 / 150 / 75 µm at 0.5 / 1 / 2 / 5 / 10 MHz.

### Gap scaling on the 5 MHz Al cell (Table 4 extract)

| Gap (nm) | V_PI (V) | Receive current S_i (nA/kPa per element) | Stroke ceiling (kPa) | Capillary ratio R |
|---|---|---|---|---|
| 1000 | 534 | 64 | 1642 | 0.01 |
| 300 | 90 | 116 | 500 | 0.09 |
| 100 | 18.3 | 196 | 173 | 0.83 |
| 50 | 7.1 | 270 | 92 | 3.3 |

### Lowest immersed frequency with sub-100 nm gaps (Table 4b)

Case A: wet release (R ≤ 0.25) and sealed (sag ≤ 0.5 g). Case B: stiction ignored (critical-point drying).

| Gap (nm) | 1 µm Al, case A | 10 µm SU-8, case A | 1 µm Al, case B |
|---|---|---|---|
| 50 | 18.9 MHz @ 39 V | 10.1 MHz @ 39 V | 3.4 MHz @ 6.0 V |
| 75 | 11.7 MHz @ 41 V | 6.4 MHz @ 41 V | 2.6 MHz @ 8.5 V |
| 100 | 8.3 MHz @ 44 V | 4.6 MHz @ 44 V | 2.2 MHz @ 11.2 V |

**Residual stress (Table 5 extract), 1 µm Al cell, a = 29.7 µm:**

| Stress (MPa) | Change in f and V_PI |
|---|---|
| +100 | +37% |
| +500 | +130% |
| 0.9 σ_cr (σ_cr ≈ −111 MPa) | −68% |

For SU-8, the nominal +17 MPa alone raises f by 34%. The root-sum-square shortcut for stressed plates reads 2–5% low.

### Equations used beyond §1

- **Exact tensioned-plate equation:** αJ1(αa)I0(βa) + βJ0(αa)I1(βa) = 0.
- **Buckling:** σ_cr = −14.68·Et²/[12(1−ν²)a²].
- **Stiffness and mass:** k = 192πD/a² + 12πN.
- **Sealed pull-in with 1-atm bias:** V² = 2(k·w_n·g − P·A)·g²/(ε0A·dC_n/dw_n).
- **Receive current:** S_i = 2n/ρc per cell.
- **Capillary-limited floor:** V_PI,min = √(0.888·γ·g_eff³/(R·ε0·g²)), independent of material.
- **Packing:** square grid, 6 µm anchor ring, 10 µm kerf.

### Caveats

- Linear small-deflection theory, axisymmetric first mode only.
- Bulk constants for the metals; sputtered dielectrics assumed (E of SiNx 100–210 GPa; SU-8 2–4 GPa).
- Residual stress set to 0 except for SU-8.
- Dielectric charging, release holes and anchor compliance not modelled.
- Lamb loading treats a single cell in a rigid baffle.
- The capillary criterion is a heuristic.
- The stroke ceiling is optimistic: Merbeler measured about half of it.
- The Lamb constant (0.6689), the buckling constant (14.68) and the plate constant (10.2158) were re-derived numerically, not read from the primary texts.

### Corrections from the independent check

1. **Insulator margin.** Sizing t_ins = V_PI/E_bd at 2 MV/cm leaves zero margin. With a 2× margin the nanogap designs run away to 117–290 V with touchdown first. The ~40 V nanogap result therefore depends on the measured breakdown field. The recommended design uses 50 nm SiO2 and never touches down.
2. **Validity of linear theory.**
   - Thin Cr rows of Table 1 under-predict pull-in by +37% to +163%.
   - The 0.5 MHz Al row of the air table is off by +26%.
   - Designs R1 and R7 are off by only +6–7%.
3. **R1 breaks the model's own screening rules:** β = 9.8, sealed sag/gap = 0.58, R = 0.261.
4. **Capillary margin.** R3–R5 sit exactly at R ≈ 0.25. The 50 nm R6 cell (R = 0.43) will stick.
5. **Insulator-free cells** weld, see 3–6.5 MV/cm on average (up to ~12 MV/cm locally), and ±10% gap error gives ±15% in V_PI.
6. **Report frequencies at operating bias:** 0.86× at 0.8 V_PI, 0.77× at 0.9 V_PI.
7. **Trapped gas in vented cells** raises air frequency +9–13% (R1), +6–8% (R7) and +42–56% (the 0.5 MHz Al air cell). It is negligible (~1%) in a 75 nm gap.
8. **Table 1's sealed column** used a thinner insulator than the vented column (2–6% low).
9. **Unmodelled stress.** Cr rows assume 0 stress even though Cr films are typically highly tensile. R2's 1.00 MHz relies on the +17 MPa SU-8 tension.
10. **Edge stress** reaches 320–390 MPa in sealed thin Cr, and 100–300 MPa in Al at pull-in.
11. **The Lamb factor 0.6689 holds;** the FE mode shape gives 0.654 (<1% in f).
12. **Wet-etch selectivity pairs are unverified.**

---

## 9. Questions for the 2026-10-29 instructor meeting

1. Which I-V instrument (model) will we use? What are its voltage ranges, its interlock behaviour and its lowest current range (we need pA for ramp C-V)? Is an enclosed, interlocked probe fixture available? It is needed above 42 V, and possibly for any test on a range that can exceed 42 V [67]. How many pA current channels share a common LO (for guarded ramp C-V, §6.5), and does the chuck have a terminal that can be tied to the SMU common?
2. Is there an SiO2 sputter target or e-beam source? Can the evaporator deposit 1 µm of Al (thermal or e-beam) and Cr/Au/Cr in one pump-down?
3. May we dilute AZ3312 with PGMEA/EBR thinner? Has anyone spun films thinner than 100 nm on these tools?
4. Is heated NMP-based remover (60–70 °C) allowed as a fallback release?
5. Can the class use a critical-point dryer at MIT.nano for run 2?
6. Are oxidized-Si pieces stocked? Can we cleave our own SEM witnesses, and how much SEM time do we get?
7. What overlay accuracy does the MIT.nano MLA actually achieve? Published MLA150 figures, such as 500 nm front-side at NIST [101], come from other installations. The bare-cell L2-to-L1 rule is gone (§6.12), but L3-to-L1 still matters, and the 7.75 µm array copy has only a 1.16 µm margin (fallback: 5.75 µm electrodes). We need it below 0.15a: ≤0.9 µm for the a = 6 µm cells and ≤1.05 µm at a = 7 µm (1.43 and 1.65 µm hold only on the 9.5 and 11 µm copies). If the MLA cannot guarantee that, we will switch to a fixed 2 µm electrode-to-anchor margin and need ≤~1.5 µm. Can the MLA camera find L1 marks under 1 µm of Al for L4?
8. Can the optical characterization setup measure thin-film reflectance on Si?
9. Can we get access to an LCR meter or impedance analyzer, and a function generator plus oscilloscope?
10. Is PAN Al etchant stocked? Are multi-hour acetone soaks acceptable in the hood? What are the waste and glassware rules for going from PAN (nitric acid) to acetone? Is a solvent-rated (vented, spark-free) oven available for IPA drying below 82 °C? IPA's flash point is ~12 °C, so its vapour in an ordinary lab oven is a fire hazard at any set point. Where may a covered acetone soak sit unattended overnight? Is an evaporator stencil available?
11. How many supervised sessions per week can we have, and is there access during Thanksgiving week? Which of our supplies are in stock for a 11-02/03 first session?
12. Is a vented, air-tested device acceptable, or would staff want an immersion attempt (Parylene)?
13. Is framing this as an fUS-band CMUT building block, with the neurotech link extrapolated by modelling, acceptable?
14. Does a measured scaling law (pull-in and stiction against gap) count as a successful outcome without acoustic output?
15. Is a DIC (Nomarski) or interferometric microscope available, and is an O2 descum possible?

---

## 10. References

1. Brenner K, Ergun AS, Firouzi K, Rasmussen MF, Stedman Q, Khuri-Yakub BT. Advances in capacitive micromachined ultrasonic transducers. *Micromachines* 10(2):152 (2019). doi:10.3390/mi10020152
2. Wygant IO, Khuri-Yakub BT, Kupnik M. Performance parameters and frequency response of CMUTs in transmit, receive, and pulse-echo operation. IEEE IUS (2019). https://ewh.ieee.org/conf/ius/2019/media/files/1094.pdf
3. Ergun AS et al. Capacitive micromachined ultrasonic transducers: fabrication technology. *IEEE TUFFC* 52(12):2242–2258 (2005). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/09/01_Ergun_05.pdf
4. Yaralioglu GG et al. Calculation and measurement of electromechanical coupling coefficient of CMUTs. *IEEE TUFFC* 50(4):449–456 (2003). doi:10.1109/TUFFC.2003.1197968
5. Dew ER et al. Outperforming piezoelectric ultrasonics with high-reliability single-membrane CMUT array elements. *Microsyst. Nanoeng.* 8:59 (2022). doi:10.1038/s41378-022-00392-0
6. Bayram B et al. A new regime for operating CMUTs. *IEEE TUFFC* 50(9):1184–1190 (2003). https://avesis.metu.edu.tr/yayin/6bdabef2-d209-4ecb-871b-0bd6c1aed8d7/a-new-regime-for-operating-capacitive-micromachined-ultrasonic-transducers
7. Park KK, Oralkan Ö, Khuri-Yakub BT. A comparison between conventional and collapse-mode CMUTs in 10-MHz 1-D arrays. *IEEE TUFFC* 60(6):1245–1255 (2013). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/09/01_Park_13.pdf
8. Olcum S et al. Deep-collapse operation of CMUTs. *IEEE TUFFC* 58(11):2475–2483 (2011). https://repository.bilkent.edu.tr/items/a44b9bea-c6a4-4ec8-b8e2-ab04171aa488
9. Köymen H et al. An improved lumped element nonlinear circuit model for a circular CMUT cell. *IEEE TUFFC* 59(8):1791–1799 (2012). doi:10.1109/TUFFC.2012.2383
10. Wang et al. Review on analytical modeling of CMUT collapse voltage and static deflection. *Micromachines* 12(6):714 (2021). https://pmc.ncbi.nlm.nih.gov/articles/PMC8235715/
11. Kupnik M et al. Finite element analysis of fabrication related thermal effects in CMUTs. IEEE Ultrasonics Symp. (2006). https://ultramems-eee.metu.edu.tr/bARIs%20BAYRAM/papersBarisBayram/conference12.pdf
12. Khuri-Yakub BT, Oralkan Ö. CMUTs for medical imaging and therapy. *J. Micromech. Microeng.* 21(5):054004 (2011). https://pmc.ncbi.nlm.nih.gov/articles/PMC3158704
13. Tas NR et al. Stiction in surface micromachining. *J. Micromech. Microeng.* 6:385–397 (1996). https://ris.utwente.nl/ws/files/6645982/stiction.pdf
14. Lamb H. On the vibrations of an elastic plate in contact with water. *Proc. R. Soc. Lond. A* 98:205–216 (1920). doi:10.1098/rspa.1920.0064 (restated in Ayela & Nicu, arXiv:0906.3616)
15. Gerardo CD, Cretu E, Rohling R. Fabrication and testing of polymer-based CMUTs for medical imaging. *Microsyst. Nanoeng.* 4:19 (2018). doi:10.1038/s41378-018-0022-5
16. Saccher M, Kawasaki S, Klootwijk J, van Schaijk R, Dekker R. Modeling and characterization of pre-charged collapse-mode CMUTs. *IEEE OJ-UFFC* 3:14–28 (2023). doi:10.1109/OJUFFC.2023.3240699
17. Yamaner FY et al. High-power CMUTs: design and experimental verification. *IEEE TUFFC* (2012). https://research.sabanciuniv.edu/19147
18. Park KK, Lee H, Kupnik M, Khuri-Yakub BT. Fabrication of CMUTs via local oxidation and direct wafer bonding. *JMEMS* 20(1):95–103 (2011). doi:10.1109/jmems.2010.2093567
19. Yamaner FY, Zhang X, Oralkan Ö. A three-mask process for fabricating vacuum-sealed CMUTs using anodic bonding. *IEEE TUFFC* 62(5):972 (2015). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/09/01_Yamaner_15.pdf
20. Zhang X, Yamaner FY, Oralkan Ö. Fabrication of CMUTs with through-glass-via interconnects. IEEE IUS (2015). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/10/03_Zhang_15.pdf
21. Zhang X. CMUTs on glass substrates for next-generation medical imaging and beyond. NCSU PhD thesis (2018). https://arxiv.org/abs/1811.10386
22. Pirouz A, Degertekin FL. Low temperature CMUT fabrication process with dielectric lift-off membrane support. *J. Micromech. Microeng.* 28:085006 (2018). doi:10.1088/1361-6439/aabe0c
23. Halbach A et al. (imec/KU Leuven). Fabrication and characterization of large-area flexible CMUTs. IEEE conf. paper (2024). https://imec-publications.be/bitstreams/9bf9f64d-e46a-4420-972a-ff19f4a22c7e/download
24. Halbach A et al. Analysis of collapse–snapback phenomena in CMUTs. *Micromachines* 16(2):160 (2025). doi:10.3390/mi16020160
25. Bahette E et al. Progresses in cMUT device fabrication using low temperature processes. *J. Micromech. Microeng.* (2014). https://hal.archives-ouvertes.fr/hal-01831020
26. Lucarini I, Maiolo L, Savoia AS. Fabrication and characterization of CMUTs integrated on ultra-thin and flexible substrates. IEEE IUS (2019). https://ewh.ieee.org/conf/ius/2019/media/files/0701.pdf
27. Tawfik HH et al. Hard-baked photoresist as a sacrificial layer for sub-180 °C surface micromachining. *Micromachines* 9:231 (2018). doi:10.3390/mi9050231
28. Dyck CW et al. (Sandia). Supercritical CO2 solvent extraction from surface-micromachined structures. SPIE (1996). https://www.sandia.gov/app/uploads/sites/145/2021/11/3_41Supercritical.pdf
29. Pang D-C, Chang C-M. Development of a novel transparent flexible CMUT. *Sensors* 17(6):1443 (2017). doi:10.3390/s17061443
30. Merbeler F et al. Ultra-low-voltage CMUTs with increased output pressure due to piston-structured plates. *Micromachines* 13:676 (2022). doi:10.3390/mi13050676
31. Joseph J, Singh SG, Vanjari SRK. Fabrication and characterization of SU-8-based CMUT for airborne applications. *J. Micro/Nanolith. MEMS MOEMS* 17(1):015003 (2018). doi:10.1117/1.JMM.17.1.015003
32. Smith et al. Integration of graphene-polymer heterostructure membranes into a multi-user MEMS fabrication process. Hilton Head (2024). doi:10.31438/TRF.HH2024.73
33. Zhou Q, Zheng J, Onishi S, Crommie MF, Zettl A. Graphene electrostatic microphone and ultrasonic radio. *PNAS* 112(29):8942 (2015). doi:10.1073/pnas.1505800112
34. Omidvar A, Cretu E, Rohling R et al. Flexible PolyCMUTs. *Adv. Mater. Technol.* 8(5):2201316 (2023). doi:10.1002/admt.202201316 (abstract level)
35. Oralkan Ö et al. CMUTs: next-generation arrays for acoustic imaging? *IEEE TUFFC* 49(11):1596–1610 (2002). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/09/04_Oralkan_02.pdf
36. Wygant IO et al. Integration of 2D CMUT arrays with front-end electronics for volumetric ultrasound imaging. *IEEE TUFFC* 55(2):327–342 (2008). doi:10.1109/TUFFC.2008.652
37. Christiansen TL et al. 3-D imaging using row-column-addressed arrays with integrated apodization, Part II. *IEEE TUFFC* 62(5):959–971 (2015). doi:10.1109/TUFFC.2014.006819
38. Grass RS et al. A hand-held 190+190 row-column addressed CMUT probe for volumetric imaging. *IEEE OJ-UFFC* 2:220 (2022). doi:10.1109/OJUFFC.2022.3213013
39. Zahorian J et al. Monolithic CMUT-on-CMOS integration for intravascular ultrasound applications. *IEEE TUFFC* 58(12):2659–2667 (2011). doi:10.1109/tuffc.2011.2128
40. Rothberg JM et al. Ultrasound-on-chip platform for medical imaging, analysis, and collective intelligence. *PNAS* 118(27):e2019339118 (2021). doi:10.1073/pnas.2019339118
41. Yole Group via Edge AI and Vision Alliance. Butterfly Network's iQ3 CMUT sensor: the ins and outs (2024-06-13). https://www.edge-ai-vision.com/2024/06/butterfly-networks-iq3-cmut-sensor-the-ins-and-outs/
42. FDA 510(k) K232808, Butterfly iQ3, decision 2024-01-04 (Innolitics mirror of the FDA database). https://fda.innolitics.com/device/K232808
43. Butterfly Network. JPM investor presentation (2026-01-12). https://s27.q4cdn.com/524696391/files/doc_presentations/2026/2026-BFLY-JPM-Deck-FINAL-1-12-26.pdf
44. Sewify et al. Systematic review of commercially available clinical CMUT-based systems. *Sensors* 25(7):2245 (2025). doi:10.3390/s25072245
45. Fierce Biotech. Exo officially enters handheld ultrasound race (Iris, pMUT) (2023). https://fiercebiotech.com/medtech/exo-officially-enters-handheld-ultrasound-race-launch-ai-powered-iris-system
46. Kim H et al. Miniature ultrasound ring array transducers for transcranial ultrasound neuromodulation of freely-moving small animals. *Brain Stimul.* 12(2):251–255 (2019). doi:10.1016/j.brs.2018.11.007
47. Jo Y et al. General-purpose ultrasound neuromodulation system for chronic, closed-loop preclinical studies in freely behaving rodents. *Adv. Sci.* 9(34):2202345 (2022). doi:10.1002/advs.202202345
48. Seok C, Yamaner FY, Sahin M, Oralkan Ö. A wearable ultrasonic neurostimulator, Part I: a 1D CMUT phased array system. *IEEE TBioCAS* 15(4):692–704 (2021). doi:10.1109/TBCAS.2021.3100458
49. Seok C et al. A wearable ultrasonic neurostimulator, Part II: a 2D CMUT phased array system with a flip-chip bonded ASIC. *IEEE TBioCAS* 15(4):705–718 (2021). doi:10.1109/TBCAS.2021.3105064 (abstract level)
50. Ibn Minhaj T et al. Design, fabrication, and characterization of CMUTs for transcranial, multifocus neurostimulation. *Micromachines* 15(9):1106 (2024). doi:10.3390/mi15091106
51. Kilinc MS et al. A CMUT-based transcranial focused ultrasound platform for blood-brain barrier opening in small animal models. arXiv:2604.22666 (2026, preprint). https://arxiv.org/abs/2604.22666 — Its peer-reviewed predecessor is reportedly Kilinc et al., *IEEE TUFFC* 71(8):1042–1050 (2024) (unverified; seen only in this preprint's reference list).
52. Wong SH et al. CMUTs for therapeutic ultrasound applications. *IEEE TBME* 57(1):114–123 (2010). https://pmc.ncbi.nlm.nih.gov/articles/PMC4029344
53. Menz MD, Oralkan Ö, Khuri-Yakub PT, Baccus SA. Precise neural stimulation in the retina using focused ultrasound. *J. Neurosci.* 33(10):4550–4560 (2013). https://pmc.ncbi.nlm.nih.gov/articles/PMC6704938
54. Tipsawat P et al. 32 element PMUT phased array for neuromodulation. *IEEE OJ-UFFC* (2022). doi:10.1109/OJUFFC.2022.3196823
55. Joshi SV et al. Flexible micromachined ultrasound transducers for biomedical applications. *Microsyst. Nanoeng.* 11:9 (2025). doi:10.1038/s41378-024-00783-5
56. Macé E et al. Functional ultrasound imaging of the brain. *Nat. Methods* 8(8):662–664 (2011). doi:10.1038/nmeth.1641
57. Griggs WS et al. Decoding motor plans using a closed-loop ultrasonic brain–machine interface. *Nat. Neurosci.* 27(1):196–207 (2024). doi:10.1038/s41593-023-01500-7
58. Rabut C et al. Functional ultrasound imaging of human brain activity through an acoustically transparent cranial window. *Sci. Transl. Med.* 16(749):eadj3143 (2024). doi:10.1126/scitranslmed.adj3143
59. Legon W et al. Transcranial focused ultrasound modulates the activity of primary somatosensory cortex in humans. *Nat. Neurosci.* 17(2):322–329 (2014). doi:10.1038/nn.3620
60. US FDA. Marketing clearance of diagnostic ultrasound systems and transducers (guidance, 2023). https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-clearance-diagnostic-ultrasound-systems-and-transducers
61. Butterfly Network. Co-development agreement with Forest Neurotech (press release, 2023-10-24). https://english.butterflynetwork.com/press-releases/co-development-agreement-with-forest-neurotech
62. Arbor Neuroscience (formerly Forest Neurotech), https://www.arborneuroscience.org/ ; Convergent Research profile, https://www.convergentresearch.org/ecosystem/forest (accessed 2026)
63. ARIA. Funding world-leading research into new neurotechnologies (2025). https://aria.org.uk/insights/funding-world-leading-research-into-new-neurotechnologies
64. BioPharmaTrend. OpenAI backs ultrasound-based brain-computer interface startup with $252M seed round (2026). https://www.biopharmatrend.com/news/openai-backs-ultrasound-based-brain-computer-interface-startup-with-252m-seed-round-1470/
65. Digital Health News. Merge Labs and Butterfly Network partner on ultrasound-based BCIs (2026; announcement date inferred). https://www.digitalhealthnews.com/sam-altman-backed-merge-labs-butterfly-network-partner-to-advance-ultrasound-based-brain-computer-interfaces
66. Keithley Application Note 2973. Ramp rate method for quasistatic C-V measurements with the 4200-SCS. https://xdevs.com/doc/Keithley/Appnotes/RampRate%20QuasiCVAppNote1.pdf
67. Tektronix/Keithley FAQ. Current limit on Keithley SMU for safety concerns (42 V threshold). https://www.tek.com/vn/support/faqs/current-limit-on-keithley-smu-for-safety-concerns
68. Zhuang X et al. Trench-isolated CMUT arrays with a supporting frame: characterization and imaging results. IEEE Ultrasonics Symp. (2007). https://research.ece.ncsu.edu/wp-content/uploads/sites/17/2016/10/04_Zhuang_07.pdf
69. Ma B, Firouzi K, Brenner K, Khuri-Yakub BT. Wide bandwidth and low driving voltage vented CMUTs for airborne applications. *IEEE TUFFC* 66(11):1777–1785 (2019). doi:10.1109/TUFFC.2019.2928170
70. Moshrefi A et al. Design and fabrication of multi-frequency and low-quality-factor CMUTs. *Micromachines* 16(7):797 (2025). doi:10.3390/mi16070797
71. Libbrecht KG, Black ED. A basic Michelson laser interferometer for the undergraduate teaching laboratory demonstrating picometer sensitivity. *Am. J. Phys.* 83(5):409–417 (2015). doi:10.1119/1.4901972
72. MIT.nano. Cleanroom metrology. https://nanousers.mit.edu/characterizenano/focus-facilities/cleanroom-metrology ; MIT News, Semilab SE-2000 ellipsometer at MIT.nano (2020). https://news.mit.edu/2020/semilab-se-2000-spectroscopic-ellipsometer-mitnano-0925
73. Mini-Circuits. ZFBT-4R2GW+ bias tee datasheet. https://www.minicircuits.com/pdfs/ZFBT-4R2GW+.pdf
74. BioPharmaWatch. Butterfly Network and Merge Labs announce ultrasound-on-chip licensing partnership for BCI (2026-09-01). https://www.biopharmawatch.com/news/BFLY/butterfly-network-merge-labs-partnership-bci
75. Wang J et al. Transcranial ultrasound stimulation parameters for neurological diseases: a systematic review. *Front. Neurol.* 16:1567482 (2025). doi:10.3389/fneur.2025.1567482
76. Ho H-C, Chen W-S, Hsiao M-Y. Neuromodulation effects of low-intensity transcranial focused ultrasound in humans: a systematic review focusing on motor and sensory functions. *J. NeuroEng. Rehabil.* 22:254 (2025). doi:10.1186/s12984-025-01722-9
77. Aubry J-F et al. ITRUSST consensus on biophysical safety for transcranial ultrasound stimulation. *Brain Stimul.* 18(6):1896–1905 (2025). doi:10.1016/j.brs.2025.10.007 (preprint arXiv:2311.05359)
78. Murphy KR et al. A practical guide to transcranial ultrasonic stimulation from the IFCN-endorsed ITRUSST consortium. arXiv:2407.07646 (2024)
79. Pichardo S, Sin VW, Hynynen K. Multi-frequency characterization of the speed of sound and attenuation coefficient for longitudinal transmission of freshly excised human skulls. *Phys. Med. Biol.* 56(1):219–250 (2011). doi:10.1088/0031-9155/56/1/014
80. Attali D et al. Three-layer model with absorption for conservative estimation of the maximum acoustic transmission coefficient through the human skull for transcranial ultrasound stimulation. *Brain Stimul.* 16(1):48–55 (2023). doi:10.1016/j.brs.2022.12.005
81. Martin E et al. Ultrasound system for precise neuromodulation of human deep brain circuits. *Nat. Commun.* 16:8024 (2025). doi:10.1038/s41467-025-63020-1
82. Chaplin V, Phipps MA, Caskey CF. A random phased-array for MR-guided transcranial ultrasound neuromodulation in non-human primates. *Phys. Med. Biol.* 63(10):105016 (2018). doi:10.1088/1361-6560/aabeff (preprint arXiv:1712.07048)
83. Braun V et al. Transcranial ultrasound stimulation in humans is associated with an auditory confound that can be effectively masked. *Brain Stimul.* 13(6):1527–1534 (2020). doi:10.1016/j.brs.2020.08.014
84. Kim T et al. Effect of low intensity transcranial ultrasound stimulation on neuromodulation in animals and humans: an updated systematic review. *Front. Neurosci.* 15:620863 (2021). doi:10.3389/fnins.2021.620863
85. Ye PP, Brown JR, Pauly KB. Frequency dependence of ultrasound neurostimulation in the mouse brain. *Ultrasound Med. Biol.* 42(7):1512–1530 (2016). doi:10.1016/j.ultrasmedbio.2016.02.012
86. Sato T, Shapiro MG, Tsao DY. Ultrasonic neuromodulation causes widespread cortical activation via an indirect auditory mechanism. *Neuron* 98(5):1031–1041 (2018). doi:10.1016/j.neuron.2018.05.009
87. Guo H et al. Ultrasound produces extensive brain activation via a cochlear pathway. *Neuron* 98(5):1020–1030 (2018). https://experts.umn.edu/en/publications/ultrasound-produces-extensive-brain-activation-via-a-cochlear-pat/
88. Mohammadjavadi M et al. Elimination of peripheral auditory pathway activation does not affect motor responses from ultrasound neuromodulation. *Brain Stimul.* 12(4):901–910 (2019). https://pmc.ncbi.nlm.nih.gov/articles/PMC6592746
89. Ultrafast Doppler for neonatal brain imaging. *NeuroImage* (2018). doi:10.1016/j.neuroimage.2018.04.016; and Functional ultrasound imaging of brain activity in human newborns. *Sci. Transl. Med.* 9:eaah6756 (2017). doi:10.1126/scitranslmed.aah6756
90. Mobile human brain imaging using functional ultrasound. *Sci. Adv.* (2025). doi:10.1126/sciadv.adu9133
91. Non-invasive 4D transcranial functional ultrasound and ultrasound localization microscopy for multimodal imaging of neurovascular response. *Sci. Rep.* 14:30240 (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11697013/
92. Miniaturized four-dimensional functional ultrasound for mapping human brain activity. medRxiv (2025, preprint). doi:10.1101/2025.08.19.25332261
93. Transcranial volumetric imaging using a conformal ultrasound patch. *Nature* 629:810–818 (2024). doi:10.1038/s41586-024-07381-5
94. Kang et al. (incl. Khuri-Yakub BT). Silicon nanocolumn-based disposable and flexible ultrasound patches. *Nat. Commun.* 16:6609 (2025). doi:10.1038/s41467-025-61903-x
95. Quantitative comparison of PZT and CMUT probes for photoacoustic imaging: experimental validation. *Photoacoustics* 8:48–58 (2017). doi:10.1016/j.pacs.2017.09.001
96. Sonogenetic control of mammalian cells using exogenous transient receptor potential A1 channels. *Nat. Commun.* 13:600 (2022). doi:10.1038/s41467-022-28205-y
97. Sonogenetics for precision medicine: from molecular toolkit to clinical translation. *Theranostics* 16(13):7345–7366 (2026). doi:10.7150/thno.134803
98. Younan Y et al. Influence of the pressure field distribution in transcranial ultrasonic neurostimulation. *Med. Phys.* 40(8):082902 (2013). doi:10.1118/1.4812423
99. Pasquinelli C et al. Safety of transcranial focused ultrasound stimulation: a systematic review of the state of knowledge from both human and animal studies. *Brain Stimul.* 12:1367–1380 (2019). doi:10.1016/j.brs.2019.07.024
100. McDannold N, White PJ, Cosgrove R. Predicting skull lesions after clinical transcranial MRI-guided focused ultrasound with acoustic and thermal simulations. arXiv:1912.00089 (2019)
101. NIST CNST NanoFab. Tool: Heidelberg MLA150 maskless aligner (front-side overlay 500 nm, minimum feature 1 µm). https://www.nist.gov/laboratories/tools-instruments/nanofab-tool-heidelberg-mla150-maskless-aligner
102. Cronos/MEMSCAP. MUMPs Design Handbook, Rev. 7.0 (design rules set by lithography resolution and alignment; enclosures; draw features larger than minimum where size allows). https://lwlin.me.berkeley.edu/me119/mumps-rule.pdf
103. Agilent Technologies. Impedance Measurement Handbook, 4th ed., §§2.4.7 and 3.4.2 (guard as circuit common; stray current to the guard bypasses the ammeter). https://xdevs.com/doc/HP/pub/5950-3000.pdf
104. Engholm M, Bouzari H, Jensen JA, Thomsen EV. Capacitive substrate coupling of row-column-addressed 2-D CMUT arrays. Proc. IEEE IUS (2016). https://backend.orbit.dtu.dk/ws/files/125795724/Engholm_et_al_IUS2016.pdf
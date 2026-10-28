# CMUT-NanoFab

**NanoGap CMUT: Sub-100 nm-Gap Capacitive Ultrasonic Transducer Arrays as Building Blocks for Ultrasound Neurotechnology**

Final project for MIT **6.2540 — Nanotechnology: From Atoms to Systems** (Fall 2026).

**Team:** Baxter Barlow · Alan Duan · Rohan Dhillon · Eric Yee

## Overview

A capacitive micromachined ultrasonic transducer (CMUT) is a thin membrane suspended over a small air gap above an electrode. A voltage pulls the membrane toward the electrode, allowing the device to emit ultrasound (electrically driven) and detect it (via changes in capacitance). CMUTs are promising for neurotechnology — ultrasound is used both to image brain activity and to stimulate cortex — because they can be lithographically patterned and integrated with electronics.

The key design choice is the **gap**: a smaller gap lowers the drive voltage but raises the risk of the membrane sticking down during release. We fabricate CMUT cells and small (8-element) arrays with **50, 75, and 100 nm** resist-defined gaps and measure how this trade-off plays out below 100 nm.

### Objectives

| # | Objective |
|---|---|
| O1 | **Fabricate** CMUT cells and 8-element arrays with 50, 75, and 100 nm gaps |
| O2 | **Pull-in voltage** vs. gap and membrane size; compare with a plate model, V<sub>PI</sub> ∝ g<sup>3/2</sup>/a² |
| O3 | **Stiction**: largest membrane that survives release at each gap (predicted ∝ √g) |
| O4 | **Arrays**: uniformity and its effect on steering an ultrasound beam |

## Repository layout

| Path | Contents |
|---|---|
| [`proposal/`](proposal/) | Project proposal (LaTeX source + PDF) |
| `proposal/NanoGap_CMUT_Proposal.*` | Full proposal (two pages) |
| `proposal/proposal_one_page.*` | One-page version (Gradescope submission format) |

## Building the PDFs

Requires a TeX Live installation with `pdflatex`:

```bash
cd proposal
latexmk -pdf NanoGap_CMUT_Proposal.tex
latexmk -pdf proposal_one_page.tex
```

The full proposal uses standard `article` with `tikz`, `booktabs`, `tabularx`, `enumitem`, and `siunitx`; the one-page version additionally uses `extarticle` (extsizes) and `newtx` fonts.

## Milestones (Fall 2026)

- **Oct 27** — Proposal submitted (Gradescope)
- **Nov 5** — Proposal presentation (5 min + Q&A)
- **Nov 24** — Project update presentation
- **Dec 10** — Final presentations

## License

[MIT](LICENSE)

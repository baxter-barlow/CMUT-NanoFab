---
course: "6.2540 — Nanotechnology: From Atoms to Systems (MIT EECS)"
artifact: final-project-requirements
source: "Final Project/Proposal/6.2540-Project Description-2026 (1).pdf"
source_pages: 2
transcribed: 2026-10-26
term: Fall 2026
---

# 6.2540 Final Project — Agent-Interpretable Requirements

This file translates the official final-project description into a structured spec. It exists so an
agent can (a) evaluate a project idea against course constraints, (b) help produce each deliverable
on time, and (c) flag anything needing course-staff approval.

**How to read this file (agent instructions):**
- **MUST** marks a stated requirement; **MAY** marks an explicit allowance. Items under *Observed
  (not required)* are style guidance inferred from examples, never binding.
- The technique/material lists in C3–C4 are **closed lists**: anything outside them is not forbidden,
  but carries the tag `REQUIRES-STAFF-APPROVAL` — surface it to the user and do not treat the plan as
  final until staff have been consulted.
- Group-specific facts (group members, chosen topic, assigned TA) are not in this file — ask the user.
- Verify against the source PDF (path in frontmatter) before relying on an exact quote.

## 1. Task definition

- Work in a group of **4–5 students** to propose and implement a nanotechnology project, based on
  course lectures and lab skills.
- Groups MAY be the same as lab groups, but this is not required; students may reorganize by topic
  of interest.
- The project MAY relate directly to one of the course labs or MAY be a completely new topic.
- The example projects in §6 are suggestions only — any idea satisfying C1–C5 is eligible.

## 2. Hard constraints on project selection (C1–C5)

| ID | Constraint |
|----|-----------|
| C1 | MUST be implementable in **about 4 weeks**. |
| C2 | MUST involve **at least one feature smaller than 100 nm**. Satisfiable three ways: a nanomaterial used in the project, a structure with sub-100 nm dimensions, or something of that scale that you **measure**. |
| C3 | MUST be implementable with the fabrication tools/techniques learned in this course (closed list below). |
| C4 | Materials MUST come from the general material categories used in this course (closed list below). |
| C5 | Characterization uses the imaging/testing tools learned about in this course (list below). |

### C3 — Allowed fabrication techniques
- Lithography (using MLA — maskless aligner)
- Sputtering
- Evaporation
- Spin coating
- Colloidal synthesis
- 3D printing
- Wet etching

> Source note (verbatim rule): "If you think your project might need a technique beyond what you
> have used in class, discuss with the course staff." → tag `REQUIRES-STAFF-APPROVAL`.

### C4 — Allowed material categories
- Colloidal particles, including quantum dots
- Two-dimensional materials
- Organic materials
- Perovskites
- Other common metals, semiconductors, and insulators that can be deposited through sputtering or
  evaporation

> Source note (verbatim rule): "If you think your project might need a material beyond what you have
> used in class, discuss with the course staff." → tag `REQUIRES-STAFF-APPROVAL`.

### C5 — Available characterization tools
- Optical microscope
- Transmission electron microscope (TEM)
- Scanning electron microscope (SEM)
- Electrical characterization setup (current–voltage / I-V measurements)
- Solar simulator setup (for solar-cell characterization)
- Optical characterization setups

## 3. Deliverables and timeline (Fall 2026)

| ID | Due date | Deliverable |
|----|----------|-------------|
| D1 | **2026-10-27** | One-page proposal, submitted through **Gradescope**, **one document per group**. MUST include: proposed idea, objectives, step-by-step approach, and the materials and tools needed to implement the project. |
| D2 | **2026-10-29** | Project discussion meeting with instructors. **One group member** signs up on behalf of the group (sign-up link posted on Canvas). Staff may request a follow-up discussion. ⚠ The guideline says "Wednesday October 29th", but 2026-10-29 is a Thursday — confirm the actual day on Canvas. |
| D3 | by **2026-11-01** | In coordination with course staff: (1) project proposal and approach finalized; (2) course staff informed of the materials, supplies, and tools needed; (3) group signed up with its **assigned TA for lab hours**. |
| D4 | **2026-11-05** | Proposal presentation to class: **5 min + 2 min Q&A**. |
| D5 | **2026-11-24** | Project update presentation: **5 min + 2 min Q&A**. |
| D6 | **2026-12-10** | Final project presentations. Format/details TBD — to be shared by course staff. |

## 4. Proposal spec (detail for D1)

**Required** (from the guideline):
- Length: one page
- Content: proposed idea, objectives, step-by-step approach, materials and tools needed
- Submission: Gradescope, one document per group

**Observed (not required)** — from the two example proposals in `Proposal/`:
- *Proposal Example 2.pdf* (1 page, matches the current length limit): header with member names +
  date, descriptive title, one-sentence aim, one figure of the device architecture, a fabrication
  paragraph mapping each layer to a course technique (e.g., direct-write lithography for electrodes,
  spin coating for the active layer), a characterization paragraph (what is applied, what is
  measured), a stretch goal marked "if time permits", and 2 references.
- *Proposal Example 1.pdf* (2 pages — exceeds the current one-page limit; treat as content/style
  reference only): abstract, materials, manufacturing process, packaging, potential areas of
  concern, testing and verification, references.
- Recommendation: follow Example 2's density; adding a short risks/concerns line (as in Example 1)
  is a cheap way to preempt staff questions.

## 5. Agent validation checklist

Run against any candidate idea or proposal draft; every unchecked box is a finding to report.

- [ ] C1: scoped to ~4 weeks — identify the longest-lead fabrication step and any drying/annealing/
      synthesis wait times
- [ ] C2: names the specific sub-100 nm feature and which form it takes (material / structure /
      measured quantity), and how its scale will be evidenced
- [ ] C3: every fabrication step maps to an allowed technique, or is tagged `REQUIRES-STAFF-APPROVAL`
- [ ] C4: every material maps to an allowed category, or is tagged `REQUIRES-STAFF-APPROVAL`
- [ ] C5: characterization plan names which listed tool answers which question
- [ ] D1: proposal fits on one page and contains all four required content elements
- [ ] Logistics: Gradescope submission (one per group), D2 meeting sign-up, TA lab-hours sign-up (D3)

## 6. Example project ideas (from the guideline; suggestions, not a closed list)

1. Organic solar cell with nanostructured surfaces to enhance efficiency
2. Flexible solar cell (cheap, light-weight, easily deployable)
3. Transparent solar cell — absorbs in IR/UV, transparent in the visible
4. Flexible organic photodetector for wearable medical sensors (e.g., blood oximetry)
5. LED usable for medical imaging through the body
6. LED with enhanced outcoupling
7. High-sensitivity, high-selectivity sensors (chemical, optical, thermal, mechanical, etc.)
8. Wearable electronics
9. Transistors and transistor applications
10. Neuromorphic device (design and build)
11. Self-assembly as a fabrication technique for **< 50 nm** features not easily achievable with
    photolithography
12. Effect of nanostructuring or strain engineering on material properties, and applications
13. Microelectromechanical (MEMS) devices — sensors, actuators, or speakers

## 7. Known unknowns / TBD

- D2 sign-up link: posted on Canvas, not in the PDF
- D6 final presentation format: "details will be shared in the following weeks"
- Grading rubric: not specified in the source document
- Group composition, chosen topic, assigned TA: user-specific — ask the user

## 8. Repository pointers

- Source guideline: `Proposal/6.2540-Project Description-2026 (1).pdf`
- Example proposals: `Proposal/Proposal Example 1.pdf`, `Proposal/Proposal Example 2.pdf`
- Course physics/notation reference: [`../COURSE_REFERENCE.md`](../COURSE_REFERENCE.md)
- CMUT-arrays-for-neurotech research and fit assessment (candidate topic): [`CMUT_NEUROTECH_RESEARCH.md`](CMUT_NEUROTECH_RESEARCH.md), with model code in [`cmut_model/`](cmut_model/)
- Python simulation environment (uv-managed): `../6_2540_environment/grating-lab/`

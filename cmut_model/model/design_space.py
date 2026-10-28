"""CMUT design space for course-depositable materials (6.2540 final project).

Run:  python3 design_space.py   -> prints markdown tables, writes results/*.csv, results/tables.txt
Assumptions (see materials.py for provenance):
  * clamped circular cells, full-coverage electrode facing the gap (electrode-down for dielectric/polymer
    membranes so the membrane dielectric does not add to the electrical gap);
  * bottom electrode Cr + sputtered Al2O3 insulator (eps_r 8); in design tables t_ins = max(50 nm, V_PI/2 MV/cm)
    so the plate can touch down without breakdown;
  * g_eff = g_air + t_ins/eps_ins; V_PI from the single-mode Wygant model (within ~1-2 % of the 6-term
    Galerkin, see validate.py); "sealed" = vacuum cavity loaded by 1 atm;
  * immersed frequency = Lamb fluid-loaded single-cell resonance (validate.py: measured immersed array
    centre frequencies were 1.1-1.5x this estimate);
  * 2-D array element = lambda/2 x lambda/2 in the medium, 10 um inter-element kerf, 6 um anchor ring
    between cells, square cell packing;
  * capillary (stiction) ratio R = (2 gamma_IPA / g) / (64 D g / a^4 + tension): pressure from an IPA
    meniscus filling the gap vs. pressure that brings the centre into contact. Piston-analog collapse
    threshold R > 0.25 (spring vs. 1/(g-w) force); R < 0.25 treated as safe for wet release.
"""
from __future__ import annotations

import csv
import json
import math
import os

import numpy as np
from scipy import optimize

import cmut
from materials import (AIR, E_BD_INSULATOR, EPS0, GAMMA_IPA, GRAPHENE, MATERIALS as M, P_ATM, WATER)

um, nm, MHz = 1e-6, 1e-9, 1e6
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

V_MAX = 150.0
BETA_MAX = 8.0          # limit fluid mass loading (f_vac/f_water <= 3); Lamb is least reliable when beta >> 1
W_ATM_MAX = 0.5         # immersed cells must be sealed: centre deflection under 1 atm <= 0.5 g_air
R_SAFE = 0.25           # capillary collapse threshold (piston analog)
G_MIN, G_MAX = 50 * nm, 2000 * nm
A_MIN, A_MAX = 5 * um, 100 * um
EPS_INS = M["Al2O3"].eps_r
POST, KERF = 6 * um, 10 * um
CP_PARASITIC = 10e-12   # ASSUMED pad + short-cable parasitic per element for the voltage-readout column
TARGETS = [0.5, 1.0, 2.0, 5.0, 10.0]
T_BASE = [0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
T_SU8 = [0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
T_PAR = [0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

STACKS = {
    # name: (layers(t_struct) gap-side first, thickness list [um], practical max [um], note)
    "Al": (lambda t: [(M["Al"], t)], T_BASE, 1.0, "Al is membrane and top electrode"),
    "Cr": (lambda t: [(M["Cr"], t)], T_BASE[:9], 0.5, "Cr membrane; high tensile stress likely"),
    "Au/SU-8": (lambda t: [(M["Au"], 50 * nm), (M["SU8"], t)], T_SU8, 10.0, "50 nm Au under spin-coated SU-8"),
    "Al/ParyC": (lambda t: [(M["Al"], 100 * nm), (M["ParyC"], t)], T_PAR, 5.0, "100 nm Al under Parylene C (CVD: REQUIRES-STAFF-APPROVAL)"),
    "Cr/SiN": (lambda t: [(M["Cr"], 50 * nm), (M["SiN"], t)], T_BASE, 1.0, "50 nm Cr under sputtered SiNx"),
    "Cr/Al2O3": (lambda t: [(M["Cr"], 50 * nm), (M["Al2O3"], t)], T_BASE, 1.0, "50 nm Cr under sputtered Al2O3"),
}


# ----------------------------------------------------------------------------------------------
def medium(name):
    return WATER if name == "water" else AIR


def f_in(props, a, med):
    fv = cmut.f_exact(props["D"], props["m"], props["N"], a)
    return cmut.f_fluid(fv, medium(med)["rho"], a, props["m"]), fv


def radius_for(props, f_target, med):
    def g(a):
        return f_in(props, a, med)[0] - f_target
    lo, hi = 1 * um, 200 * um
    if np.sign(g(lo)) == np.sign(g(hi)):
        return float("nan")
    return optimize.brentq(g, lo, hi, xtol=1e-10)


def packing(a, f, med):
    p = medium(med)["c"] / f / 2
    n = math.floor((p - KERF + POST) / (2 * a + POST))
    ff = n ** 2 * math.pi * a ** 2 / p ** 2 if n > 0 else 0.0
    return p, n, ff


def ff_dense(a):
    return math.pi * a ** 2 / (2 * a + POST) ** 2


def tins_for(V):
    return max(50 * nm, V / E_BD_INSULATOR)


def cell(props, a, g_air, V_target=None, Pb=0.0, t_ins_fixed=None):
    """Single-mode cell; insulator either fixed or self-consistent with V_PI (no breakdown at contact)."""
    if t_ins_fixed is not None:
        sm = cmut.SingleMode(props["D"], props["m"], props["N"], a, g_air, g_air + t_ins_fixed / EPS_INS, P_bias=Pb)
        return sm, t_ins_fixed
    t_ins = tins_for(V_target if V_target else 50.0)
    for _ in range(8):
        sm = cmut.SingleMode(props["D"], props["m"], props["N"], a, g_air, g_air + t_ins / EPS_INS, P_bias=Pb)
        t_new = tins_for(sm.V_PI)
        if abs(t_new - t_ins) < 1 * nm:
            break
        t_ins = t_new
    return sm, t_ins


def max_gap(props, a):
    """Largest air gap in [50 nm, 2 um] with vented V_PI <= 150 V (t_ins sized for 150 V)."""
    k, A = cmut.k_avg(props["D"], props["N"], a), math.pi * a ** 2
    g_eff = (V_MAX ** 2 * EPS0 * A / (0.1483 * k)) ** (1 / 3)
    g_air = g_eff - tins_for(V_MAX) / EPS_INS
    if g_air < G_MIN:
        return float("nan")
    return min(g_air, G_MAX)


def w_atm_center(props, a):
    """Centre deflection of a vacuum-sealed cell under 1 atm (single-mode, includes tension)."""
    k = cmut.k_avg(props["D"], props["N"], a)
    return 3 * P_ATM * math.pi * a ** 2 / k


def stiction_ratio_props(props, a, g_air):
    k = cmut.k_avg(props["D"], props["N"], a)
    return (2 * GAMMA_IPA / g_air) / (k * (g_air / 3) / (math.pi * a ** 2))


def evaluate(stack, t, a, g_air, f_target, med):
    layers, _, tmax, _ = STACKS[stack]
    props = cmut.stack_props(layers(t))
    fm, fv = f_in(props, a, med)
    sm, t_ins = cell(props, a, g_air)
    smS, _ = cell(props, a, g_air, V_target=sm.V_PI, Pb=P_ATM)
    p, n, ff = packing(a, f_target * MHz, med)
    ff_used = ff if med == "water" else ff_dense(a)
    rho_c = medium(med)["rho"] * medium(med)["c"]
    p_ceil = ff_used * rho_c * 2 * math.pi * fm * 0.5 * sm.wn_PI * sm.g
    ss = sm.small_signal(0.8 * sm.V_PI, rho_f=medium(med)["rho"], c_f=medium(med)["c"])
    sm100, _ = cell(props, a, 100 * nm)
    sm50, _ = cell(props, a, 50 * nm)
    sig_cr = -cmut.N_buckle(props["D"], a) / props["t"]
    return dict(stack=stack, medium=med, f_target=f_target, t_struct_um=t / um, t_total_um=props["t"] / um,
                a_um=a / um, f_vac_MHz=fv / MHz, f_med_MHz=fm / MHz, beta=cmut.lamb_beta(medium(med)["rho"], a, props["m"]),
                g_air_nm=g_air / nm, t_ins_nm=t_ins / nm, g_eff_nm=sm.g / nm, V_PI=sm.V_PI, V_PI_sealed=smS.V_PI,
                sealed_collapsed=smS.collapsed_by_bias, w_atm_over_g=w_atm_center(props, a) / g_air,
                touchdown=sm.touchdown, pitch_um=p / um, cells_side=n, FF=ff, p_ceil_kPa=p_ceil / 1e3,
                n_uNperV=ss["n"] * 1e6, k2=ss["k2"], S_i_pA_per_Pa=ss["S_i"] * 1e12, C0_fF=ss["C"] * 1e15,
                V_PI_g100=sm100.V_PI, V_PI_g50=sm50.V_PI, sigma_cr_MPa=sig_cr / 1e6,
                stiction=stiction_ratio_props(props, a, g_air), practical=t <= tmax * um + 1e-12,
                D=props["D"], m=props["m"], N=props["N"])


def best_design(stack, f_target, med):
    """water: sealed-cell constraints (beta <= 8, 1-atm centre deflection <= 0.5 g, >= 1 cell per lambda/2
    element), then maximise the stroke-limited output p_ceil among course-practical thicknesses.
    air: vented bench device; thickest course-practical plate that hits f with a <= 100 um (robustness),
    then the largest gap with V_PI <= 150 V."""
    layers, tlist, _, _ = STACKS[stack]
    cands = []
    for t_um in tlist:
        t = t_um * um
        props = cmut.stack_props(layers(t))
        a = radius_for(props, f_target * MHz, med)
        if not (A_MIN <= a <= A_MAX):
            continue
        g = max_gap(props, a)
        if not np.isfinite(g):
            continue
        if med == "water":
            p, n, ff = packing(a, f_target * MHz, med)
            if n < 1 or cmut.lamb_beta(WATER["rho"], a, props["m"]) > BETA_MAX:
                continue
            if w_atm_center(props, a) > W_ATM_MAX * g:
                continue
        cands.append(evaluate(stack, t, a, g, f_target, med))
    if not cands:
        return None
    pract = [c for c in cands if c["practical"]]
    pool = pract if pract else cands
    if med == "water":
        return max(pool, key=lambda c: c["p_ceil_kPa"])
    return max(pool, key=lambda c: c["t_struct_um"])


# ----------------------------------------------------------------------------------------------
def fmt(x, nd=1):
    if isinstance(x, str):
        return x
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "-"
    return f"{x:.{nd}f}"


def design_tables():
    rows_all, lines = {}, {}
    for med in ("water", "air"):
        pc = "p_ceil kPa (FF of lambda/2 element)" if med == "water" else "p_ceil Pa (dense-packed FF)"
        L = [f"| f target MHz | stack | t_struct (total) um | a um | f_vac MHz | f_{med} MHz | Lamb beta | g_air nm (max @V_PI<=150 V) | t_ins nm | "
             f"V_PI vented V | V_PI sealed V | w_atm,centre/g | cells per lambda/2 elem | FF | {pc} | V_PI if g=100 nm | V_PI if g=50 nm | "
             f"sigma_cr MPa | capillary ratio R | flags |", "|" + "---|" * 20]
        rows = []
        for f in TARGETS:
            for st in STACKS:
                d = best_design(st, f, med)
                if d is None:
                    why = "a 5-100 um, t list, V_PI<=150 V" + (", >=1 cell/elem, beta<=8, sealed w_atm<=0.5 g" if med == "water" else "")
                    L.append(f"| {f} | {st} | no design meets {why} |" + " |" * 17)
                    continue
                rows.append(d)
                flags = []
                if not d["practical"]:
                    flags.append("t > course-practical")
                if d["sealed_collapsed"]:
                    flags.append("must be vented (1 atm collapses a sealed cell)")
                if d["touchdown"]:
                    flags.append("touchdown")
                if d["stiction"] > R_SAFE:
                    flags.append("wet-release stiction risk")
                pcv = d["p_ceil_kPa"] if med == "water" else d["p_ceil_kPa"] * 1e3
                L.append(f"| {f} | {st} | {fmt(d['t_struct_um'],2)} ({fmt(d['t_total_um'],2)}) | {fmt(d['a_um'])} | {fmt(d['f_vac_MHz'],2)} | "
                         f"{fmt(d['f_med_MHz'],2)} | {fmt(d['beta'],1)} | {fmt(d['g_air_nm'],0)} | {fmt(d['t_ins_nm'],0)} | {fmt(d['V_PI'],0)} | "
                         f"{'collapsed' if d['sealed_collapsed'] else fmt(d['V_PI_sealed'],0)} | {fmt(d['w_atm_over_g'],2)} | "
                         f"{d['cells_side']**2} | {fmt(d['FF'],2)} | {fmt(pcv,0)} | {fmt(d['V_PI_g100'],1)} | "
                         f"{fmt(d['V_PI_g50'],1)} | {fmt(d['sigma_cr_MPa'],0)} | {fmt(d['stiction'],2)} | {'; '.join(flags)} |")
        lines[med], rows_all[med] = L, rows
        with open(os.path.join(OUT, f"designs_{med}.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return lines, rows_all


def pitch_table():
    diam = [10, 20, 30, 40, 60, 80, 120, 160, 200]
    L = ["| f MHz | lambda water um | lambda/2 water um | lambda/2 air um | " + " | ".join(f"2a={d} um" for d in diam) + " |",
         "|" + "---|" * (4 + len(diam))]
    for f in TARGETS:
        lam = WATER["c"] / (f * MHz)
        cells = []
        for d in diam:
            p, n, ff = packing(d / 2 * um, f * MHz, "water")
            cells.append(f"{n*n} ({ff:.2f})" if n > 0 else "0 (cell > pitch)")
        L.append(f"| {f} | {lam/um:.0f} | {lam/2/um:.0f} | {AIR['c']/(f*MHz)/2/um:.1f} | " + " | ".join(cells) + " |")
    return L


def nanogap_table(ref_rows):
    gaps = [1000, 500, 300, 200, 100, 75, 50]
    t_ins = 50 * nm
    L = ["Fixed 50 nm Al2O3 insulator (g_eff = g + 6 nm) so that only the gap changes; 't_ins for contact' = V_PI / 2 MV/cm "
         "is the insulator needed if the plate may touch down. V_op = 0.8 V_PI unless noted."]
    for ref in ref_rows:
        layers = STACKS[ref["stack"]][0]
        props = cmut.stack_props(layers(ref["t_struct_um"] * um))
        a = ref["a_um"] * um
        f = ref["f_med_MHz"] * MHz
        p, n, ff = packing(a, ref["f_target"] * MHz, "water")
        N = n * n
        L.append(f"\n**Reference cell: {ref['stack']} t = {ref['t_struct_um']:.2f} um, a = {ref['a_um']:.1f} um, f_water(Lamb) = "
                 f"{ref['f_med_MHz']:.2f} MHz, {N} cells per lambda/2 element (FF {ff:.2f})**\n")
        L += ["| g_air nm | g_eff nm | V_PI vented V | V_PI sealed V | w_atm,centre/g | t_ins for contact nm | C0/cell fF | E_gap at V_op V/um | "
              "n at V_op uN/V | k_T^2 | S_i/element nA/kPa (in-band, TIA) | S_v/element uV/Pa (Cp=10 pF) | S_oc static/cell uV/Pa (no Cp) | "
              "n at fixed 10 V uN/V | p_ceil kPa | capillary ratio R |", "|" + "---|" * 16]
        for g in gaps:
            sm, _ = cell(props, a, g * nm, t_ins_fixed=t_ins)
            smS, _ = cell(props, a, g * nm, Pb=P_ATM, t_ins_fixed=t_ins)
            ss = sm.small_signal(0.8 * sm.V_PI)
            n10 = sm.small_signal(10.0)["n"] * 1e6 if sm.V_PI > 10.0 else float("nan")
            Si_el = ss["S_i"] * N
            Sv_el = Si_el / (2 * math.pi * f * (N * ss["C"] + CP_PARASITIC))
            p_ceil = ff * WATER["rho"] * WATER["c"] * 2 * math.pi * f * 0.5 * sm.wn_PI * sm.g
            L.append(f"| {g} | {sm.g/nm:.0f} | {sm.V_PI:.1f} | {'collapsed' if smS.collapsed_by_bias else f'{smS.V_PI:.1f}'} | "
                     f"{w_atm_center(props, a)/(g*nm):.2f} | {tins_for(sm.V_PI)/nm:.0f} | {ss['C']*1e15:.1f} | {ss['E_gap']/1e6:.0f} | "
                     f"{ss['n']*1e6:.3f} | {ss['k2']:.2f} | {Si_el*1e12:.0f} | {Sv_el*1e6:.2f} | {ss['S_oc']*1e6:.1f} | {fmt(n10,3)} | "
                     f"{p_ceil/1e3:.0f} | {stiction_ratio_props(props, a, g*nm):.2f} |")
    return L


def nanogap_feasibility():
    """Lowest immersed frequency reachable with a sub-100 nm gap under: beta<=8, a 5-100 um, practical t,
    sealed (1 atm centre deflection <= 0.5 g); case A also wet-release safe (R <= 0.25)."""
    L = ["| g_air nm | stack | A: lowest f_water MHz (sealed + R<=0.25) | A: t um / a um | A: V_PI vented / sealed V | A: cells per lambda/2 | "
         "B: lowest f_water MHz (sealed, stiction ignored) | B: t um / a um | B: V_PI vented / sealed V |", "|" + "---|" * 9]
    rows = []
    for g_nm in (50, 75, 100):
        g = g_nm * nm
        for st, (layers, tlist, tmax, _) in STACKS.items():
            res = {}
            for case, rmax in (("A", R_SAFE), ("B", np.inf)):
                best = None
                for t_um in tlist:
                    if t_um > tmax + 1e-9:
                        continue
                    props = cmut.stack_props(layers(t_um * um))

                    def ok(a):
                        return (w_atm_center(props, a) <= W_ATM_MAX * g and stiction_ratio_props(props, a, g) <= rmax
                                and cmut.lamb_beta(WATER["rho"], a, props["m"]) <= BETA_MAX)
                    if not ok(A_MIN):
                        continue
                    if ok(A_MAX):
                        a_hi = A_MAX
                    else:
                        a_hi = optimize.brentq(lambda a: 1.0 if ok(a) else -1.0, A_MIN, A_MAX, xtol=1e-9)
                        while not ok(a_hi):
                            a_hi *= 0.9999
                    fw, fv = f_in(props, a_hi, "water")
                    if best is None or fw < best[0]:
                        best = (fw, t_um, a_hi, props)
                if best is None:
                    res[case] = None
                    continue
                fw, t_um, a, props = best
                sm, _ = cell(props, a, g)
                smS, _ = cell(props, a, g, V_target=sm.V_PI, Pb=P_ATM)
                p, n, ff = packing(a, fw, "water")
                res[case] = (fw, t_um, a, sm.V_PI, smS.V_PI, n * n)
                rows.append(dict(g_nm=g_nm, stack=st, case=case, f_water_MHz=fw / MHz, t_um=t_um, a_um=a / um,
                                 V_PI=sm.V_PI, V_PI_sealed=smS.V_PI, cells=n * n))

            def cellA(r):
                return "none" if r is None else f"{r[0]/MHz:.2f}"
            A, B = res.get("A"), res.get("B")
            L.append(f"| {g_nm} | {st} | {cellA(A)} | {'-' if A is None else f'{A[1]:.2f} / {A[2]/um:.1f}'} | "
                     f"{'-' if A is None else f'{A[3]:.1f} / {A[4]:.1f}'} | {'-' if A is None else A[5]} | {cellA(B)} | "
                     f"{'-' if B is None else f'{B[1]:.2f} / {B[2]/um:.1f}'} | {'-' if B is None else f'{B[3]:.1f} / {B[4]:.1f}'} |")
    return L, rows


def stress_table(ref_rows):
    L = ["| design | sigma MPa | N a^2/D | f_vac exact MHz | f_rss MHz | f_water MHz | V_PI (Galerkin, vented) V | V_PI change vs sigma=0 |",
         "|---|---|---|---|---|---|---|---|"]
    for ref in ref_rows:
        layers = STACKS[ref["stack"]][0]
        t, a = ref["t_struct_um"] * um, ref["a_um"] * um
        g, g_eff = ref["g_air_nm"] * nm, ref["g_eff_nm"] * nm
        base = cmut.stack_props(layers(t), sigma_override=0.0)
        nominal = cmut.stack_props(layers(t))["N"] / base["t"] / 1e6
        scr = -cmut.N_buckle(base["D"], a) / base["t"] / 1e6
        sigmas = [None, -100, -50, 0, 50, 100, 200, 500]
        if abs(nominal) > 1e-6:
            sigmas.insert(4, round(nominal, 1))
        name = f"{ref['stack']} t={t/um:.2f} um a={a/um:.1f} um g={g/nm:.0f} nm"
        rp0 = cmut.RitzPlate(a, [(1.0, base["D"], base["m"], 0.0, base["nu"])])
        v0 = rp0.pullin(g, g_eff)["V_PI"]
        for s in sigmas:
            s_val = 0.9 * scr if s is None else float(s)
            if s_val <= scr:
                L.append(f"| {name} | {s_val:.0f} | - | buckled (sigma_cr = {scr:.0f} MPa) | - | - | - | - |")
                continue
            props = cmut.stack_props(layers(t), sigma_override=s_val * 1e6)
            fv = cmut.f_exact(props["D"], props["m"], props["N"], a)
            frss = cmut.f_rss(props["D"], props["m"], props["N"], a) if props["N"] >= 0 else float("nan")
            fw = cmut.f_fluid(fv, WATER["rho"], a, props["m"])
            rp = cmut.RitzPlate(a, [(1.0, props["D"], props["m"], props["N"], props["nu"])])
            v = rp.pullin(g, g_eff)["V_PI"]
            tag = " (0.9 sigma_cr)" if s is None else (" (nominal)" if abs(s_val - nominal) < 0.05 and nominal != 0 else "")
            L.append(f"| {name} | {s_val:.0f}{tag} | {props['N']*a**2/props['D']:.1f} | {fv/MHz:.2f} | {fmt(frss/MHz, 2)} | "
                     f"{fw/MHz:.2f} | {v:.1f} | {(v/v0-1)*100:+.0f}% |")
    return L


def graphene_table():
    L = ["| layers | tension T N/m | a um | f_vac MHz | f_water MHz (Lamb, indicative) | V_PI vented V (g=100 nm) | sealed: w_atm,centre um (gap 0.1 um) | strain % |",
         "|---|---|---|---|---|---|---|---|"]
    for nl in (1, 5):
        m = nl * GRAPHENE["t_layer"] * GRAPHENE["rho"]
        for T in (0.01, 0.1, 1.0):
            for a_um in (2, 5, 10):
                a, g = a_um * um, 100 * nm
                fv = cmut.f_membrane(T, m, a)
                fw = cmut.J0Z / (2 * math.pi * a) * math.sqrt(T / (m + cmut.LAMB_GAMMA * WATER["rho"] * a))
                sm = cmut.SingleMode(0.0, m, T, a, g, g, shape="membrane")
                w_atm = P_ATM * a ** 2 / (4 * T)
                L.append(f"| {nl} | {T} | {a_um} | {fv/MHz:.2f} | {fw/MHz:.3f} | {sm.V_PI:.2f} | {w_atm/um:.1f} | {T/(nl*GRAPHENE['E2D'])*100:.3f} |")
    return L


RECS = [
    dict(name="R1 Lecture-4 analog, resist gap, ~0.5 MHz immersed", stack="Al", t=1.0, f=0.5, g=[1000],
         gap_process="spin-coated AZ3312 sacrificial (~1 um), anchors opened by MLA; solvent release, IPA dry",
         notes="Pset-4 cantilever flow made circular; the same die resonates near 1.6 MHz in air for bench tests; vent for air, seal for water"),
    dict(name="R2 SU-8 polyCMUT, ~1 MHz immersed", stack="Au/SU-8", t=4.0, f=1.0, g=[500],
         gap_process="500 nm sputtered Cr (or Cu) sacrificial, wet-etched through lateral channels",
         notes="Gerardo-2018-like but spin-coat + evaporation only; SU-8 tensile stress raises f (Table 5); seal channel mouths with spin-coated SU-8"),
    dict(name="R3 Al nanogap 100 nm, ~8 MHz immersed (wet-release safe)", stack="Al", t=1.0, a=12.3, g=[100],
         gap_process="100 nm sputtered sacrificial metal (gap = sputtered thickness)",
         notes="largest-radius 1 um Al cell that survives IPA drying (R<=0.25) and 1 atm sealing at g=100 nm"),
    dict(name="R4 Al nanogap 75 nm, ~12 MHz immersed (wet-release safe)", stack="Al", t=1.0, a=10.7, g=[75],
         gap_process="75 nm sputtered sacrificial metal",
         notes="true sub-100 nm gap (C2); verify gap by SEM of a cleaved witness step and by V_PI"),
    dict(name="R5 Cr/SiNx nanogap 100 nm, ~7.5 MHz immersed", stack="Cr/SiN", t=1.0, a=15.5, g=[100],
         gap_process="100 nm sputtered Al sacrificial removed in Al etchant; SiNx membrane over 50 nm Cr",
         notes="needs low-stress/tensile SiNx: compressive films beyond sigma_cr buckle"),
    dict(name="R6 gap-scaling test die (insulator-free pull-in cells)", stack="Al", t=1.0, a=10.0, g=[200, 100, 50], t_ins_fixed=0.0,
         gap_process="same mask, sacrificial 50/100/200 nm on separate pieces",
         notes="pull-in shorts the electrodes -> current step in the I-V sweep (use compliance); V_PI ~ g^1.5 extracts the gap"),
    dict(name="R7 air-coupled bench device, ~2 MHz in air", stack="Al", t=1.0, a=35.0, g=[1000], med="air",
         gap_process="AZ3312 resist sacrificial (~1 um), vented (no seal)",
         notes="same process and mask as R1 (smaller radius); resonance measurable in air without sealing"),
    dict(name="R8 Parylene-C variant, ~1 MHz immersed", stack="Al/ParyC", t=5.0, f=1.0, g=[500],
         gap_process="500 nm sacrificial metal; Parylene CVD also seals release holes",
         notes="REQUIRES-STAFF-APPROVAL (Parylene CVD)"),
]


def recommended():
    L = ["| design | stack (gap side first) | a um | g_air nm | t_ins nm | f_vac/air MHz (Ritz) | f_water MHz (Lamb) | expected immersed centre MHz | "
         "V_PI vented V (Galerkin) | V_PI sealed V (Galerkin) | w_atm,centre nm | sigma_cr MPa | cells per lambda/2 elem (FF) | capillary ratio R | gap process | notes |",
         "|" + "---|" * 16]
    out_rows = []
    for r in RECS:
        med = r.get("med", "water")
        layers = STACKS[r["stack"]][0]
        props = cmut.stack_props(layers(r["t"] * um))
        a = radius_for(props, r["f"] * MHz, med) if r.get("f") else r["a"] * um
        for gnm in r["g"]:
            g = gnm * nm
            sm, t_ins = cell(props, a, g, t_ins_fixed=r.get("t_ins_fixed"))
            g_eff = g + t_ins / EPS_INS
            rp = cmut.RitzPlate(a, [(1.0, props["D"], props["m"], props["N"], props["nu"])])
            fv, _ = rp.freq()
            fw = cmut.f_fluid(fv, WATER["rho"], a, props["m"])
            pv = rp.pullin(g, g_eff)
            ps = rp.pullin(g, g_eff, P_bias=P_ATM)
            w_atm = rp.static_center_deflection(P_ATM)
            f_pack = fw if med == "water" else fv
            p, n, ff = packing(a, f_pack, med)
            scr = -cmut.N_buckle(props["D"], a) / props["t"] / 1e6
            st = "collapsed by 1 atm" if ps["collapsed_by_bias"] else f"{ps['V_PI']:.1f}"
            fw_s = f"{fw/MHz:.2f}" if med == "water" else "-"
            likely = f"{fw/MHz:.2f}-{1.5*fw/MHz:.2f}" if med == "water" else f"air: {fv/MHz:.2f}"
            stack_desc = " / ".join(f"{mat.name.split(' (')[0]} {tt/um:.2f} um" for mat, tt in layers(r["t"] * um))
            R = stiction_ratio_props(props, a, g)
            label = r["name"] + (f" [g={gnm} nm]" if len(r["g"]) > 1 else "")
            L.append(f"| {label} | {stack_desc} | {a/um:.1f} | {gnm} | {t_ins/nm:.0f} | {fv/MHz:.2f} | {fw_s} | {likely} | "
                     f"{pv['V_PI']:.1f}{' (touchdown)' if pv['touchdown'] else ''} | {st} | {w_atm/nm:.1f} | {scr:.0f} | "
                     f"{n*n} ({ff:.2f}) | {R:.2f} | {r['gap_process']} | {r['notes']} |")
            out_rows.append(dict(name=label, membrane=stack_desc, thickness_um=props["t"] / um, radius_um=a / um, gap_nm=gnm,
                                 t_ins_nm=t_ins / nm, f_vac_MHz=fv / MHz, f_water_MHz=fw / MHz, V_PI=pv["V_PI"],
                                 V_PI_sealed=(0.0 if ps["collapsed_by_bias"] else ps["V_PI"]), w_atm_nm=w_atm / nm,
                                 sigma_cr_MPa=scr, cells=n * n, FF=ff, R=R, medium=med, gap_process=r["gap_process"],
                                 notes=r["notes"], sigma_nominal_MPa=props["N"] / props["t"] / 1e6))
    return L, out_rows


def main():
    import validate
    parts = ["## Validation\n" + validate.run()]
    lines, rows = design_tables()
    parts.append("## Table 1. Immersed (water) designs: largest gap with V_PI <= 150 V; sealed-cell constraints; thickness maximises stroke-limited output\n"
                 "(k_T^2 at 0.8 V_PI = 0.16 for every design: for the clamped-plate shape it depends only on V/V_PI)\n" + "\n".join(lines["water"]))
    parts.append("## Table 2. Air designs (vented bench devices; thickest course-practical plate, largest gap with V_PI <= 150 V)\n" + "\n".join(lines["air"]))
    parts.append("## Table 3. lambda/2 pitch in water vs cell diameter: cells per lambda/2 x lambda/2 element (fill factor)\n" + "\n".join(pitch_table()))
    refs = [r for r in rows["water"] if (r["stack"], r["f_target"]) in (("Au/SU-8", 1.0), ("Cr/SiN", 2.0), ("Al", 5.0))]
    parts.append("## Table 4. Nanogap scaling on fixed reference cells\n" + "\n".join(nanogap_table(refs)))
    fl, frows = nanogap_feasibility()
    parts.append("## Table 4b. What frequencies can a sub-100 nm gap reach? (lowest immersed f with sealing / stiction constraints)\n" + "\n".join(fl))
    srefs = [r for r in rows["water"] if (r["stack"], r["f_target"]) in (("Al", 1.0), ("Au/SU-8", 1.0), ("Cr", 2.0), ("Cr/SiN", 5.0))]
    parts.append("## Table 5. Residual stress (uniform biaxial stress through the stack)\n" + "\n".join(stress_table(srefs)))
    parts.append("## Table 6. Few-layer graphene membranes (tension-dominated model)\n" + "\n".join(graphene_table()))
    rl, rrows = recommended()
    parts.append("## Table 7. Recommended starting designs (6-term Galerkin pull-in, Ritz frequency)\n" + "\n".join(rl))
    text = "\n\n".join(parts)
    with open(os.path.join(OUT, "tables.txt"), "w") as fh:
        fh.write(text)
    with open(os.path.join(OUT, "recommended.json"), "w") as fh:
        json.dump(rrows, fh, indent=1)
    with open(os.path.join(OUT, "nanogap_feasibility.json"), "w") as fh:
        json.dump(frows, fh, indent=1)
    print(text)


if __name__ == "__main__":
    main()

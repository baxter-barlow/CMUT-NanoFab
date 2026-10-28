"""Verification of the model against (1) exact analytical limits, (2) multi-mode Galerkin reference,
(3) two published CMUTs:
  - Gerardo, Cretu, Rohling, Microsyst. Nanoeng. 4, 19 (2018), doi:10.1038/s41378-018-0022-5
    (SU-8 polyCMUT: a = 50 um, gap 0.30 um, SU-8 0.67 um below a 0.57 um Cr electrode of radius 0.46a,
     SU-8 2.40 um + Parylene-C 3.67 um above; vacuum sealed; f_air 2.83 MHz, 82 nm atmospheric deflection,
     1.525 MHz centre in mineral oil, pull-in 65 V)
  - Merbeler et al., Micromachines 13, 676 (2022), doi:10.3390/mi13050676
    (poly-Si plate 0.8 um, 44 um diameter, 120 nm vacuum gap, 25 nm insulator; f_air 6.43 MHz,
     V_PI 7.4 V measured, 3.35 MHz spectral peak in silicone oil)
"""
from __future__ import annotations

import numpy as np

import cmut
from materials import EPS0, MATERIALS as M, OIL_MINERAL_RHO, OIL_SILICONE_RHO, P_ATM

um, nm = 1e-6, 1e-9


def analytic_limits() -> list[str]:
    out = ["| check | model value | reference value |", "|---|---|---|"]
    out.append(f"| clamped plate lambda^2 (N=0) | {cmut.omega_param(0.0):.4f} | 10.2158 (Leissa NASA SP-160; root of J0 I1 + J1 I0 = 0) |")
    for k2 in (1e4, 1e6):
        out.append(f"| Omega/sqrt(Na^2/D) at Na^2/D={k2:.0e} | {cmut.omega_param(k2)/np.sqrt(k2):.4f} | 2.4048 (membrane, first zero of J0) |")
    out.append(f"| Omega at N = -0.999 N_cr | {cmut.omega_param(-0.999*cmut.J1Z**2):.3f} | -> 0 (buckling at N_cr = {cmut.J1Z**2:.2f} D/a^2) |")
    return out


def ritz_vs_exact() -> list[str]:
    al = M["Al"]
    t, a = 1 * um, 30 * um
    D, m = cmut.plate_D(al.E, al.nu, t), al.rho * t
    out = ["| sigma [MPa] | N a^2/D | f exact [MHz] | f Ritz (6 terms) [MHz] | f_rss=sqrt(fp^2+fm^2) [MHz] | rss error |",
           "|---|---|---|---|---|---|"]
    Ncr = cmut.N_buckle(D, a)
    for sig in (-0.9 * Ncr / t / 1e6, -50, 0, 50, 100, 200, 500, 1000):
        N = sig * 1e6 * t
        fe = cmut.f_exact(D, m, N, a)
        rp = cmut.RitzPlate(a, [(1.0, D, m, N, al.nu)])
        fr, _ = rp.freq()
        frss = cmut.f_rss(D, m, N, a) if N >= 0 else float("nan")
        err = f"{(frss/fe-1)*100:+.1f}%" if N >= 0 else "n/a (compression)"
        out.append(f"| {sig:.0f} | {N*a**2/D:.1f} | {fe/1e6:.3f} | {fr/1e6:.3f} | {frss/1e6 if N>=0 else float('nan'):.3f} | {err} |")
    return out


def pullin_accuracy() -> list[str]:
    """Compare single-mode Wygant, Galerkin (6-term), and two parallel-plate 'piston' shortcuts."""
    al = M["Al"]
    out = ["| case | V_PI Galerkin 6-term [V] | single-mode (Wygant) | piston, k=64piD/a^2 (uniform-load) | piston, k=192piD/a^2 (avg-deflection) |",
           "|---|---|---|---|---|"]
    cases = [("Al 1um a30um g200nm, vented", 1 * um, 30 * um, 200 * nm, 0.0, 0.0),
             ("Al 1um a30um g200nm, sigma=+100 MPa", 1 * um, 30 * um, 200 * nm, 100e6, 0.0),
             ("Al 1um a15um g100nm, sealed 1 atm", 1 * um, 15 * um, 100 * nm, 0.0, P_ATM),
             ("Al 1um a25um g100nm, sealed 1 atm", 1 * um, 25 * um, 100 * nm, 0.0, P_ATM),
             ("Al 2um a60um g1um, vented", 2 * um, 60 * um, 1000 * nm, 0.0, 0.0)]
    for name, t, a, g, sig, Pb in cases:
        D, m, N = cmut.plate_D(al.E, al.nu, t), al.rho * t, sig * t
        rp = cmut.RitzPlate(a, [(1.0, D, m, N, al.nu)])
        gal = rp.pullin(g, g, P_bias=Pb)["V_PI"]
        sm = cmut.SingleMode(D, m, N, a, g, g, P_bias=Pb)
        p1, p2 = sm.V_PI_piston("uniform_load_64D"), sm.V_PI_piston("avg")
        bias_note = " (piston formulas ignore the 1-atm bias)" if Pb else ""
        out.append(f"| {name}{bias_note} | {gal:.2f} | {sm.V_PI:.2f} ({(sm.V_PI/gal-1)*100:+.1f}%) | {p1:.2f} ({(p1/gal-1)*100:+.0f}%) | {p2:.2f} ({(p2/gal-1)*100:+.0f}%) |")
    # closed-form prefactor check
    sm = cmut.SingleMode(1.0, 1.0, 0.0, 1.0, 1.0, 1.0)
    pref = sm.V_PI ** 2 * EPS0 * sm.A / (sm.k * 1.0)
    out.append(f"| single-mode prefactor V_PI^2 eps0 A/(k g^3) | - | {pref:.4f} (Wygant 2019: 0.148), wn_PI = {sm.wn_PI:.3f} (0.154) | 8/27 = 0.296 | 8/27 = 0.296 |")
    return out


def gerardo2018() -> list[str]:
    su8, cr, par = M["SU8"], M["Cr"], M["ParyC"]
    a, g = 50 * um, 0.30 * um
    inner = cmut.stack_props([(su8, 0.67 * um), (cr, 0.57 * um), (su8, 2.40 * um), (par, 3.67 * um)])
    outer = cmut.stack_props([(su8, 0.67 * um + 0.57 * um), (su8, 2.40 * um), (par, 3.67 * um)])
    rows = []
    for label, E_su8 in (("SU-8 E=4.0 GPa", 4.0e9), ("SU-8 E=2.0 GPa", 2.0e9)):
        su8x = type(su8)(su8.name, E_su8, su8.nu, su8.rho, su8.sigma, su8.eps_r, su8.src)
        inner = cmut.stack_props([(su8x, 0.67 * um), (cr, 0.57 * um), (su8x, 2.40 * um), (par, 3.67 * um)])
        outer = cmut.stack_props([(su8x, 1.24 * um), (su8x, 2.40 * um), (par, 3.67 * um)])
        nu = outer["nu"]
        rp = cmut.RitzPlate(a, [(0.46, inner["D"], inner["m"], inner["N"], nu), (1.0, outer["D"], outer["m"], outer["N"], nu)])
        f_vac, vec = rp.freq()
        m_eff = rp.modal_areal_mass(vec)
        f_oil = cmut.f_fluid(f_vac, OIL_MINERAL_RHO, a, m_eff)
        w_atm = rp.static_center_deflection(P_ATM)
        g_eff = g + 0.67 * um / su8.eps_r
        pi = rp.pullin(g, g_eff, rho_e=0.46, P_bias=P_ATM)
        # uniform-stack closed forms for comparison
        rows.append(f"| Gerardo 2018 polyCMUT, {label} | f_air {f_vac/1e6:.2f} MHz (meas. 2.83) | w_atm {w_atm/nm:.0f} nm (meas. 82) | "
                    f"f_oil(Lamb) {f_oil/1e6:.2f} MHz (meas. centre 1.525) | V_PI {pi['V_PI']:.0f} V (meas. 65, sealed, 46% electrode) |")
    return rows


def merbeler2022() -> list[str]:
    ps = M["polySi"]
    t, a, g, tins = 0.8 * um, 22 * um, 120 * nm, 25 * nm
    D, m = cmut.plate_D(ps.E, ps.nu, t), ps.rho * t
    rows = []
    for eps_ins in (4.0, 7.0):
        g_eff = g + tins / eps_ins
        rp = cmut.RitzPlate(a, [(1.0, D, m, 0.0, ps.nu)])
        f_vac, _ = rp.freq()
        sealed = rp.pullin(g, g_eff, P_bias=P_ATM)["V_PI"]
        vented = rp.pullin(g, g_eff, P_bias=0.0)["V_PI"]
        f_oil = cmut.f_fluid(f_vac, OIL_SILICONE_RHO, a, m)
        rows.append(f"| Merbeler 2022 poly-Si (no piston), insulator eps_r={eps_ins:.0f} | f_air {f_vac/1e6:.2f} MHz (meas. 6.43) | "
                    f"w_atm {rp.static_center_deflection(P_ATM)/nm:.0f} nm of {g/nm:.0f} nm gap | f_oil(Lamb) {f_oil/1e6:.2f} MHz (meas. peak 3.35) | "
                    f"V_PI sealed {sealed:.1f} V / vented {vented:.1f} V (meas. 7.4) |")
    return rows


def run() -> str:
    parts = ["### V1. Analytical limits of the exact tensioned-plate frequency equation", *analytic_limits(), "",
             "### V2. Residual stress: exact vs Ritz vs root-sum-square approximation (Al, t = 1 um, a = 30 um)", *ritz_vs_exact(), "",
             "### V3. Pull-in: single-mode and piston shortcuts vs 6-term Galerkin", *pullin_accuracy(), "",
             "### V4. Published devices (no fitting except SU-8 modulus choice)",
             "| device | vacuum/air resonance | atmospheric deflection | fluid-loaded (Lamb) | pull-in |", "|---|---|---|---|---|",
             *gerardo2018(), *merbeler2022()]
    return "\n".join(parts)


if __name__ == "__main__":
    print(run())

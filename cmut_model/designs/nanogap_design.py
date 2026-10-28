"""Nanoscale-showcase CMUT concept for 6.2540: sub-100 nm resist-defined gap under an evaporated Al membrane.
Reuses the validated single-mode / Galerkin / exact-frequency model in ../cmut_model (cmut.py).
All results are my own calculations (small-deflection plate theory, bulk Al constants ASSUMED)."""
import os, sys, math, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import cmut
from materials import MATERIALS as M, EPS0, P_ATM

out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

Al = M["Al"]
t_m = 1.0e-6                    # evaporated Al membrane (also top electrode)
t_ins, eps_ins = 50e-9, 3.9     # sputtered/evaporated SiO2 insulator
rho_e = 0.85                    # bottom-electrode disk radius / cell radius (keeps electrode clear of anchor ring; MLA overlay margin)
GAMMA_IPA, GAMMA_W = 0.023, 0.072
props = cmut.stack_props([(Al, t_m)])
D, m = props["D"], props["m"]
P(f"Al t={t_m*1e6:.2f} um: D={D:.3e} N m, m''={m:.3e} kg/m2")

def cell(a, g, tins=t_ins, N=0.0, rhoe=rho_e, Pb=0.0):
    geff = g + tins / eps_ins
    return cmut.SingleMode(D, m, N, a, g, geff, rho_e=rhoe, P_bias=Pb), geff

def Rcap(a, g, gamma=GAMMA_IPA, N=0.0):
    k = cmut.k_avg(D, N, a)
    return (2 * gamma / g) / (k * (g / 3) / (math.pi * a ** 2))

def a_at_R(g, R, gamma=GAMMA_IPA):
    return (R * 64 * D * g ** 2 / (2 * gamma)) ** 0.25

def tas_membrane(g, gamma=GAMMA_IPA):
    lc = (3 * Al.E * t_m ** 3 * g ** 2 / (16 * gamma)) ** 0.25    # Tas 1996 cantilever (drying)
    return 1.7 * lc, 2.4 * lc

gaps = [50e-9, 75e-9, 100e-9, 200e-9]
radii = [6, 7, 8, 9, 9.5, 10, 11, 12, 14, 16, 18, 20]
P("\n=== 1. Stiction-safe radius vs gap (IPA dry, gamma=0.023 N/m) ===")
P("g nm | a(R=0.18) um | a(R=0.25) um | Tas membrane drying 1.7x / peel 2.4x um | water-dried a(R=0.25)")
stict = {}
for g in gaps:
    a18, a25 = a_at_R(g, 0.18), a_at_R(g, 0.25)
    t17, t24 = tas_membrane(g)
    aw = a_at_R(g, 0.25, GAMMA_W)
    stict[int(round(g*1e9))] = dict(a_R018=a18*1e6, a_R025=a25*1e6, tas17=t17*1e6, tas24=t24*1e6, a_water=aw*1e6)
    P(f"{g*1e9:5.0f} | {a18*1e6:6.2f} | {a25*1e6:6.2f} | {t17*1e6:6.2f} / {t24*1e6:6.2f} | {aw*1e6:6.2f}")

P("\n=== 2. Radius ladder: f, V_PI (insulated, 50 nm SiO2, rho_e=0.85) and insulator-free, R ===")
ladder = []
for g in gaps:
    P(f"-- gap {g*1e9:.0f} nm --")
    P(" a um | f_vac MHz | f_water(Lamb) MHz | V_PI ins V | V_PI bare V | C0/cell fF (ins) | R_IPA | status")
    for a_um in radii:
        a = a_um * 1e-6
        fv = cmut.f_exact(D, m, 0.0, a); fw = cmut.f_fluid(fv, 1000.0, a, m)
        sm, geff = cell(a, g)
        smb, _ = cell(a, g, tins=0.0)
        C0 = EPS0 * math.pi * a ** 2 * rho_e ** 2 / geff
        R = Rcap(a, g)
        st = "safe" if R <= 0.18 else ("marginal" if R <= 0.25 else ("likely stuck (wet)" ))
        ladder.append(dict(g_nm=g*1e9, a_um=a_um, f_vac=fv/1e6, f_water=fw/1e6, Vpi_ins=sm.V_PI, Vpi_bare=smb.V_PI, C0_fF=C0*1e15, R=R, status=st))
        P(f"{a_um:5.1f} | {fv/1e6:7.2f} | {fw/1e6:7.2f} | {sm.V_PI:7.1f} | {smb.V_PI:7.1f} | {C0*1e15:6.1f} | {R:5.2f} | {st}")

P("\n=== 3. Design point: g=75 nm, a=9.5 um, Al 1 um, 50 nm SiO2, rho_e=0.85 ===")
g0, a0 = 75e-9, 9.5e-6
sm, geff = cell(a0, g0)
# Galerkin reference
rp = cmut.RitzPlate(a0, [(1.0, D, m, 0.0, Al.nu)])
gal = rp.pullin(g0, geff, rho_e=rho_e)
fv = cmut.f_exact(D, m, 0, a0); fw = cmut.f_fluid(fv, 1000.0, a0, m); beta = cmut.lamb_beta(1000.0, a0, m)
P(f"g_eff={geff*1e9:.1f} nm; f_vac={fv/1e6:.2f} MHz; f_water(Lamb)={fw/1e6:.2f} MHz (beta={beta:.2f}); expected immersed centre {fw/1e6:.1f}-{1.5*fw/1e6:.1f} MHz if sealed")
P(f"V_PI single-mode={sm.V_PI:.2f} V; Galerkin={gal['V_PI']:.2f} V; centre defl at PI (Galerkin)={gal['w_center_PI']*1e9:.1f} nm; touchdown before PI? {sm.touchdown}")
R0 = Rcap(a0, g0); P(f"capillary ratio R(IPA)={R0:.3f}; R(water)={Rcap(a0,g0,GAMMA_W):.3f}")
sigcr = -cmut.N_buckle(D, a0) / t_m
P(f"buckling stress sigma_cr={sigcr/1e6:.0f} MPa")
wsealed = 3 * P_ATM * math.pi * a0**2 / cmut.k_avg(D, 0, a0)
P(f"if vacuum-sealed: 1-atm centre deflection={wsealed*1e9:.2f} nm ({wsealed/g0*100:.1f}% of gap)")
smS, _ = cell(a0, g0, Pb=P_ATM); P(f"sealed V_PI={smS.V_PI:.2f} V")
VPI = gal["V_PI"]
for frac in (0.5, 0.8, 0.9):
    V = frac * sm.V_PI
    ss = sm.small_signal(V)
    wc = 3 * ss["wn"] * geff
    E_ins = V / (t_ins + eps_ins * (g0 - wc))
    P(f" V={V:5.1f} V ({frac:.1f} V_PI): centre defl={wc*1e9:5.1f} nm, n={ss['n']*1e6:.3f} uN/V/cell, k_T^2={ss['k2']:.3f}, k_s/k={ss['soft']:.3f} -> f_bias={fv*math.sqrt(ss['soft'])/1e6:.1f} MHz (vac), C/cell={ss['C']*1e15:.1f} fF, insulator field at centre={E_ins/1e8:.2f} MV/cm")
E_td = sm.V_PI / t_ins
P(f"insulator field if plate touches down at V_PI: {E_td/1e8:.1f} MV/cm (thermal SiO2 measured 8.7 MV/cm; extrinsic 1-2 MV/cm)")

# touchdown-safe insulator vs breakdown field (self-consistent, stiction-limited radius R=0.18)
P("\n=== 4. Self-consistent touchdown-safe insulator under the stiction limit (R=0.18, g=75 nm) ===")
for Ebd in (2e8, 4e8, 6e8, 8.7e8):
    V = 30.0; conv = True
    for _ in range(200):
        tins = V / Ebd; ge = g0 + tins / eps_ins
        Vn = math.sqrt(0.888 * GAMMA_IPA * ge ** 3 / (0.18 * EPS0 * g0 ** 2))
        if Vn > 1000: conv = False; break
        if abs(Vn - V) < 1e-6: break
        V = Vn
    P(f" E_bd={Ebd/1e8:.1f} MV/cm -> " + (f"V_PI={V:.1f} V, t_ins={V/Ebd*1e9:.0f} nm" if conv else "no solution (runaway: thicker insulator raises V_PI faster than it adds margin)"))

# element / array
P("\n=== 5. 8-element 1D array: 100 um pitch (fUS-probe pitch), 2 mm elements ===")
pitch, kerf, web, Lel = 100e-6, 10e-6, 6e-6, 2.0e-3
per = 2 * a0 + web
nx = int((pitch - kerf + web) // per); ny = int((Lel + web) // per)
Ncell = nx * ny
FF = Ncell * math.pi * a0 ** 2 / (pitch * Lel)
C0 = EPS0 * math.pi * a0 ** 2 * rho_e ** 2 / geff
Cel = Ncell * C0
ssPI_C = EPS0*math.pi*a0**2/geff * cmut.G_plate(sm.wn_PI, rho_e)
P(f"cells/element={nx} x {ny} = {Ncell}; fill factor={FF:.2f}; C0/cell={C0*1e15:.1f} fF; element C0={Cel*1e12:.2f} pF; C at pull-in={Ncell*ssPI_C*1e12:.2f} pF (+{(ssPI_C/C0-1)*100:.0f}%)")
# post-collapse capacitance estimate: contact disk radius ~0.3a landing on insulator only
def C_collapsed(V, rc_frac=0.3):
    # crude: inner contact disk at t_ins/eps (capped by electrode), remainder approx at 0.5 g_air + t_ins/eps
    rc = rc_frac * a0
    re = rho_e * a0
    C_in = EPS0 * math.pi * min(rc, re) ** 2 / (t_ins / eps_ins)
    C_out = EPS0 * math.pi * (re ** 2 - min(rc, re) ** 2) / (0.5 * g0 + t_ins / eps_ins)
    return C_in + C_out
Cc = C_collapsed(sm.V_PI)
P(f"crude post-collapse C/cell (contact disk r=0.3a)={Cc*1e15:.0f} fF -> element jump {Ncell*(Cc-ssPI_C)*1e12:.1f} pF; charge step at V_PI ~{Ncell*(Cc-ssPI_C)*sm.V_PI*1e12:.0f} pC")
for rr in (0.1, 1.0):
    P(f" ramp-rate C-V at {rr} V/s: displacement current {Cel*rr*1e12:.2f} pA (pre-collapse) -> {Ncell*Cc*rr*1e12:.1f} pA (collapsed); leakage must be << this")
# parasitic: bottom routing lines under channels only; pads off-membrane on thick oxide
Apad = (150e-6) ** 2; tox = 1e-6
Cpad = EPS0 * 3.9 * Apad / tox
P(f"pad over 1 um thermal oxide to Si (150 um square): {Cpad*1e12:.2f} pF each (Si floating -> series; upper bound)")

# Comparison: same cell with 1 um gap; and V_PI scaling at fixed a
P("\n=== 6. What the nanogap buys (same a=9.5 um Al cell, 50 nm SiO2) ===")
for g in (1000e-9, 500e-9, 200e-9, 100e-9, 75e-9, 50e-9):
    s, ge = cell(a0, g)
    n20 = s.small_signal(min(20.0, 0.9*s.V_PI))["n"] if s.V_PI > 22.3 else float('nan')
    n08 = s.small_signal(0.8*s.V_PI)
    P(f" g={g*1e9:5.0f} nm: g_eff={ge*1e9:6.1f} nm, V_PI={s.V_PI:8.1f} V, n@20V={n20*1e6 if n20==n20 else float('nan'):.4f} uN/V, n@0.8VPI={n08['n']*1e6:.3f} uN/V, R_IPA={Rcap(a0,g):.3f}, p_ceiling(water,FF={FF:.2f})={FF*1.5e6*2*math.pi*fw*0.5*0.154*ge/1e3:.0f} kPa")

# stress sensitivity
P("\n=== 7. Residual stress sensitivity (design point and 200 nm-gap a=18 um ladder cell) ===")
for (a_um, g) in ((9.5, 75e-9), (18.0, 200e-9)):
    a = a_um*1e-6
    scr = -cmut.N_buckle(D, a) / t_m
    for sig in (-200e6, -100e6, 0, 100e6, 200e6):
        N = sig * t_m
        if N <= -cmut.N_buckle(D, a): P(f" a={a_um} g={g*1e9:.0f}: sigma={sig/1e6:+.0f} buckled"); continue
        f = cmut.f_exact(D, m, N, a)
        s, _ = cell(a, g, N=N)
        P(f" a={a_um} um g={g*1e9:.0f} nm sigma={sig/1e6:+5.0f} MPa: f_vac={f/1e6:6.2f} MHz, V_PI={s.V_PI:6.1f} V, R_IPA={Rcap(a,g,N=N):.3f} (sigma_cr={scr/1e6:.0f} MPa)")

# Ladder fit: V_PI^2 a^4 = c*(192 D + 12 N a^2) -> separate D and N
P("\n=== 8. Ladder fit check (200 nm die, insulator-free cells): V_PI^2 * a^4 vs a^2 ===")
for sig in (0, 50e6, 100e6):
    xs, ys = [], []
    for a_um in (8, 10, 12, 14, 16, 18):
        a = a_um*1e-6; s, _ = cell(a, 200e-9, tins=0.0, N=sig*t_m)
        xs.append(a**2); ys.append(s.V_PI**2 * a**4)
    p = np.polyfit(xs, ys, 1)
    P(f" sigma={sig/1e6:.0f} MPa: slope/intercept = {p[0]/p[1]*1e-12:.5f} per um^2 (expected 12N/(192D) = {12*sig*t_m/(192*D)*1e-12:.5f}); V_PI(a=8..18)={[round(math.sqrt(y)/x,1) for x,y in zip(xs,ys)]}")

# Air squeeze film at 75 nm (rough)
P("\n=== 9. Air in a 75 nm vented gap (rough) ===")
lam_mfp = 68e-9; mu = 1.8e-5
for g in (75e-9, 200e-9):
    Kn = lam_mfp / g; mu_eff = mu / (1 + 9.638 * Kn ** 1.159)
    om = 2 * math.pi * fv
    sigma_sq = 12 * mu_eff * om * a0 ** 2 / (P_ATM * g ** 2)
    k_gas = P_ATM * math.pi * a0 ** 2 / g
    P(f" g={g*1e9:.0f} nm: Kn={Kn:.2f}, mu_eff/mu={mu_eff/mu:.2f}, squeeze number at {fv/1e6:.0f} MHz={sigma_sq:.0f} (>>1: trapped gas), isothermal gas stiffness/plate k={k_gas/cmut.k_avg(D,0,a0):.3f}")

# displacement per volt in air (quasi-static) and Michelson signal
P("\n=== 10. Small-signal motion in air at 0.8 V_PI (design point) ===")
V = 0.8*sm.V_PI; ss = sm.small_signal(V)
x_avg = ss["n"] / ss["ks"]            # m/V average deflection
P(f" quasi-static: {x_avg*1e9:.3f} nm/V average, {3*x_avg*1e9:.2f} nm/V centre; x Q at resonance; Michelson (633 nm) at quadrature: {3*x_avg*1e9*2*math.pi/633*100:.2f}% of fringe p-p per V (centre, quasi-static)")

json.dump(dict(stiction=stict, ladder=ladder, design=dict(g_nm=75, a_um=9.5, t_um=1.0, t_ins_nm=50, rho_e=rho_e, geff_nm=geff*1e9,
          f_vac_MHz=fv/1e6, f_water_MHz=fw/1e6, Vpi_single=sm.V_PI, Vpi_galerkin=gal['V_PI'], Vpi_sealed=smS.V_PI, R_IPA=R0,
          sigma_cr_MPa=sigcr/1e6, cells_per_element=Ncell, FF=FF, C0_fF=C0*1e15, C_el_pF=Cel*1e12)),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nanogap_results.json"), "w"), indent=1)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nanogap_results.txt"), "w").write("\n".join(out))

"""Round-2 (v2) numbers: gap-matched array copies, bare-twin offsets, usability Monte Carlo. See report §6.12."""
"""v2 design numbers (C2 + C3 + C4 applied to v1). Uses the v1 physics core read-only."""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import cmut
from materials import MATERIALS as M, EPS0, P_ATM

Al = M["Al"]; pr = cmut.stack_props([(Al, 1e-6)]); D, m = pr["D"], pr["m"]
EPS_INS, T_INS, RHO_E = 3.9, 50e-9, 0.85
G23, G217 = 0.023, 0.0217
COPIES = [7.75e-6, 9.5e-6, 11.0e-6]
GAPS = [50e-9, 75e-9, 100e-9]
MATCH = dict(zip(GAPS, COPIES))
pitch, kerf, web, Lel = 100e-6, 10e-6, 6e-6, 2.0e-3

def Rcap(a, g, gam=G23):
    k = cmut.k_avg(D, 0.0, a); return (2*gam/g)/(k*(g/3)/(math.pi*a**2))
def sm(a, g, tins=T_INS, rho=RHO_E, gbare_extra=0.0):
    return cmut.SingleMode(D, m, 0.0, a, g+gbare_extra, g+gbare_extra+tins/EPS_INS, rho_e=rho)
def cells(a):
    per = 2*a+web; nx = int((pitch-kerf+web)//per); ny = int((Lel+web)//per); return nx, ny, nx*ny

print("=== A. Gap-matched array copies at their target gap (1 um Al, 50 nm SiO2, rho_e 0.85) ===")
print("g nm | a um | cells/elem | FF | C0 elem pF | I@1V/s pA | R(23) | R(21.7) | Vbare | Vins | 0.7Vins | f_vac | f@0.7 | Lamb sealed | dC/C0@0.7 | dC pF | kT2 | E_ins MV/cm | margin 0.15a um")
for g in GAPS:
    a = MATCH[g]; nx, ny, N = cells(a); FF = N*math.pi*a**2/(pitch*Lel)
    s = sm(a, g); sb = sm(a, g, tins=0)
    geff = g + T_INS/EPS_INS
    C0c = EPS0*math.pi*(RHO_E*a)**2/geff; C0 = N*C0c
    V = 0.7*s.V_PI; ss = s.small_signal(V)
    fv = cmut.f_exact(D, m, 0, a); fb = fv*math.sqrt(ss["soft"]); fl = cmut.f_fluid(fv, 1000.0, a, m)
    dCr = ss["C"]/C0c - 1
    wc = 3*ss["wn"]*geff; Eins = V/(T_INS + EPS_INS*(g - wc))
    print(f"{g*1e9:4.0f} | {a*1e6:5.2f} | {nx}x{ny}={N} | {FF:.2f} | {C0*1e12:.2f} | {C0*1e12:.1f} | {Rcap(a,g):.3f} | {Rcap(a,g,G217):.3f} | {sb.V_PI:.1f} | {s.V_PI:.1f} | {V:.1f} | {fv/1e6:.1f} | {fb/1e6:.1f} | {fl/1e6:.1f} | {dCr*100:.1f}% | {dCr*C0*1e12:.3f} | {ss['k2']:.3f} | {Eins/1e8:.2f} | {0.15*a*1e6:.2f}")

print("\n=== B. Cross matrix: every copy on every gap (R at 23 mN/m; bare V_PI; 0.7x insulated V_PI) ===")
for g in GAPS:
    row = []
    for a in COPIES:
        R = Rcap(a, g); vb = sm(a, g, tins=0).V_PI; v7 = 0.7*sm(a, g).V_PI
        st = "STUCK?" if R > 0.25 else ("marginal" if R > 0.20 else ("bias>40V" if v7 > 40 else "usable"))
        row.append(f"a={a*1e6:.2f}: R={R:.3f} Vb={vb:.1f} 0.7Vi={v7:.1f} [{st}]")
    print(f"{g*1e9:.0f} nm | " + " | ".join(row))
print("lowest bare V_PI of any copy on each gap (cap for unselected-copy screening):",
      {int(g*1e9): round(min(sm(a, g, tins=0).V_PI for a in COPIES), 1) for g in GAPS})

print("\n=== C. C2 sensitivity: true fraction of insulated V_PI reached by a '0.7x' (and 0.6x) bias when the bare gap is larger by d ===")
for g in GAPS:
    for a in sorted(set([MATCH[g], 9.5e-6])):
        vi = sm(a, g).V_PI; fac = ((g+T_INS/EPS_INS)/g)**1.5
        out = []
        for d in (5e-9, 10e-9, 20e-9, 50e-9):
            vb = sm(a, g, tins=0, gbare_extra=d).V_PI
            out.append(f"+{d*1e9:.0f}nm: 0.7x->{0.7*vb*fac/vi:.3f} 0.6x->{0.6*vb*fac/vi:.3f} (bare V_PI {vb:.1f} V)")
        print(f"{g*1e9:.0f} nm, a={a*1e6:.2f}: matched bare V_PI {sm(a,g,tins=0).V_PI:.1f} V | " + " | ".join(out))

print("\n=== D. C2 L2-well geometry (anchor ring 6 um = web) ===")
for a in COPIES + [6e-6, 14e-6]:
    for mg in (10e-6, 30e-6, 50e-6):
        Ro = a + 6e-6 + mg
        print(f"a={a*1e6:5.2f} um, margin {mg*1e6:.0f} um: isolated-twin opening radius {Ro*1e6:.1f} um (dia {2*Ro*1e6:.0f} um)")
# shared end-zone well per array end: 8 elements x 2 twins, twins on 2a+web pitch within each 90 um element width
for a in COPIES:
    per = 2*a+web
    w_zone = 8*pitch          # spans the array width
    depth_twins = per          # one row of twins per element end (2 twins side-by-side fit in 90 um)
    for mg in (30e-6, 50e-6):
        depth = depth_twins + 2*mg + 12e-6
        guard_to_array = mg
        area = w_zone*depth
        print(f"a={a*1e6:5.2f}: end-zone well {w_zone*1e6:.0f} x {depth*1e6:.0f} um (margin {mg*1e6:.0f} um); plus {guard_to_array*1e6:.0f} um guard to first insulated anchor; area/end {area*1e6:.3f} mm^2 -> 2 ends {2*area*1e6:.3f} mm^2")

print("\n=== E. Extra bare metal per bare twin under diluted resist (C2 trade) ===")
for a in COPIES:
    Ael = math.pi*(RHO_E*a)**2
    for mg, w in ((30e-6, 1e-6), (30e-6, 2e-6)):
        Lbus = 2*(6e-6 + 10e-6)  # 2 bus segments crossing anchor ring + ~10 um in-well before reaching an L4 opening/pad corridor (short in-well segment)
        print(f"a={a*1e6:5.2f}: electrode {Ael*1e12:.0f} um^2; extra bare bus ~{Lbus*w*1e12:.0f} um^2 at {w*1e6:.0f} um width (+{Lbus*w/Ael*100:.0f}%)")

print("\n=== F. 7.75 um copy with fallback electrode min(0.85a, a-2um) = 5.75 um (if L3-L1 overlay > ~0.9 um) ===")
a = 7.75e-6; g = 50e-9; rho2 = 5.75/7.75
s1 = sm(a, g); s2 = sm(a, g, rho=rho2); b1 = sm(a, g, tins=0); b2 = sm(a, g, tins=0, rho=rho2)
print(f"rho_e {RHO_E}->{rho2:.3f}: Vins {s1.V_PI:.1f}->{s2.V_PI:.1f} V; Vbare {b1.V_PI:.1f}->{b2.V_PI:.1f} V; C0 x{(rho2/RHO_E)**2:.3f}")

print("\n=== G. Run-2 thicker SiO2: 0.7x insulated V_PI (V) per copy ===")
for t in (72e-9, 100e-9, 139e-9):
    print(f"SiO2 {t*1e9:.0f} nm: " + " | ".join(f"{g*1e9:.0f}nm: " + ", ".join(f"{a*1e6:.2f}->{0.7*sm(a,g,tins=t).V_PI:.1f}" for a in COPIES) for g in GAPS))

print("\n=== H. Capillary floor for stiction-safe bare cells, R = 0.25: V_min = sqrt(0.888 gamma g/(R eps0)) ===")
for g in GAPS:
    print(f"{g*1e9:.0f} nm: {math.sqrt(0.888*G23*g/(0.25*EPS0)):.1f} V (gamma 23) / {math.sqrt(0.888*G217*g/(0.25*EPS0)):.1f} V (21.7)")

print("\n=== I. Usable-array Monte Carlo (independent check; gap ~ N(target, sigma); R<=0.20 at 23 mN/m) ===")
rng = np.random.default_rng(11)
grid = np.linspace(20e-9, 180e-9, 321)
tab = {}
for a in COPIES:
    tab[a] = (np.array([sm(a, g).V_PI for g in grid]), np.array([sm(a, g, tins=0).V_PI for g in grid]))
def usable(a, g, crit):
    vi = np.interp(g, grid, tab[a][0]); vb = np.interp(g, grid, tab[a][1])
    if Rcap(a, g) > 0.20: return False
    if crit == "strict": return 0.7*vi <= 40
    if crit == "v1pol": return 0.6*vi <= 40
    if crit == "bare": return 0.7*vi <= 40 and vb <= 40
for sig in (0.10, 0.15):
    for crit in ("strict", "v1pol", "bare"):
        per1, per3 = [], []
        for t in GAPS:
            gs = t*(1+sig*rng.standard_normal(3000)); gs = gs[gs > 25e-9]
            per1.append(np.mean([usable(9.5e-6, g, crit) for g in gs]))
            per3.append(np.mean([any(usable(a, g, crit) for a in COPIES) for g in gs]))
        print(f"sigma {sig:.0%} {crit:6s}: per-die P v1 " + "/".join(f"{p:.2f}" for p in per1) + " -> v2 " + "/".join(f"{p:.2f}" for p in per3)
              + f" | E[usable arrays per 6-die run] {2*sum(per1):.2f} -> {2*sum(per3):.2f}")

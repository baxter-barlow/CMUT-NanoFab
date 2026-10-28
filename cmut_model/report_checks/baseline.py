import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import cmut
from materials import MATERIALS as M, EPS0, P_ATM
Al = M["Al"]
def run(t, g, tins, eps, radii, rhoe=0.85, label=""):
    p = cmut.stack_props([(Al, t)]); D, m = p["D"], p["m"]
    print(f"== {label}: Al {t*1e6} um, gap {g*1e9:.0f} nm, ins {tins*1e9:.0f} nm eps {eps}")
    for a_um in radii:
        a = a_um*1e-6; geff = g + tins/eps
        fv = cmut.f_exact(D, m, 0, a); fw = cmut.f_fluid(fv, 1000.0, a, m)
        si = cmut.SingleMode(D, m, 0, a, g, geff, rho_e=rhoe)
        sb = cmut.SingleMode(D, m, 0, a, g, g, rho_e=rhoe)
        ss = cmut.SingleMode(D, m, 0, a, g, geff, rho_e=rhoe, P_bias=P_ATM)
        k = cmut.k_avg(D, 0, a); R = (2*0.023/g)/(k*(g/3)/(math.pi*a**2))
        watm = 3*P_ATM*math.pi*a**2/k
        sig = -cmut.N_buckle(D, a)/t
        print(f"a={a_um:5.1f} f_vac={fv/1e6:6.2f} f_w={fw/1e6:5.2f} Vins={si.V_PI:6.1f} Vbare={sb.V_PI:6.1f} Vsealed={ss.V_PI:6.1f} R={R:5.2f} watm={watm*1e9:6.0f}nm sigcr={sig/1e6:6.0f}MPa")
run(1.0e-6, 1.0e-6, 50e-9, 3.9, [20,25,30,35,40,45,50], label="baseline die")
run(1.0e-6, 200e-9, 50e-9, 3.9, [14,15,16,17], label="200 nm split")
run(0.8e-6, 75e-9, 50e-9, 3.9, [7.5,8.0,8.5], label="sputtered 0.8 um fallback")
# Concept A sealed check: 0.8 um Al, a=30, 1 um gap, 80 nm SiO2, rho_e 0.8
run(0.8e-6, 1.0e-6, 80e-9, 3.9, [30], rhoe=0.8, label="Concept A array cell")

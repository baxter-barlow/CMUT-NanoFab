"""Insulator safety-margin sensitivity: t_ins = margin * V_contact / E_bd (E_bd = 2 MV/cm, eps_r 8).
Single-mode Wygant model with contact at centre deflection = g_air (touchdown before pull-in handled)."""
import math, numpy as np
from check import stack, sm_pullin
E_BD, EPS = 2e8, 8.0
cases = [("R1", [("Al", 1e-6)], 39.43e-6, 1000e-9), ("R3", [("Al", 1e-6)], 12.3e-6, 100e-9),
         ("R4", [("Al", 1e-6)], 10.7e-6, 75e-9), ("R5", [("Cr", 50e-9), ("SiN", 1e-6)], 15.5e-6, 100e-9)]
for name, layers, a, g in cases:
    s = stack(layers)
    for margin in (1.0, 2.0):
        t = 50e-9
        for _ in range(200):
            V, wn, td = sm_pullin(s["D"], s["N"], a, g + t / EPS, g_air=g)
            tn = max(50e-9, margin * V / E_BD)
            if abs(tn - t) < 0.01e-9: break
            t = 0.5 * t + 0.5 * tn
        print(f"{name} margin {margin:.0f}x: t_ins = {t*1e9:.0f} nm, g_eff = {(g+t/EPS)*1e9:.0f} nm, V_max = {V:.1f} V, "
              f"{'TOUCHDOWN before pull-in' if td else 'pull-in'}")
    V50, _, td = sm_pullin(s["D"], s["N"], a, g + 50e-9 / EPS, g_air=g)
    print(f"{name} 50 nm insulator (no touchdown allowed): V_PI = {V50:.1f} V")

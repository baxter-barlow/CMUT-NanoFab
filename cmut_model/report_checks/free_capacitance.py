"""Static (Q/V) vs free (dQ/dV) capacitance change of the 75 nm design cell; the ramp C-V reads the free capacitance (report §6.12 erratum)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import cmut
from materials import MATERIALS as M
al = M['Al'] if 'Al' in M else [v for k, v in M.items() if k.lower().startswith('al')][0]
p = cmut.stack_props([(al, 1e-6)])
D, m, N = p['D'], p['m'], p.get('N', 0.0)
a, g_air = 9.5e-6, 75e-9
g_eff = g_air + 50e-9 / 3.9
cell = cmut.SingleMode(D, m, N, a, g_air, g_eff, rho_e=0.85)
def Q(V):
    wn = cell.operating_point(V)
    return cmut.EPS0 * cell.A / g_eff * cell.G(wn) * V
C0 = cmut.EPS0 * cell.A / g_eff * cell.G(1e-9)
print(f"V_PI = {cell.V_PI:.2f} V, C0 = {C0*1e15:.2f} fF/cell")
for V in (20.0, 0.6 * cell.V_PI, 0.7 * cell.V_PI, 0.8 * cell.V_PI):
    h = 1e-3
    CT = (Q(V + h) - Q(V - h)) / (2 * h)
    Cs = Q(V) / V
    print(f"V = {V:5.1f} V ({V/cell.V_PI:.2f} V_PI): static C/C0 = {Cs/C0-1:+.1%}, free C_T/C0 = {CT/C0-1:+.1%}")

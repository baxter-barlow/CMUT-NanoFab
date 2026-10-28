"""Fast add-on checks (closed-form plate theory): edge bending stress, gap fields, gap-tolerance sensitivity.
Clamped plate under uniform q: centre w0 = q a^4/(64 D); radial edge moment M_r(a) = q a^2/8 -> sigma_edge = 3 q a^2/(4 t^2).
Electrostatic load at pull-in approximated by the uniform q giving the pull-in centre deflection 0.46 g_eff.
"""
import math

P = 101325.0
E = dict(Al=(70e9, 0.35), Cr=(250e9, 0.21))
# name, mat, t, a, g_air, t_ins, V_PI vented, sealed?
D = [
    ("R1", "Al", 1.0e-6, 39.43e-6, 1000e-9, 516e-9, 102.0, True),
    ("R3", "Al", 1.0e-6, 12.3e-6, 100e-9, 221e-9, 43.5, True),
    ("R4", "Al", 1.0e-6, 10.7e-6, 75e-9, 204e-9, 40.2, True),
    ("R6 g200", "Al", 1.0e-6, 10.0e-6, 200e-9, 0.0, 129.2, False),
    ("R6 g100", "Al", 1.0e-6, 10.0e-6, 100e-9, 0.0, 45.7, False),
    ("R6 g50", "Al", 1.0e-6, 10.0e-6, 50e-9, 0.0, 16.1, False),
    ("R7", "Al", 1.0e-6, 35.0e-6, 1000e-9, 673e-9, 133.1, False),
    ("T1 Cr0.5 0.5MHz", "Cr", 0.5e-6, 32.6e-6, 1334e-9, 749e-9, 150.0, True),
    ("T1 Cr0.2 1MHz", "Cr", 0.2e-6, 14.3e-6, 1095e-9, 749e-9, 150.0, True),
    ("T1 Al1 1MHz", "Al", 1.0e-6, 29.7e-6, 842e-9, 750e-9, 150.0, True),
]
print("design | sigma_edge 1atm MPa (linear) | sigma_edge at vented PI MPa | E_air at V_PI, undeflected MV/cm | E_air at PI centre MV/cm | dV_PI for +-10% gap")
for n, mat, t, a, g, ti, V, sealed in D:
    Em, nu = E[mat]
    Dp = Em * t ** 3 / (12 * (1 - nu ** 2))
    s_atm = 0.75 * P * a * a / t ** 2 if sealed else float("nan")
    geff = g + ti / 8
    q_pi = 64 * Dp * 0.46 * geff / a ** 4
    s_pi = 0.75 * q_pi * a * a / t ** 2
    E0 = V / geff / 1e8
    Ec = V / (geff - 0.46 * geff) / 1e8
    # V ~ g_eff^1.5 with t_ins fixed
    up = ((g * 1.1 + ti / 8) / geff) ** 1.5 - 1
    dn = ((g * 0.9 + ti / 8) / geff) ** 1.5 - 1
    print(f"{n} | {s_atm/1e6:.0f} | {s_pi/1e6:.0f} | {E0:.2f} | {Ec:.2f} | {up*100:+.0f}% / {dn*100:+.0f}%")

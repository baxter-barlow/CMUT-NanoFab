"""Thin-film reflectance of the sacrificial resist / SiO2 witness on Si (normal incidence, 2-interface Airy),
plus sanity checks. Optical constants are ASSUMED approximate handbook values (resist n=1.64 non-dispersive;
Si n,k interpolated; SiO2 n=1.46)."""
import math, numpy as np
lam = np.array([400, 450, 500, 550, 600, 650, 700, 750, 800.])
nSi = np.interp(lam, [400, 450, 500, 550, 600, 650, 700, 800], [5.57, 4.67, 4.30, 4.08, 3.94, 3.85, 3.78, 3.69]) \
    + 1j*np.interp(lam, [400, 450, 500, 550, 600, 650, 700, 800], [0.39, 0.14, 0.07, 0.04, 0.02, 0.02, 0.01, 0.006])
def R(n1, d):
    r01 = (1 - n1)/(1 + n1); r12 = (n1 - nSi)/(n1 + nSi)
    ph = np.exp(2j*2*np.pi*n1*d/(lam*1e-9))
    r = (r01 + r12*ph)/(1 + r01*r12*ph)
    return np.abs(r)**2
R0 = np.abs((1 - nSi)/(1 + nSi))**2
print("lambda nm      :", " ".join(f"{l:5.0f}" for l in lam))
print("bare Si        :", " ".join(f"{x:5.3f}" for x in R0))
for d in (50, 60, 75, 90, 100, 200):
    print(f"resist {d:3d} nm  :", " ".join(f"{x:5.3f}" for x in R(1.64, d*1e-9)))
print(f"SiO2 50 nm     :", " ".join(f"{x:5.3f}" for x in R(1.46, 50e-9)))
# sensitivity dR/dd at 500 and 600 nm for 75 nm resist
for l_i in (2, 4):
    d1 = R(1.64, 74e-9)[l_i]; d2 = R(1.64, 76e-9)[l_i]
    print(f"dR/dd at {lam[l_i]:.0f} nm, d=75 nm: {(d2-d1)/2:.4f} per nm (abs reflectance)")
# Pirouz 2018 sanity check of the capillary criterion (my estimate; SiN E assumed 150 GPa, nu 0.25; square 46 um -> equal-area circle)
E, nu, t = 150e9, 0.25, 2.2e-6; D = E*t**3/(12*(1-nu**2)); a = 46e-6/math.sqrt(math.pi); g = 95e-9
for gam, name in ((0.023, "IPA"), (0.072, "water")):
    Rc = 2*gam*a**4/(64*D*g**2); print(f"Pirouz cell (a_eq={a*1e6:.1f} um, 2.2 um SiN, 95 nm gap) R_{name}={Rc:.2f}")

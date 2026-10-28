"""Independent physics check of the CMUT design-space model (6.2540 final project).

Independent of cmut_model/: different numerics throughout.
  * constants re-derived: clamped-plate lambda^2 (Bessel root), buckling j11^2, Lamb AVMI factor from the
    incompressible baffled Rayleigh integral (Hankel transform), Wygant single-mode pull-in constants from a
    numerically integrated capacitance, Timoshenko-type large-deflection coefficient from a Ritz energy.
  * plate model: axisymmetric Hermite-cubic finite elements (local basis; the checked model used a global
    polynomial Galerkin), with bending + residual tension, consistent mass, and nonlinear electrostatic
    pressure eps0 V^2 / (2 (g_eff - w)^2) integrated on the element quadrature points.
  * pull-in: displacement-controlled fixed-point iteration on the FE model (centre deflection prescribed,
    V^2 eliminated), sweep to the maximum of V^2 along the stable branch.
Run: python3 check.py
"""
from __future__ import annotations

import math

import numpy as np
from scipy import integrate, linalg, optimize, special

EPS0 = 8.8541878128e-12
P_ATM = 101325.0
RHO_W = 1000.0
um, nm, MHz, GPa, MPa = 1e-6, 1e-9, 1e6, 1e9, 1e6

# same nominal material constants as the checked model (so that differences isolate the physics/numerics)
MAT = {
    "Al": dict(E=70 * GPa, nu=0.35, rho=2700.0, sig=0.0),
    "Cr": dict(E=250 * GPa, nu=0.21, rho=7190.0, sig=0.0),
    "Au": dict(E=79 * GPa, nu=0.42, rho=19300.0, sig=0.0),
    "SU8": dict(E=4.0 * GPa, nu=0.22, rho=1190.0, sig=17 * MPa),
    "ParyC": dict(E=2.8 * GPa, nu=0.40, rho=1289.0, sig=0.0),
    "SiN": dict(E=150 * GPa, nu=0.25, rho=2700.0, sig=0.0),
    "Al2O3": dict(E=120 * GPa, nu=0.24, rho=3000.0, sig=0.0),
}
EPS_INS = 8.0


# =====================================================================================================
# 1. Constants
# =====================================================================================================
def clamped_lambda2() -> float:
    f = lambda x: special.j0(x) * special.i1(x) + special.j1(x) * special.i0(x)
    x = optimize.brentq(f, 2.5, 3.8, xtol=1e-14)
    return x * x


def lamb_coefficient() -> tuple[float, float]:
    """Generalized fluid mass for w = (1-rho^2)^2 on a rigid baffle, incompressible fluid:
    M_f = (rho_f / 2pi) int_0^inf |w_hat(k)|^2 dk, w_hat = 2pi int w J0(kr) r dr = 2pi a^2 * 8 J3(ka)/(ka)^3.
    Plate generalized mass M_p = m * 2pi a^2 * int (1-rho^2)^4 rho drho = pi m a^2 / 5.
    beta = M_f / M_p = Gamma * rho_f a / m.  Returns (Gamma, Lamb's c in T_L = c rho_f a^3 Cdot^2)."""
    # check the transform numerically too
    k = 3.7
    num = integrate.quad(lambda r: (1 - r * r) ** 2 * special.j0(k * r) * r, 0, 1)[0]
    assert abs(num - 8 * special.jv(3, k) / k ** 3) < 1e-10
    I = 0.0
    edges = np.concatenate([[0.0], np.arange(5, 2000, 5.0)])
    for lo, hi in zip(edges[:-1], edges[1:]):
        I += integrate.quad(lambda x: special.jv(3, x) ** 2 / x ** 6 if x > 0 else 0.0, lo, hi, limit=200)[0]
    # tail beyond 2000 ~ int (2/(pi x)) * 0.5 / x^6 dx -> negligible
    Mf_coef = (1 / (2 * math.pi)) * (2 * math.pi * 8) ** 2 * I       # M_f = Mf_coef * rho a^3
    Gamma = Mf_coef / (math.pi / 5)
    return Gamma, Mf_coef / 2


def Cn_numeric(wn: float) -> float:
    """C / (eps0 A / g) for w = 3 wn g (1-rho^2)^2, integrated numerically (not the atanh closed form)."""
    return integrate.quad(lambda r: 2 * r / (1 - 3 * wn * (1 - r * r) ** 2), 0, 1, epsabs=1e-13, epsrel=1e-12)[0]


def wygant_constants() -> tuple[float, float, float]:
    h = 1e-5
    def v2(wn):   # V^2 eps0 A / (k g^3) = 2 wn / Cn'(wn)
        d = (Cn_numeric(wn + h) - Cn_numeric(wn - h)) / (2 * h)
        return 2 * wn / d
    res = optimize.minimize_scalar(lambda w: -v2(w), bounds=(0.05, 0.3), method="bounded", options=dict(xatol=1e-7))
    wn = res.x
    return v2(wn), wn, Cn_numeric(wn)


def large_deflection_coefficient(nu: float) -> float:
    """Ritz: w = w0 (1-rho^2)^2, immovable clamped edge, u = a sum c_k rho^k (1-rho), k=1..8.
    Returns c3 in  P a^4 / (64 D) = w0 [1 + c3 (w0/t)^2]."""
    K = 8
    x, wq = np.polynomial.legendre.leggauss(80)
    r = 0.5 * (x + 1); wq = 0.5 * wq
    wp = -4 * r * (1 - r * r)               # dw/drho per unit w0
    phi = np.array([r ** k * (1 - r) for k in range(1, K + 1)])
    dphi = np.array([k * r ** (k - 1) - (k + 1) * r ** k for k in range(1, K + 1)])
    # eps_r = (1/a)[a u'_rho/a ...] -> with u = a U(rho), w = w0 W(rho): eps_r = U' + 0.5 (w0/a)^2 W'^2, eps_t = U / rho
    # energy density per (E t/(2(1-nu^2))) * 2 pi a^2 :  int (er^2 + et^2 + 2 nu er et) rho drho ; let s = 0.5 (w0/a)^2
    # quadratic in c: c^T Q c + 2 s b^T c + s^2 e
    Q = np.zeros((K, K)); b = np.zeros(K)
    for i in range(K):
        for j in range(K):
            Q[i, j] = np.sum((dphi[i] * dphi[j] + phi[i] * phi[j] / r ** 2 + nu * (dphi[i] * phi[j] + dphi[j] * phi[i]) / r) * r * wq)
        b[i] = np.sum((dphi[i] * wp ** 2 + nu * wp ** 2 * phi[i] / r) * r * wq)
    e = np.sum(wp ** 4 * r * wq)
    c = -linalg.solve(Q, b)                 # per unit s
    Iu = e + 2 * b @ c + c @ Q @ c          # min energy integral per s^2
    # U_m = (E t / (2 (1-nu^2))) 2 pi a^2 * s^2 * Iu,  s = 0.5 w0^2/a^2 -> U_m = C_m w0^4
    # C_m = (E t/(2(1-nu^2))) 2 pi a^2 * 0.25 / a^4 * Iu = E t pi Iu / (4 (1-nu^2) a^2)
    # equilibrium: P pi a^2 / 3 = (64 pi D / (3 a^2)) w0 + 4 C_m w0^3
    # -> P a^4/(64 D) = w0 [1 + (12 a^2 C_m / (64 pi D)) w0^2]; D = E t^3 / (12 (1-nu^2))
    # coefficient on (w0/t)^2 = 12 * 12 * Iu / (64 * 4) * ... compute explicitly:
    E, t, a = 1.0, 1.0, 1.0
    D = E * t ** 3 / (12 * (1 - nu ** 2))
    Cm = E * t * math.pi * Iu / (4 * (1 - nu ** 2) * a ** 2)
    return 12 * a ** 2 * Cm / (64 * math.pi * D) * t ** 2


# =====================================================================================================
# 2. Stack properties (A-B-D laminate form, independent code)
# =====================================================================================================
def stack(layers, sigma_override=None):
    """layers: [(mat_name, t)] gap side first. Returns D, m, N, t_total (classical laminate, isotropic layers)."""
    z = 0.0; A = B = Dz = m = N = 0.0
    for name, t in layers:
        p = MAT[name]; Ep = p["E"] / (1 - p["nu"] ** 2)
        z0, z1 = z, z + t
        A += Ep * (z1 - z0)
        B += Ep * (z1 ** 2 - z0 ** 2) / 2
        Dz += Ep * (z1 ** 3 - z0 ** 3) / 3
        m += p["rho"] * t
        N += p["sig"] * t
        z = z1
    if sigma_override is not None:
        N = sigma_override * z
    return dict(D=Dz - B * B / A, m=m, N=N, t=z)


# =====================================================================================================
# 3. Axisymmetric Hermite-cubic FEM for a clamped circular plate
# =====================================================================================================
class FEPlate:
    def __init__(self, a, D, m, N, nu=0.3, ne=120, nq=6):
        self.a = a
        # graded mesh, finer near the clamped edge
        s = np.linspace(0, 1, ne + 1)
        self.nodes = a * (1 - (1 - s) ** 1.0)
        ndof = 2 * (ne + 1)
        K = np.zeros((ndof, ndof)); Mm = np.zeros((ndof, ndof))
        xg, wg = np.polynomial.legendre.leggauss(nq)
        self.qr, self.qw, self.qN, self.qdofs = [], [], [], []
        for e in range(ne):
            r0, r1 = self.nodes[e], self.nodes[e + 1]; L = r1 - r0
            xi = 0.5 * (xg + 1); r = r0 + L * xi; w = 0.5 * L * wg
            H = np.array([1 - 3 * xi ** 2 + 2 * xi ** 3, L * (xi - 2 * xi ** 2 + xi ** 3), 3 * xi ** 2 - 2 * xi ** 3, L * (-xi ** 2 + xi ** 3)])
            H1 = np.array([(-6 * xi + 6 * xi ** 2) / L, (1 - 4 * xi + 3 * xi ** 2), (6 * xi - 6 * xi ** 2) / L, (-2 * xi + 3 * xi ** 2)])
            H2 = np.array([(-6 + 12 * xi) / L ** 2, (-4 + 6 * xi) / L, (6 - 12 * xi) / L ** 2, (-2 + 6 * xi) / L])
            dofs = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
            ke = np.zeros((4, 4)); me = np.zeros((4, 4))
            for i in range(4):
                for j in range(4):
                    bend = H2[i] * H2[j] + H1[i] * H1[j] / r ** 2 + nu * (H2[i] * H1[j] + H2[j] * H1[i]) / r
                    ke[i, j] = 2 * np.pi * np.sum((D * bend + N * H1[i] * H1[j]) * r * w)
                    me[i, j] = 2 * np.pi * np.sum(m * H[i] * H[j] * r * w)
            K[np.ix_(dofs, dofs)] += ke; Mm[np.ix_(dofs, dofs)] += me
            self.qr.append(r); self.qw.append(2 * np.pi * r * w); self.qN.append(H); self.qdofs.append(dofs)
        self.qr = np.concatenate(self.qr); self.qw = np.concatenate(self.qw)
        # global interpolation matrix: w(quad pts) = Phi @ q
        Phi = np.zeros((self.qr.size, ndof)); k0 = 0
        for H, dofs in zip(self.qN, self.qdofs):
            n = H.shape[1]
            Phi[k0:k0 + n][:, dofs] = H.T; k0 += n
        # BCs: w'(0)=0 (dof 1), w(a)=w'(a)=0 (last two)
        free = [i for i in range(ndof) if i not in (1, ndof - 2, ndof - 1)]
        self.free = free
        self.K = K[np.ix_(free, free)]; self.M = Mm[np.ix_(free, free)]
        self.Phi = Phi[:, free]
        self.F1 = self.Phi.T @ self.qw          # consistent load vector for unit uniform pressure
        self.Kinv_F1 = linalg.solve(self.K, self.F1)

    def freq(self):
        ev = linalg.eigh(self.K, self.M, eigvals_only=True)
        return math.sqrt(ev[0]) / (2 * math.pi)

    def mode(self):
        ev, vec = linalg.eigh(self.K, self.M)
        return vec[:, 0]

    def centre_deflection(self, P):
        return P * self.Kinv_F1[0]

    def pullin(self, g_air, g_eff, P_bias=0.0, n=120):
        """Displacement control on the centre DOF. Returns V_PI, centre deflection at PI, touchdown flag, collapsed flag."""
        wb = self.Kinv_F1 * P_bias
        if wb[0] >= g_air:
            return dict(V=0.0, wc=float("nan"), touchdown=False, collapsed=True)
        q = wb.copy()
        best = (-1.0, None)
        wcs = wb[0] + (0.999 * g_air - wb[0]) * np.linspace(0.005, 1, n)
        lam = 0.0
        for wc in wcs:
            for it in range(400):
                wq = self.Phi @ q
                gap = g_eff - wq
                if np.any(gap <= 0):
                    return dict(V=math.sqrt(max(best[0], 0)), wc=best[1], touchdown=False, collapsed=False)
                Fe = self.Phi.T @ (0.5 * EPS0 / gap ** 2 * self.qw)
                u = linalg.solve(self.K, Fe)
                lam_new = (wc - wb[0]) / u[0]
                q_new = lam_new * u + wb
                if np.max(np.abs(q_new[::2] - q[::2])) < 1e-10 * g_eff:
                    q, lam = q_new, lam_new
                    break
                q = 0.5 * q + 0.5 * q_new; lam = lam_new
            if lam > best[0]:
                best = (lam, wc)
            elif lam < 0.97 * best[0]:
                break
        touchdown = best[1] is not None and best[1] >= wcs[-1] * 0.999
        return dict(V=math.sqrt(max(best[0], 0)), wc=best[1], touchdown=bool(touchdown), collapsed=False)


def fluid_beta_modeshape(fp: FEPlate, m: float, rho_f=RHO_W) -> float:
    """AVMI factor for the actual FE mode shape (Rayleigh integral, incompressible, rigid baffle)."""
    q = fp.mode()
    r = fp.qr; wdA = fp.qw
    w = fp.Phi @ q
    Mp = m * np.sum(w * w * wdA)
    ks = np.concatenate([np.linspace(1e-6, 60, 6000), np.linspace(60, 3000, 30000)[1:]]) / fp.a
    what = np.array([np.sum(w * special.j0(k * r) * wdA) for k in ks])
    Mf = rho_f / (2 * math.pi) * integrate.trapezoid(what ** 2, ks)
    return Mf / Mp


# =====================================================================================================
# 4. Single-mode helpers (closed form, used for checks and the nonlinear-stiffening estimate)
# =====================================================================================================
def Cn(wn):
    s = np.sqrt(3 * wn); return np.arctanh(s) / s


def dCn(wn, h=1e-7):
    return (Cn(wn + h) - Cn(wn - h)) / (2 * h)


def d2Cn(wn, h=1e-5):
    return (Cn(wn + h) - 2 * Cn(wn) + Cn(wn - h)) / h ** 2


def sm_pullin(D, N, a, g_eff, t=None, c3=0.0, Pb=0.0, g_air=None):
    """Single-mode pull-in with optional cubic (stretching) stiffening k w (1 + c3 (3 w / t)^2), w = average deflection."""
    A = math.pi * a * a; k = 192 * math.pi * D / a ** 2 + 12 * math.pi * N
    wmax = (g_air if g_air else g_eff) / (3 * g_eff)
    wn = np.linspace(1e-6, min(wmax, 1 / 3) - 1e-7, 20000)
    w = wn * g_eff
    F = k * w * (1 + (c3 * (3 * w / t) ** 2 if t else 0.0)) - Pb * A
    v2 = 2 * F * g_eff ** 2 / (EPS0 * A * dCn(wn))
    v2 = np.where(F > 0, v2, -np.inf)
    i = int(np.argmax(v2))
    return math.sqrt(max(v2[i], 0)), wn[i], i >= len(wn) - 3


def kT2_soft(frac):
    """Coupling k_T^2 and spring softening k_s/k at V = frac * V_PI for the Wygant clamped-plate model."""
    wn = np.linspace(1e-6, 0.154, 200000)
    v2n = (2 * wn / dCn(wn)) / 0.148        # (V/V_PI)^2
    w = float(np.interp(frac ** 2, v2n, wn))
    Vn2 = frac ** 2 * 0.148                 # V^2 eps0 A / (k g^3)
    # all normalized by k and C0 = eps0 A / g:  n^2/(C k) = V^2 C'^2/(C k) ... in units: n = V dC/dw
    C = Cn(w); dC = dCn(w); d2C = d2Cn(w)
    ks_over_k = 1 - 0.5 * Vn2 * d2C
    n2_over_Ck = Vn2 * dC ** 2 / C
    k2 = n2_over_Ck / (ks_over_k + n2_over_Ck)
    return k2, ks_over_k, w


# =====================================================================================================
# 5. Designs to recompute (reported values from the checked model)
# =====================================================================================================
DESIGNS = [
    # name, layers(gap side first), a, g_air, t_ins, reported dict
    ("R1 Al 1um resist gap", [("Al", 1.0 * um)], 39.4317 * um, 1000 * nm, 516.2 * nm,
     dict(f_vac=1.64, f_w=0.50, V=102.0, Vs=43.4, watm=576)),
    ("R2 Au50nm/SU-8 4um", [("Au", 50 * nm), ("SU8", 4.0 * um)], 43.3043 * um, 500 * nm, 419.2 * nm,
     dict(f_vac=2.46, f_w=1.00, V=83.4, Vs=63.6, watm=119)),
    ("R3 Al 1um nanogap 100", [("Al", 1.0 * um)], 12.3 * um, 100 * nm, 221.0 * nm,
     dict(f_vac=16.86, f_w=8.38, V=43.5, Vs=41.5, watm=5.5)),
    ("R4 Al 1um nanogap 75", [("Al", 1.0 * um)], 10.7 * um, 75 * nm, 204.1 * nm,
     dict(f_vac=22.28, f_w=11.66, V=40.2, Vs=38.8, watm=3.1)),
    ("R5 Cr50nm/SiN 1um 100", [("Cr", 50 * nm), ("SiN", 1.0 * um)], 15.5 * um, 100 * nm, 220.1 * nm,
     dict(f_vac=15.80, f_w=7.54, V=43.3, Vs=41.3, watm=5.5)),
    ("R6 Al 1um a10 g200 no ins", [("Al", 1.0 * um)], 10.0 * um, 200 * nm, 0.0,
     dict(f_vac=25.5, f_w=13.7, V=129.2, Vs=127.5, watm=2.4)),
    ("R6 Al 1um a10 g100 no ins", [("Al", 1.0 * um)], 10.0 * um, 100 * nm, 0.0,
     dict(f_vac=25.5, f_w=13.7, V=45.7, Vs=44.5, watm=2.4)),
    ("R6 Al 1um a10 g50 no ins", [("Al", 1.0 * um)], 10.0 * um, 50 * nm, 0.0,
     dict(f_vac=25.5, f_w=13.7, V=16.1, Vs=15.3, watm=2.4)),
    ("R7 Al 1um a35 g1000 (air)", [("Al", 1.0 * um)], 35.0 * um, 1000 * nm, 673.0 * nm,
     dict(f_vac=2.08, f_w=0.67, V=133.1, Vs=85.6, watm=357)),
    ("R8 Al100nm/ParyC 5um", [("Al", 100 * nm), ("ParyC", 5.0 * um)], 46.9144 * um, 500 * nm, 445.3 * nm,
     dict(f_vac=2.38, f_w=1.00, V=88.1, Vs=69.1, watm=110)),
    # Table 1 rows (single-mode values reported; sealed column in Table 1 used a thinner, self-consistent t_ins)
    ("T1 0.5MHz Cr 0.5um", [("Cr", 0.5 * um)], 32.6 * um, 1334 * nm, 749 * nm,
     dict(f_vac=1.33, f_w=0.50, V=150, Vs=71, watm=0.49 * 1334)),
    ("T1 1MHz Al 1um", [("Al", 1.0 * um)], 29.7 * um, 842 * nm, 750 * nm,
     dict(f_vac=2.89, f_w=1.00, V=150, Vs=113, watm=0.22 * 842)),
    ("T1 2MHz Cr 0.3um", [("Cr", 0.3 * um)], 13.6 * um, 649 * nm, 749 * nm,
     dict(f_vac=4.57, f_w=2.00, V=150, Vs=126, watm=0.14 * 649)),
    ("T1 5MHz Al 0.6um", [("Al", 0.6 * um)], 11.3 * um, 338 * nm, 749 * nm,
     dict(f_vac=11.92, f_w=5.00, V=150, Vs=140, watm=0.05 * 338)),
    ("T1 10MHz Al 0.6um", [("Al", 0.6 * um)], 8.5 * um, 200 * nm, 749 * nm,
     dict(f_vac=21.23, f_w=10.00, V=150, Vs=144, watm=0.03 * 200)),
    ("T1 1MHz Cr 0.2um", [("Cr", 0.2 * um)], 14.3 * um, 1095 * nm, 749 * nm,
     dict(f_vac=2.77, f_w=1.00, V=150, Vs=93, watm=0.35 * 1095)),
    ("T2 air 0.5MHz Al 1um", [("Al", 1.0 * um)], 71.1 * um, 2000 * nm, 426 * nm,
     dict(f_vac=0.50, f_w=float("nan"), V=85, Vs=0, watm=3.04 * 2000)),
]


def main():
    print("=" * 100)
    print("1. CONSTANTS")
    l2 = clamped_lambda2()
    print(f"  clamped circular plate lambda^2 (root of J0 I1 + J1 I0)       = {l2:.4f}   (model 10.2158)")
    j11 = special.jn_zeros(1, 1)[0]
    print(f"  clamped-plate axisymmetric buckling j11^2                      = {j11**2:.3f}   (model 14.68)")
    G, c = lamb_coefficient()
    print(f"  Lamb AVMI Gamma (Rayleigh integral, shape (1-r^2)^2, baffled)  = {G:.4f}   (model 0.6689; Ayela&Nicu 0.67; T_L coef c = {c:.4f} vs 0.21)")
    v, wn, cpi = wygant_constants()
    print(f"  Wygant single-mode: V_PI^2 eps0 A/(k g^3) = {v:.4f} (0.148), wn_PI = {wn:.4f} (0.154), C_PI/C0 = {cpi:.3f} (1.22)")
    for nu in (0.3, 0.35, 0.21):
        print(f"  large-deflection coef (Ritz, immovable edge), nu={nu}: P a^4/64D = w0[1 + {large_deflection_coefficient(nu):.3f}(w0/t)^2]  (Timoshenko nu=0.3: 0.488, from memory)")
    for frac in (0.8, 0.9):
        k2, soft, w = kT2_soft(frac)
        print(f"  at V = {frac} V_PI: k_T^2 = {k2:.3f}, k_s/k = {soft:.3f} -> biased f / unbiased f = {math.sqrt(soft):.3f}")
    # parallel plate k_T^2 at 0.8 V_PI
    x = optimize.brentq(lambda x: x * (1 - x) ** 2 - 0.64 * 4 / 27, 0, 1 / 3)
    print(f"  parallel plate at 0.8 V_PI: x/g = {x:.4f}, k_T^2 = 2x/(g-x) = {2*x/(1-x):.3f}  (model quotes 0.28)")
    # k choice for 'piston' formulas
    print(f"  piston sqrt(8kg^3/27eps0A): k=64piD/a^2 -> ratio to Wygant {math.sqrt(8/27*64/(0.148*192)):.3f};"
          f" k=192piD/a^2 -> {math.sqrt(8/27*192/(0.148*192)):.3f}")

    print("\n  FE sanity: Al 1 um a=30 um, sigma 0 / +100 MPa / -0.9 sigma_cr")
    s = stack([("Al", 1 * um)])
    for sig in (0.0, 100 * MPa, None):
        if sig is None:
            sig = -0.9 * j11 ** 2 * s["D"] / (30 * um) ** 2 / s["t"]
        fp = FEPlate(30 * um, s["D"], s["m"], sig * s["t"], nu=0.35)
        print(f"    sigma = {sig/MPa:8.1f} MPa: f_FE = {fp.freq()/MHz:.4f} MHz  (model V2 table: 2.835 / 3.891 / 0.909)")
    fp = FEPlate(30 * um, s["D"], s["m"], 0.0, nu=0.35)
    print(f"    uniform load check: FE centre = {fp.centre_deflection(P_ATM)/nm:.3f} nm; P a^4/(64D) = {P_ATM*(30*um)**4/(64*s['D'])/nm:.3f} nm")
    print(f"    AVMI from FE mode shape: Gamma = {fluid_beta_modeshape(fp, s['m']) * s['m']/(RHO_W*30*um):.4f}")
    r = fp.pullin(200 * nm, 200 * nm)
    print(f"    pull-in Al 1um a30 g200 vented: FE {r['V']:.2f} V (model Galerkin 14.35, single-mode 14.53)")
    r = FEPlate(60 * um, *[stack([("Al", 2 * um)])[k] for k in ("D", "m")], 0.0, nu=0.35).pullin(1000 * nm, 1000 * nm)
    print(f"    pull-in Al 2um a60 g1000 vented: FE {r['V']:.2f} V (model Galerkin 113.46)")

    print("\n" + "=" * 100)
    print("2. DESIGN RECOMPUTATION (FE frequency, Lamb water, FE pull-in vented + sealed with the SAME t_ins)")
    hdr = ("design", "f_vac rep/FE", "f_w rep/FE", "beta", "V_PI vent rep/FE", "V_PI seal rep/FE", "w_atm rep/FE nm",
           "wcPI/t", "watm/t", "V_PI +stretch", "g_eff nm", "E_ins@V_PI MV/cm", "sig_cr MPa")
    print(" | ".join(hdr))
    c3 = {nu: large_deflection_coefficient(nu) for nu in (0.21, 0.22, 0.25, 0.35, 0.40)}
    rows = []
    for name, layers, a, g, tins, rep in DESIGNS:
        s = stack(layers)
        nu = MAT[layers[-1][0]]["nu"] if len(layers) > 1 else MAT[layers[0][0]]["nu"]
        fp = FEPlate(a, s["D"], s["m"], s["N"], nu=nu)
        fv = fp.freq()
        beta = 0.6689 * RHO_W * a / s["m"]
        fw = fv / math.sqrt(1 + beta)
        geff = g + tins / EPS_INS
        pv = fp.pullin(g, geff)
        ps = fp.pullin(g, geff, P_bias=P_ATM)
        watm = fp.centre_deflection(P_ATM)
        # nonlinear stretching estimate (single-mode + Ritz cubic term; layered stacks: uses nominal t, rough)
        cc = c3.get(round(nu, 2), large_deflection_coefficient(nu))
        Vlin, _, _ = sm_pullin(s["D"], s["N"], a, geff, g_air=g)
        Vnl, _, _ = sm_pullin(s["D"], s["N"], a, geff, t=s["t"], c3=cc, g_air=g)
        sig_cr = -j11 ** 2 * s["D"] / a ** 2 / s["t"]
        Eins = (pv["V"] / tins / 1e8) if tins > 0 else float("inf")
        wc_t = (pv["wc"] or float("nan")) / s["t"]
        row = [name, f"{rep['f_vac']:.2f}/{fv/MHz:.2f}", f"{rep['f_w']:.2f}/{fw/MHz:.2f}", f"{beta:.1f}",
               f"{rep['V']:.1f}/{pv['V']:.1f}{'(TD)' if pv['touchdown'] else ''}",
               f"{rep['Vs']:.1f}/{'collapsed' if ps['collapsed'] else format(ps['V'], '.1f')}",
               f"{rep['watm']:.1f}/{watm/nm:.1f}", f"{wc_t:.2f}", f"{watm/s['t']:.2f}",
               f"{Vnl:.1f} ({(Vnl/Vlin-1)*100:+.0f}%)", f"{geff/nm:.0f}", f"{Eins:.2f}", f"{sig_cr/MPa:.0f}"]
        rows.append(row)
        print(" | ".join(row))

    print("\n  R2 layered-stack detail and mode-shape AVMI:")
    s = stack([("Au", 50 * nm), ("SU8", 4.0 * um)])
    fp = FEPlate(43.3043 * um, s["D"], s["m"], s["N"], nu=0.22)
    print(f"    D = {s['D']:.4e} N m, m = {s['m']:.4e} kg/m^2, N = {s['N']:.2f} N/m, N a^2/D = {s['N']*(43.3043*um)**2/s['D']:.2f}")
    bm = fluid_beta_modeshape(fp, s["m"])
    print(f"    beta Lamb = {0.6689*RHO_W*43.3043*um/s['m']:.3f}; beta from FE mode shape = {bm:.3f}; f_w(mode-shape beta) = {fp.freq()/math.sqrt(1+bm)/MHz:.3f} MHz")
    fp0 = FEPlate(43.3043 * um, s["D"], s["m"], 0.0, nu=0.22)
    print(f"    without SU-8 tension: f_vac = {fp0.freq()/MHz:.3f} MHz, f_w = {fp0.freq()/math.sqrt(1+0.6689*RHO_W*43.3043*um/s['m'])/MHz:.3f} MHz")

    print("\n  Table-1 sealed-column consistency (same t_ins as vented vs thinner self-consistent t_ins):")
    for name, layers, a, g, tins, rep in DESIGNS[10:16]:
        s = stack(layers); nu = MAT[layers[0][0]]["nu"]
        fp = FEPlate(a, s["D"], s["m"], s["N"], nu=nu)
        ps_same = fp.pullin(g, g + tins / EPS_INS, P_bias=P_ATM)["V"]
        t2 = rep["Vs"] / 2e8
        ps_thin = fp.pullin(g, g + t2 / EPS_INS, P_bias=P_ATM)["V"]
        print(f"    {name}: reported {rep['Vs']}, FE same t_ins {ps_same:.1f}, FE with t_ins = V_s/(2 MV/cm) = {t2/nm:.0f} nm: {ps_thin:.1f}")

    print("\n  Capillary ratio recheck R = (2 gamma/g)/(64 D g/a^4), gamma = 0.023 N/m, and piston-analog threshold:")
    for name, layers, a, g, tins, rep in DESIGNS[:10]:
        s = stack(layers)
        k = 192 * math.pi * s["D"] / a ** 2 + 12 * math.pi * s["N"]
        R = (2 * 0.023 / g) / (k * g / 3 / (math.pi * a * a))
        print(f"    {name}: R = {R:.3f}")

    print("\n  Squeeze/gas-spring stiffening for VENTED air operation (isothermal P0/g vs plate 192D/a^4 per area):")
    for name, layers, a, g, tins, rep in (DESIGNS[0], DESIGNS[8], DESIGNS[16]):
        s = stack(layers); mu = 1.8e-5
        f = rep["f_vac"] * MHz
        sq = 12 * mu * 2 * math.pi * f * a * a / (P_ATM * g * g)
        kp = 192 * s["D"] / a ** 4; kg = P_ATM / g
        print(f"    {name}: squeeze number {sq:.0f}; gas/plate stiffness {kg/kp:.2f} (isothermal) -> f x {math.sqrt(1+kg/kp):.3f}"
              f" (adiabatic {math.sqrt(1+1.4*kg/kp):.3f}) if the cavity air is trapped at f")


if __name__ == "__main__":
    main()

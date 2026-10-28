"""Physics core for a clamped circular CMUT cell (small-deflection plate theory).

Models (sources in validate.py / README text returned to the orchestrator):
  * Layered plate: D = sum E'_i [t_i^3/12 + t_i (z_i - z_n)^2], E' = E/(1-nu^2); m'' = sum rho_i t_i;
    in-plane force N = sum sigma_i t_i (biaxial residual stress, + tensile).
  * Exact lowest axisymmetric frequency of a uniform clamped plate under in-plane force N, from
    D lap^2 w - N lap w - m'' w_tt = 0  ->  w = A J0(alpha r) + B I0(beta r),
    clamped edge -> alpha J1(alpha a) I0(beta a) + beta J0(alpha a) I1(beta a) = 0.
    N = 0 recovers lambda^2 = 10.2158 (Leissa NASA SP-160), N -> inf recovers the membrane 2.405,
    N -> -14.68 D/a^2 recovers clamped-plate buckling (f -> 0).
  * Rayleigh-Ritz / Galerkin with basis (1-rho^2)^2 rho^(2n-2) for piecewise-radial stacks (partial
    electrodes) and multi-mode electrostatic pull-in (reference solution).
  * Single-mode electrostatics of Wygant, Kupnik & Khuri-Yakub (IUS 2008, doi:10.1109/ULTSYM.2008.0522;
    JMEMS 27, 448, 2018, doi:10.1109/JMEMS.2018.2823200; IUS 2019 digest): shape 3(1-r^2/a^2)^2 so the
    lumped coordinate is the AVERAGE deflection; C = (eps0 A/g) atanh(sqrt(3 wn))/sqrt(3 wn);
    V_PI = sqrt(0.148 k g^3/(eps0 A)) with k = 192 pi D/a^2 (+ 12 pi N for tension), wn_PI = 0.154.
  * Fluid loading: Lamb (1920, doi:10.1098/rspa.1920.0064) added-virtual-mass factor
    beta = 0.6689 rho_f a / m'' (one face wetted, baffled), f_fluid = f_vac / sqrt(1+beta).
"""
from __future__ import annotations

import numpy as np
from scipy import linalg, optimize, special

from materials import EPS0, Material

J0Z = float(special.jn_zeros(0, 1)[0])   # 2.404826 (membrane)
J1Z = float(special.jn_zeros(1, 1)[0])   # 3.831706 (clamped-plate buckling: N_cr = J1Z^2 D/a^2 = 14.68 D/a^2)
LAMB_GAMMA = 0.6689                      # Lamb 1920 AVMI coefficient (0.67 rounded in Ayela & Nicu, arXiv:0906.3616)


# ----------------------------------------------------------------------------------------------
# Layered stacks
# ----------------------------------------------------------------------------------------------
def stack_props(layers: list[tuple[Material, float]], sigma_override: float | None = None) -> dict:
    """layers: (Material, thickness [m]) from the gap side upward.
    Returns flexural rigidity D [N m], areal mass m [kg/m^2], in-plane force N [N/m], nu, total t."""
    z, rows = 0.0, []
    for mat, t in layers:
        rows.append((mat.E / (1 - mat.nu ** 2), t, z + t / 2, mat))
        z += t
    zn = sum(Ep * t * zc for Ep, t, zc, _ in rows) / sum(Ep * t for Ep, t, _, _ in rows)
    D = sum(Ep * (t ** 3 / 12 + t * (zc - zn) ** 2) for Ep, t, zc, _ in rows)
    m = sum(mat.rho * t for _, t, _, mat in rows)
    if sigma_override is None:
        N = sum(mat.sigma * t for _, t, _, mat in rows)
    else:
        N = sigma_override * z
    nu = sum(mat.nu * mat.E * t for _, t, _, mat in rows) / sum(mat.E * t for _, t, _, mat in rows)
    return dict(D=D, m=m, N=N, nu=nu, t=z)


def plate_D(E: float, nu: float, t: float) -> float:
    return E * t ** 3 / (12 * (1 - nu ** 2))


# ----------------------------------------------------------------------------------------------
# Frequencies
# ----------------------------------------------------------------------------------------------
def N_buckle(D: float, a: float) -> float:
    """Critical uniform radial compression of a clamped circular plate (axisymmetric mode) [N/m]."""
    return J1Z ** 2 * D / a ** 2


def _char(Om: float, k2: float) -> float:
    s = np.sqrt(k2 ** 2 + 4 * Om ** 2)
    if k2 >= 0:
        A2, B2 = 2 * Om ** 2 / (k2 + s), (k2 + s) / 2
    else:
        A2, B2 = (s - k2) / 2, 2 * Om ** 2 / (s - k2)
    al, be = np.sqrt(A2), np.sqrt(B2)
    return al * special.j1(al) + be * special.j0(al) * special.i1e(be) / special.i0e(be)


def omega_param(k2: float) -> float:
    """Nondimensional frequency Omega = omega a^2 sqrt(m/D) for tension parameter k2 = N a^2/D."""
    if k2 <= -J1Z ** 2:
        return float("nan")
    if k2 == 0.0 and _OMEGA0 is not None:
        return _OMEGA0
    guess = np.sqrt(10.2158 ** 2 + (J0Z ** 2) * max(k2, 0.0)) if k2 >= 0 else 10.2158 * np.sqrt(1 + k2 / J1Z ** 2)
    grid = np.geomspace(max(guess, 1e-6) * 1e-3, max(guess, 1e-3) * 4, 400)
    vals = np.array([_char(o, k2) for o in grid])
    idx = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
    if len(idx) == 0:
        return float("nan")
    i = idx[0]
    return optimize.brentq(_char, grid[i], grid[i + 1], args=(k2,), xtol=1e-12)


_OMEGA0 = None
_OMEGA0 = omega_param(0.0)   # 10.2158, cached


def f_exact(D: float, m: float, N: float, a: float) -> float:
    """Exact lowest axisymmetric resonance [Hz] (vacuum) of a uniform clamped plate with in-plane force N."""
    k2 = N * a ** 2 / D
    Om = omega_param(k2)
    return Om / (2 * np.pi * a ** 2) * np.sqrt(D / m)


def f_plate(D: float, m: float, a: float) -> float:
    return 10.2158 / (2 * np.pi * a ** 2) * np.sqrt(D / m)


def f_membrane(N: float, m: float, a: float) -> float:
    return J0Z / (2 * np.pi * a) * np.sqrt(max(N, 0.0) / m)


def f_rss(D: float, m: float, N: float, a: float) -> float:
    """Common approximation f^2 ~ f_plate^2 + f_membrane^2 (tension only)."""
    return np.sqrt(f_plate(D, m, a) ** 2 + f_membrane(N, m, a) ** 2)


def lamb_beta(rho_f: float, a: float, m: float) -> float:
    return LAMB_GAMMA * rho_f * a / m


def f_fluid(f_vac: float, rho_f: float, a: float, m: float) -> float:
    return f_vac / np.sqrt(1 + lamb_beta(rho_f, a, m))


# ----------------------------------------------------------------------------------------------
# Rayleigh-Ritz / Galerkin model (piecewise-radial stacks, partial electrode)
# ----------------------------------------------------------------------------------------------
class RitzPlate:
    """Axisymmetric clamped plate, radius a, with radial regions [(rho_out, D, m, N, nu), ...]."""

    def __init__(self, a: float, regions: list[tuple[float, float, float, float, float]],
                 nbasis: int = 6, kind: str = "plate", nq: int = 48):
        self.a, self.regions, self.nb, self.kind = a, regions, nbasis, kind
        # basis as polynomial terms in rho: list of (coef, power)
        if kind == "plate":      # (1-r^2)^2 r^(2p): clamped (w=w'=0 at edge)
            self.terms = [[(1, 2 * p), (-2, 2 * p + 2), (1, 2 * p + 4)] for p in range(nbasis)]
        else:                    # membrane: (1-r^2) r^(2p): w=0 at edge only
            self.terms = [[(1, 2 * p), (-1, 2 * p + 2)] for p in range(nbasis)]
        xg, wg = np.polynomial.legendre.leggauss(nq)
        K = np.zeros((nbasis, nbasis))
        M = np.zeros((nbasis, nbasis))
        r_in = 0.0
        for (r_out, D, m, N, nu) in regions:
            r = 0.5 * (r_out - r_in) * xg + 0.5 * (r_out + r_in)
            w = 0.5 * (r_out - r_in) * wg
            ph, d1, d2, d1r = self._eval(r)
            lap = d2 + d1r
            for i in range(nbasis):
                for j in range(nbasis):
                    bend = lap[i] * lap[j] - (1 - nu) * (d2[i] * d1r[j] + d2[j] * d1r[i])
                    K[i, j] += 2 * np.pi / a ** 2 * np.sum(D * bend * r * w) + 2 * np.pi * np.sum(N * d1[i] * d1[j] * r * w)
                    M[i, j] += 2 * np.pi * a ** 2 * np.sum(m * ph[i] * ph[j] * r * w)
            r_in = r_out
        self.K, self.M = K, M
        r = 0.5 * xg + 0.5
        ph = self._eval(r)[0]
        self.avec = np.array([2 * np.pi * a ** 2 * np.sum(ph[i] * r * 0.5 * wg) for i in range(nbasis)])
        self.area = np.pi * a ** 2

    def _eval(self, r):
        r = np.asarray(r, dtype=float)
        ph = np.zeros((self.nb, r.size)); d1 = np.zeros_like(ph); d2 = np.zeros_like(ph); d1r = np.zeros_like(ph)
        for i, terms in enumerate(self.terms):
            for c, q in terms:
                ph[i] += c * r ** q
                if q >= 1:
                    d1[i] += c * q * r ** (q - 1)
                    d1r[i] += c * q * r ** (q - 2)
                if q >= 2:
                    d2[i] += c * q * (q - 1) * r ** (q - 2)
        return ph, d1, d2, d1r

    # -- dynamics --
    def freq(self) -> tuple[float, np.ndarray]:
        evals = linalg.eigh(self.K, eigvals_only=True)
        if evals.min() <= 0:
            return float("nan"), np.full(self.nb, np.nan)
        w2, vec = linalg.eigh(self.K, self.M)
        return float(np.sqrt(w2[0]) / (2 * np.pi)), vec[:, 0]

    def modal_areal_mass(self, vec: np.ndarray) -> float:
        """sum(m phi^2 dA)/sum(phi^2 dA) for the computed mode -> used in Lamb's beta."""
        xg, wg = np.polynomial.legendre.leggauss(96)
        num = den = 0.0
        r_in = 0.0
        for (r_out, D, m, N, nu) in self.regions:
            r = 0.5 * (r_out - r_in) * xg + 0.5 * (r_out + r_in)
            w = 0.5 * (r_out - r_in) * wg
            shape = vec @ self._eval(r)[0]
            num += np.sum(m * shape ** 2 * r * w)
            den += np.sum(shape ** 2 * r * w)
            r_in = r_out
        return num / den

    # -- statics --
    def static_center_deflection(self, P: float) -> float:
        c = linalg.solve(self.K, P * self.avec)
        return float(c[0])

    def pullin(self, g_air: float, g_eff: float, rho_e: float = 1.0, P_bias: float = 0.0,
               nsteps: int = 80, nq: int = 160) -> dict:
        """Displacement-controlled multi-mode Galerkin pull-in (reference solution).
        w positive toward the substrate; contact when center deflection = g_air (insulator surface)."""
        xg, wg = np.polynomial.legendre.leggauss(nq)
        r = 0.5 * rho_e * (xg + 1)
        wq = 0.5 * rho_e * wg
        ph = self._eval(r)[0]
        pref = 0.5 * EPS0 * 2 * np.pi * self.a ** 2

        def fvec(c):
            wdef = c @ ph
            return pref * (ph / (g_eff - wdef) ** 2) @ (r * wq)

        c_b = linalg.solve(self.K, P_bias * self.avec)
        wc0 = c_b[0]
        if wc0 >= g_air:
            return dict(V_PI=0.0, collapsed_by_bias=True, w_center_bias=wc0, touchdown=False)
        # nondimensionalize: lengths by g_eff, voltage^2 by k11 g^3/(eps0 A), forces by k11 g
        L = g_eff
        lam_ref = self.K[0, 0] * L ** 3 / (EPS0 * self.area)
        F_ref = self.K[0, 0] * L
        y = np.concatenate([c_b[1:] / L, [1e-3]])
        best = (-1.0, None)
        wcs = wc0 + (g_air * 0.999 - wc0) * np.linspace(0.01, 1.0, nsteps)
        for wc in wcs:
            def res(yy):
                c = np.concatenate([[wc], yy[:-1] * L])
                return (self.K @ c - P_bias * self.avec - yy[-1] * lam_ref * fvec(c)) / F_ref
            sol = optimize.root(res, y, method="hybr", options=dict(xtol=1e-12))
            if not sol.success or np.max(np.abs(sol.fun)) > 1e-8:
                sol = optimize.root(res, y, method="lm", options=dict(xtol=1e-14, ftol=1e-14))
                if not sol.success or np.max(np.abs(sol.fun)) > 1e-8:
                    break
            y = sol.x
            lam = y[-1] * lam_ref
            if lam > best[0]:
                best = (lam, wc)
            elif lam < 0.9 * best[0]:
                break
        if best[1] is None:
            return dict(V_PI=float("nan"), collapsed_by_bias=False, w_center_bias=wc0, touchdown=False)
        touchdown = best[1] >= wcs[-1] * 0.999
        return dict(V_PI=float(np.sqrt(max(best[0], 0))), w_center_PI=best[1], collapsed_by_bias=False,
                    w_center_bias=wc0, touchdown=bool(touchdown))


# ----------------------------------------------------------------------------------------------
# Single-mode (Wygant) electrostatics, average-deflection coordinate
# ----------------------------------------------------------------------------------------------
def G_plate(wn, rho_e=1.0):
    """Normalized capacitance C/(eps0 pi a^2/g_eff) for shape 3(1-rho^2)^2, electrode radius rho_e*a."""
    s = np.sqrt(3 * np.asarray(wn, dtype=float))
    ue = 1 - rho_e ** 2
    return (np.arctanh(s) - np.arctanh(s * ue)) / s


def dG_plate(wn, rho_e=1.0):
    s = np.sqrt(3 * np.asarray(wn, dtype=float))
    ue = 1 - rho_e ** 2
    num = (1 / (1 - s ** 2) - ue / (1 - (s * ue) ** 2)) * s - (np.arctanh(s) - np.arctanh(s * ue))
    return num / s ** 2 * 1.5 / s


def G_mem(wn, rho_e=1.0):
    """Same for membrane shape 2(1-rho^2)."""
    x = 2 * np.asarray(wn, dtype=float)
    ue = 1 - rho_e ** 2
    return (np.log(1 - x * ue) - np.log(1 - x)) / x


def dG_mem(wn, rho_e=1.0, h=1e-7):
    return (G_mem(wn + h, rho_e) - G_mem(wn - h, rho_e)) / (2 * h)


def k_avg(D: float, N: float, a: float, shape: str = "plate") -> float:
    """Lumped stiffness referred to AVERAGE deflection."""
    if shape == "plate":
        return 192 * np.pi * D / a ** 2 + 12 * np.pi * N
    return 8 * np.pi * N            # tension-dominated membrane, parabolic shape (exact for uniform load)


def m_avg(m: float, a: float, shape: str = "plate") -> float:
    return (1.8 if shape == "plate" else 4.0 / 3.0) * m * np.pi * a ** 2


class SingleMode:
    """Lumped single-mode CMUT cell (Wygant shape function), w = average deflection."""

    def __init__(self, D, m, N, a, g_air, g_eff, rho_e=1.0, P_bias=0.0, shape="plate"):
        self.D, self.m, self.N, self.a = D, m, N, a
        self.g_air, self.g, self.rho_e, self.Pb, self.shape = g_air, g_eff, rho_e, P_bias, shape
        self.A = np.pi * a ** 2
        self.k = k_avg(D, N, a, shape)
        self.G = (lambda w: G_plate(w, rho_e)) if shape == "plate" else (lambda w: G_mem(w, rho_e))
        self.dG = (lambda w: dG_plate(w, rho_e)) if shape == "plate" else (lambda w: dG_mem(w, rho_e))
        cfac = 3.0 if shape == "plate" else 2.0        # center/average deflection ratio
        self.wn_contact = min(g_air / (cfac * g_eff), 1 / cfac - 1e-9)
        self.wn_bias = P_bias * self.A / (self.k * g_eff) if self.k > 0 else np.inf
        self._solve()

    def V2(self, wn):
        return 2 * (self.k * wn * self.g - self.Pb * self.A) * self.g ** 2 / (EPS0 * self.A * self.dG(wn))

    def _solve(self):
        self.collapsed_by_bias = self.wn_bias >= self.wn_contact
        if self.collapsed_by_bias or self.k <= 0:
            self.V_PI, self.wn_PI, self.touchdown = 0.0, np.nan, False
            return
        lo = max(self.wn_bias, 1e-7)
        wn = np.linspace(lo, self.wn_contact - 1e-6, 4000)[1:]
        with np.errstate(invalid='ignore', divide='ignore'):
            v2 = self.V2(wn)
        v2 = np.where(np.isfinite(v2), v2, -np.inf)
        i = int(np.argmax(v2))
        self.V_PI = float(np.sqrt(v2[i]))
        self.wn_PI = float(wn[i])
        self.touchdown = i >= len(wn) - 2       # still rising at contact: plate lands on insulator
        self._wn_branch, self._v2_branch = wn[: i + 1], v2[: i + 1]

    def operating_point(self, V: float) -> float:
        if V >= self.V_PI:
            return float("nan")
        return float(np.interp(V ** 2, self._v2_branch, self._wn_branch))

    def small_signal(self, V: float, rho_f: float = 1000.0, c_f: float = 1500.0, Cp: float = 0.0) -> dict:
        wn = self.operating_point(V)
        h = 1e-6
        C = EPS0 * self.A / self.g * self.G(wn)
        dC = EPS0 * self.A / self.g ** 2 * self.dG(wn)
        d2C = EPS0 * self.A / self.g ** 3 * (self.dG(wn + h) - self.dG(wn - h)) / (2 * h)
        n = V * dC                                   # transformer ratio [C/m] = [N/V]
        ks = self.k - 0.5 * V ** 2 * d2C            # short-circuit (constant-V) stiffness
        k2 = n ** 2 / (C * ks + n ** 2)               # coupling coefficient (= 1 - C_S/C_T)
        Ct = C + Cp
        S_oc = (n / Ct) * self.A / (ks + n ** 2 / Ct)  # static open-circuit receive sensitivity [V/Pa]
        S_i = 2 * n / (rho_f * c_f)                   # in-band immersed short-circuit current [A/Pa], blocked-pressure x2
        return dict(wn=wn, C=C, n=n, ks=ks, k2=k2, S_oc=S_oc, S_i=S_i,
                    E_gap=V / (self.g - wn * self.g * (3 if self.shape == "plate" else 2)),
                    soft=ks / self.k)

    def V_PI_piston(self, which: str) -> float:
        """Textbook parallel-plate formula V = sqrt(8 k g^3/(27 eps0 A)) with two common k choices."""
        if which == "uniform_load_64D":     # k = (64 D/a^4) * A  (center-deflection stiffness under uniform load)
            k = 64 * np.pi * self.D / self.a ** 2 + 4 * np.pi * self.N
        else:                              # k referred to average deflection (192 pi D / a^2)
            k = self.k
        return float(np.sqrt(8 * k * self.g ** 3 / (27 * EPS0 * self.A)))

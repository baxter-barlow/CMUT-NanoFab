"""Array-level numbers: full fUS probe spec vs. student 16-element slice; receive-beamforming robustness (Monte Carlo);
quasi-static displacement responsivity for the interferometer test; sealed (Al-plug) cell in oil."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
import numpy as np
import cmut, fus_cell as F
from materials import P_ATM, EPS0
um, nm, MHz = 1e-6, 1e-9, 1e6
rng = np.random.default_rng(1)
out = {}
# ---- 1. full fUS probe (anchored to Griggs et al. 2024: 128 el, 15.6 MHz, 0.1 mm pitch) ----
c_t = 1540.0
f = 15.6e6; lam = c_t/f; p = 100e-6; N = 128; D = N*p
out["full_probe"] = dict(f_MHz=15.6, lambda_um=lam/um, pitch_um=100, pitch_over_lambda=p/lam, lambda_half_um=lam/2/um,
    N=N, aperture_mm=D*1e3,
    lateral_res_um_at_5mm=lam*5e-3/D/um, lateral_res_um_at_10mm=lam*10e-3/D/um,
    axial_res_um_FBW100=c_t/(2*1.0*f)/um, axial_res_um_FBW60=c_t/(2*0.6*f)/um,
    gratinglobe_free_steer_deg_pitch100=float(np.degrees(np.arcsin(max(lam/p-1, -1)))) if lam/p>1 else 0.0,
    elements_needed_lambda_half_same_aperture=int(np.ceil(D/(lam/2))))
# ---- 2. student slice ----
c_o = 1468.0
for fs in (10e6, 12e6, 15e6):
    l = c_o/fs; Ns = 16; Ds = Ns*p
    out[f"slice_oil_{int(fs/1e6)}MHz"] = dict(lambda_um=l/um, pitch_over_lambda=p/l, aperture_mm=Ds*1e3,
        angular_res_deg=float(np.degrees(l/Ds)), lateral_FWHM_mm_at_5mm=0.886*l*5e-3/Ds*1e3,
        unambiguous_window_deg=float(np.degrees(np.arcsin(min(1, l/(2*p))))),
        far_field_start_mm=Ds**2/l*1e3)
# ---- 3. Monte Carlo receive DAS beam (16 el, 12 MHz oil), source at 15 deg in far field ----
def beam(theta_scan, theta0, w, phi, l=c_o/12e6, Ns=16):
    x = (np.arange(Ns) - (Ns-1)/2)*p
    k = 2*np.pi/l
    sig = w*np.exp(1j*(k*x*np.sin(theta0) + phi))
    steer = np.exp(-1j*k*np.outer(np.sin(theta_scan), x))
    return np.abs(steer @ sig)
th = np.radians(np.linspace(-60, 60, 4801))
th0 = np.radians(15.0)
ideal = beam(th, th0, np.ones(16), np.zeros(16)); ideal_pk = ideal.max()
def metrics(b):
    i = np.argmax(b); pk = b[i]
    # main lobe region: within first nulls approx +-lambda/D in sin space around peak
    s = np.sin(th); s0 = s[i]; mask = np.abs(s - s0) > (c_o/12e6)/(16*p)*1.0
    psl = 20*np.log10(b[mask].max()/pk)
    return np.degrees(th[i]), 20*np.log10(pk/ideal_pk), psl
res = {}
res["ideal"] = dict(zip(("peak_deg","gain_dB","PSL_dB"), metrics(ideal)))
for label, sa, sp, ndead in (("amp20_phase0.1", 0.2, 0.1, 0), ("amp20_phase0.3", 0.2, 0.3, 0),
                             ("amp20_phase0.1_dead2", 0.2, 0.1, 2), ("amp20_phase0.1_dead4", 0.2, 0.1, 4),
                             ("amp30_phase0.5_dead4", 0.3, 0.5, 4)):
    vals = []
    for _ in range(2000):
        w = np.clip(1 + sa*rng.standard_normal(16), 0, None)
        if ndead: w[rng.choice(16, ndead, replace=False)] = 0
        phi = sp*rng.standard_normal(16)
        vals.append(metrics(beam(th, th0, w, phi)))
    v = np.array(vals)
    res[label] = dict(angle_err_deg_rms=float(np.sqrt(np.mean((v[:,0]-15)**2))), gain_dB_mean=float(v[:,1].mean()),
                      PSL_dB_median=float(np.median(v[:,2])), PSL_dB_p90=float(np.percentile(v[:,2], 90)))
out["MC_receive_DAS_16el_12MHz_src15deg"] = res
# phase error from resonance spread for a radiation-damped element: dphi ~ 2 Q df/f at band centre
out["phase_from_freq_spread"] = {f"Q={Q}, df/f={d}": 2*Q*d for Q in (0.5, 1.0) for d in (0.05, 0.10)}
# ---- 4. quasi-static displacement responsivity (interferometer test), baseline a=11 um, vented, in air ----
a, g = 11*um, 80*nm
pr, _ = F.stack(2.0*um, t_ox_mem=0.10*um)
geff = g + 0.05*um/3.9 + 0.10*um/3.9
sm = cmut.SingleMode(pr["D"], pr["m"], pr["N"], a, g, geff)
qs = {}
for V in (20.0, 30.0, 40.0):
    ss = sm.small_signal(V)
    x_avg_per_V = ss["n"]/ss["ks"]
    qs[f"{V:.0f}V"] = dict(center_nm_per_Vac=3*x_avg_per_V/nm, static_center_nm=3*ss["wn"]*geff/nm,
                           fringe_fraction_per_Vac_633nm=4*np.pi*3*x_avg_per_V/633e-9/2)  # at quadrature dI/Ipp = (2pi/lambda)*2x/2
out["quasi_static_responsivity_a11"] = qs
out["V_PI_a11_vented"] = sm.V_PI
json.dump(out, open("fus_array.json", "w"), indent=1, default=float)
def pr_(d, ind=""):
    for k, v in d.items():
        if isinstance(v, dict): print(ind+k); pr_(v, ind+"   ")
        else: print(f"{ind}{k}: {v:.4g}" if isinstance(v, (float, np.floating, int)) else f"{ind}{k}: {v}")
pr_(out)

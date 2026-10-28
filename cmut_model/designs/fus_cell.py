"""Cell + element design for the 'fUS-slice' nanogap CMUT linear array (6.2540, app-first concept).
Uses the validated model in ../cmut_model (Wygant single-mode + Galerkin pull-in, exact tensioned plate, Lamb).
Stack (gap side first): evaporated SiO2 (membrane insulator) / Ti-Au top electrode / spin-coated SU-8 [/ optional sputtered SiO2 seal].
Bottom: Ti/Au electrode + evaporated SiO2 insulator on glass. Gap = evaporated Cr sacrificial thickness.
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cmut_model"))
import numpy as np
import cmut
from materials import Material, MATERIALS as M, EPS0, P_ATM, WATER, GAMMA_IPA

um, nm, MHz, GPa, MPa = 1e-6, 1e-9, 1e6, 1e9, 1e6
# ASSUMED evaporated SiO2 constants (bulk fused-silica-like); stress unknown -> swept
SIO2 = Material("SiO2 (e-beam evap.)", 70*GPa, 0.17, 2200, 0.0, 3.9, "ASSUMED bulk fused silica values; evaporated films lower/variable")
RHO_OIL, C_OIL = 923.0, 1468.0   # vegetable oil values used by Seok 2021 (digest)

def stack(t_su8, t_ox_mem=0.15*um, t_au=0.05*um, t_seal=0.0, sig_ox=0.0, seal_mat=SIO2):
    ox = Material(SIO2.name, SIO2.E, SIO2.nu, SIO2.rho, sig_ox, SIO2.eps_r, SIO2.src)
    layers = [(ox, t_ox_mem), (M["Au"], t_au), (M["SU8"], t_su8)]
    if t_seal > 0:
        layers.append((Material(seal_mat.name, seal_mat.E, seal_mat.nu, seal_mat.rho, sig_ox, seal_mat.eps_r, ""), t_seal))
    return cmut.stack_props(layers), t_ox_mem

def cell(a, g_air, t_su8=2.0*um, t_ins=0.08*um, t_seal=0.0, sig_ox=0.0, rho_f=1000.0, c_f=1500.0, galerkin=False):
    p, t_oxm = stack(t_su8, t_seal=t_seal, sig_ox=sig_ox)
    g_eff = g_air + t_ins/SIO2.eps_r + t_oxm/SIO2.eps_r
    fv = cmut.f_exact(p["D"], p["m"], p["N"], a)
    fw = cmut.f_fluid(fv, rho_f, a, p["m"])
    beta = cmut.lamb_beta(rho_f, a, p["m"])
    k = cmut.k_avg(p["D"], p["N"], a)
    R = (2*GAMMA_IPA/g_air)/(64*p["D"]*g_air/a**4 + 4*p["N"]*g_air/a**2)
    vent = cmut.SingleMode(p["D"], p["m"], p["N"], a, g_air, g_eff)
    seal = cmut.SingleMode(p["D"], p["m"], p["N"], a, g_air, g_eff, P_bias=P_ATM)
    w_atm = 3*P_ATM*np.pi*a**2/k
    sig_cr = -cmut.N_buckle(p["D"], a)/p["t"]
    out = dict(a_um=a/um, g_nm=g_air/nm, g_eff_nm=g_eff/nm, t_tot_um=p["t"]/um, D=p["D"], m=p["m"], N=p["N"],
               f_vac_MHz=fv/MHz, f_water_MHz=fw/MHz, beta=beta, R_capillary=R,
               V_PI_vent=vent.V_PI, V_PI_seal=seal.V_PI, touchdown_vent=vent.touchdown,
               w_atm_center_nm=w_atm/nm, w_atm_over_g=w_atm/g_air, sigma_cr_MPa=sig_cr/MPa)
    for tag, sm in (("vent", vent), ("seal", seal)):
        if sm.V_PI > 0:
            V = 0.8*sm.V_PI
            ss = sm.small_signal(V, rho_f=rho_f, c_f=c_f)
            A = np.pi*a**2
            out.update({f"{tag}_Vop": V, f"{tag}_C0_fF": ss["C"]*1e15, f"{tag}_n_uN_per_V": ss["n"]*1e6,
                        f"{tag}_kT2": ss["k2"], f"{tag}_Si_nA_per_kPa": ss["S_i"]*1e9*1e3,
                        f"{tag}_soft": ss["soft"], f"{tag}_TX_kPa_per_V_cellarea": ss["n"]/A/1e3,
                        f"{tag}_field_contact_MVcm": sm.V_PI/((t_ins+t_oxm))/1e8})
    if galerkin:
        rp = cmut.RitzPlate(a, [(1.0, p["D"], p["m"], p["N"], p["nu"])])
        out["V_PI_vent_galerkin"] = rp.pullin(g_air, g_eff)["V_PI"]
        out["V_PI_seal_galerkin"] = rp.pullin(g_air, g_eff, P_bias=P_ATM)["V_PI"]
    return out

if __name__ == "__main__":
    print("== radius sweep, SU-8 2.0 um, gap 80 nm, bottom SiO2 80 nm, vented & sealed(vacuum) ==")
    hdr = "a  f_vac f_w(water) beta  R    VPIv  VPIs  w_atm/g  sig_cr  C0fF  kT2  Si(nA/kPa) TXkPa/V"
    print(hdr)
    for a in [7,8,9,10,11,12,13,14]:
        c = cell(a*um, 80*nm)
        print(f"{a:2d} {c['f_vac_MHz']:5.1f} {c['f_water_MHz']:5.2f} {c['beta']:5.2f} {c['R_capillary']:5.2f} "
              f"{c['V_PI_vent']:5.1f} {c['V_PI_seal']:5.1f} {c['w_atm_over_g']:6.3f} {c['sigma_cr_MPa']:7.0f} "
              f"{c['vent_C0_fF']:5.1f} {c['vent_kT2']:.2f} {c['vent_Si_nA_per_kPa']:6.1f} {c['vent_TX_kPa_per_V_cellarea']:5.1f}")
    print("\n== SU-8 thickness sweep at a=10 um, gap 80 nm ==")
    for t in [1.5, 2.0, 2.4, 3.0]:
        c = cell(10*um, 80*nm, t_su8=t*um)
        print(f"t_su8={t}: f_w={c['f_water_MHz']:.2f} R={c['R_capillary']:.2f} VPIv={c['V_PI_vent']:.1f} VPIs={c['V_PI_seal']:.1f}")

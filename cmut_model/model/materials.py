"""Thin-film material database for the CMUT design-space study (6.2540 final project).

Every number is either (a) taken from a source located during this study (URL/DOI in `src`),
or (b) a standard bulk handbook value / explicit assumption, marked "ASSUMED" in `src`.
Thin-film moduli are often 10-50 % below bulk and depend strongly on deposition conditions,
so the sweeps in design_space.py treat E and sigma as uncertain.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Material:
    name: str
    E: float          # Young's modulus [Pa]
    nu: float         # Poisson ratio [-]
    rho: float        # density [kg/m^3]
    sigma: float      # nominal residual (biaxial) stress [Pa], + = tensile
    eps_r: float      # relative permittivity (dielectrics); 0 for conductors
    src: str          # provenance


GPa, MPa = 1e9, 1e6

MATERIALS: dict[str, Material] = {
    # --- metals -------------------------------------------------------------------------------
    "Al": Material("Al (sputtered/evap.)", 70 * GPa, 0.35, 2700, 0.0, 0.0,
                   "ASSUMED bulk handbook E/nu/rho; residual stress process-dependent (swept)"),
    "Cr": Material("Cr (sputtered/evap.)", 250 * GPa, 0.21, 7190, 0.0, 0.0,
                   "ASSUMED (bulk E~279 GPa; films lower). Evaporated Cr typically highly tensile - swept"),
    "Au": Material("Au (evap.)", 79 * GPa, 0.42, 19300, 0.0, 0.0, "ASSUMED bulk handbook values"),
    # --- polymers -----------------------------------------------------------------------------
    "SU8": Material("SU-8 (hard-baked)", 4.0 * GPa, 0.22, 1190, 17 * MPa, 4.1,
                    "E: 2.0 GPa Kayaku table (kayakuam.com SU-8 table of properties) to 4.02 GPa "
                    "(MIT 6.777 matprops, web.mit.edu/6.777/www/matprops/su-8.htm); rho 1190, nu 0.22, "
                    "sigma 16-19 MPa (MIT 6.777); eps_r 4.1 @1 GHz SU-8 2000 (Kayaku). 4.0 GPa chosen "
                    "because it reproduces the Gerardo 2018 atmospheric deflection (validate.py)"),
    "ParyC": Material("Parylene C", 2.8 * GPa, 0.40, 1289, 0.0, 3.0,
                      "E 2.8-3.2 GPa, rho 1.289 g/cm3, eps_r 3.15 (60 Hz)-2.95 (1 MHz): vendor TDS "
                      "(hzo.com Parylene C datasheet; knowde VSI Parylene C). nu ASSUMED. CVD deposition "
                      "is REQUIRES-STAFF-APPROVAL"),
    # --- sputtered dielectrics ----------------------------------------------------------------
    "SiN": Material("SiNx (reactive sputtered)", 150 * GPa, 0.25, 2700, 0.0, 7.0,
                    "E 100-210 GPa by nanoindentation for sputtered SiNx (Vila et al., JAP 94, 7868, 2003, "
                    "doi:10.1063/1.1626799); rho, nu, eps_r ASSUMED; stress often compressive - swept"),
    "Al2O3": Material("Al2O3 (sputtered, amorphous)", 120 * GPa, 0.24, 3000, 0.0, 8.0,
                      "E of amorphous sputtered alumina ~100-170 GPa and halves with deposition pressure "
                      "(van der Rest et al., Acta Mater. 125, 27, 2017, doi:10.1016/j.actamat.2016.11.037); "
                      "rho, nu, eps_r ASSUMED"),
    # --- validation-only materials ------------------------------------------------------------
    "polySi": Material("polysilicon", 160 * GPa, 0.22, 2330, 0.0, 0.0, "ASSUMED typical values (validation only)"),
}

# Few-layer graphene is treated as a tension-dominated membrane (see design_space.graphene_table)
GRAPHENE = dict(
    t_layer=0.335e-9,          # interlayer spacing [m]
    rho=2200.0,                # graphite density [kg/m^3] -> 7.4e-7 kg/m^2 per layer
    E2D=340.0,                 # 2D stiffness [N/m] per layer, Lee et al. Science 321, 385 (2008), doi:10.1126/science.1157996
    T_break=42.0,              # intrinsic strength [N/m] per layer (same source)
    src="Lee et al. 2008 (E~1.0 TPa, 340 N/m, 42 N/m). Built-in tension of suspended graphene is "
        "device-dependent (Bunch et al., Science 315, 490, 2007, doi:10.1126/science.1136836 report "
        "built-in tension but values were not verified here) - swept 0.01-1 N/m.",
)

# Fluids / constants
EPS0 = 8.8541878128e-12
P_ATM = 101325.0
WATER = dict(rho=1000.0, c=1500.0)
AIR = dict(rho=1.2, c=343.0)
OIL_SILICONE_RHO = 965.0   # ASSUMED (validation vs. Merbeler 2022)
OIL_MINERAL_RHO = 850.0    # ASSUMED (validation vs. Gerardo 2018)
GAMMA_IPA = 0.023          # surface tension of IPA [N/m], ASSUMED handbook value (stiction estimate)
E_BD_INSULATOR = 200e6     # ASSUMED breakdown field of sputtered SiNx/Al2O3 [V/m] = 2 MV/cm (conservative)

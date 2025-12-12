import CoolProp.CoolProp as CP
import numpy as np


def isotherm(fluid, T):
    T_crit = CP.PropsSI('Tcrit', fluid)
    T_k = T + 273.15
    P_range = np.logspace(np.log10(5e5), np.log10(200e5), 100)
    if T_k > T_crit:
        # Supercrítico
        h_iso = np.array([CP.PropsSI('H', 'T', T_k, 'P', p, fluid) for p in P_range])
        p_iso = P_range
    else:
        # Subcrítico (con parte plana)
        P_saturation = CP.PropsSI('P', 'T', T_k, 'Q', 0, fluid)
        P_liquid = np.logspace(np.log10(P_saturation * 1.01), np.log10(200e5), 30)
        P_vapor = np.logspace(np.log10(5e5), np.log10(P_saturation * 0.99), 30)
        
        h_liquid = [CP.PropsSI('H', 'T', T_k, 'P', p, fluid) for p in P_liquid]
        h_sat_liq = CP.PropsSI('H', 'T', T_k, 'Q', 0, fluid)
        h_sat_vap = CP.PropsSI('H', 'T', T_k, 'Q', 1, fluid)
        h_vapor_gas = [CP.PropsSI('H', 'T', T_k, 'P', p, fluid) for p in P_vapor]
        
        p_iso = np.concatenate([P_vapor, [P_saturation, P_saturation], P_liquid])
        h_iso = np.concatenate([h_vapor_gas, [h_sat_vap, h_sat_liq], h_liquid])
    
    return h_iso/1000, p_iso/1e5


def isoentropic(fluid, s):
    h_s = []
    p_s = []
    P_range = np.logspace(np.log10(5e5), np.log10(200e5), 100)
    for p in P_range:
        try:
            # Calculamos H dada la Presión (P) y Entropía (S)
            # Nota: s entra en J/kgK, por eso multiplicamos por 1000
            h = CP.PropsSI('H', 'P', p, 'S', s*1000, fluid)
            h_s.append(h)
            p_s.append(p)
        except:
            pass # Si el cálculo falla (fuera de rango), seguimos
    return np.array(h_s)/1000, np.array(p_s)/1e5


def isochoric(fluid, v):
    h_v = []
    p_v = []
    P_range = np.logspace(np.log10(5e5), np.log10(200e5), 100)
    # CoolProp usa Densidad (D) en kg/m3, no volumen específico.
    rho = 1 / v 
    for p in P_range:
        try:
            # Calculamos H dada la Presión (P) y Densidad (D)
            h = CP.PropsSI('H', 'P', p, 'D', rho, fluid)
            h_v.append(h)
            p_v.append(p)
        except:
            pass
    return np.array(h_v)/1000, np.array(p_v)/1e5

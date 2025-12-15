import CoolProp.CoolProp as CP
import matplotlib.pyplot as plt
import numpy as np
from ph import isochoric, isoentropic, isotherm

fluido = 'CO2'
T_Kelvin = 273.15
T_crit = CP.PropsSI('Tcrit', fluido)
P_crit = CP.PropsSI('Pcrit', fluido)
H_crit = CP.PropsSI('H', 'T', T_crit, 'P', P_crit, fluido)

# Configuración del gráfico
plt.figure(figsize=(14, 10))
plt.xlim(0, 650)      # Entalpía en kJ/kg
plt.ylim(5, 200)      # Presión en Bar


# --- 1. CAMPANA DE SATURACIÓN  ---
T_sat = np.linspace(CP.PropsSI('Tmin', fluido) + 1, T_crit - 0.1, 200)
h_liq, h_vap, p_sat = [], [], []

for T in T_sat:
    p_sat.append(CP.PropsSI('P', 'T', T, 'Q', 0, fluido))
    h_liq.append(CP.PropsSI('H', 'T', T, 'Q', 0, fluido))
    h_vap.append(CP.PropsSI('H', 'T', T, 'Q', 1, fluido))

# Dibujamos la campana gruesa
plt.plot(np.array(h_liq)/1000, np.array(p_sat)/1e5, 'k', linewidth=2)
plt.plot(np.array(h_vap)/1000, np.array(p_sat)/1e5, 'k', linewidth=2)

# 3. Graficar el punto crítico
plt.plot(H_crit/1000, P_crit/1e5, 'ko', markersize=6, zorder=10)

# 4. Añadir etiqueta
plt.text(H_crit/1000, (P_crit/1e5) + 5, 
         f'{T_crit-T_Kelvin:.1f}°C\n{P_crit/1e5:.1f} bar', 
         horizontalalignment='center',
         verticalalignment='bottom',
         fontsize=9,
         color='k',
         fontweight='bold')


# --- 2. ISOTERMAS (Corregidas con la meseta horizontal) ---
temperaturas = [-40, -20, 0, 20, 31.1, 60, 100]
for T_c in temperaturas:
    h_iso, p_iso = isotherm(fluido, T_c)
    plt.plot(h_iso, p_iso, 'b--', linewidth=0.5, alpha=0.6)
    plt.text(h_iso[-1], p_iso[-1]-10, f'{T_c}ºC', color='b', fontsize=7, ha='center', va='center')


# --- 3. LÍNEAS ISENTRÓPICAS (Entropía Constante) ---
# Definimos valores típicos de entropía para CO2 (kJ/kgK)
entropias = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4] 
for s in entropias:
    h_s, p_s = isoentropic(fluido, s)
    plt.plot(h_s, p_s, color='orange', linestyle='-', linewidth=0.8, alpha=0.8)
    if len(h_s) > 0:
        plt.text(h_s[-1], p_s[-1]-10, f's={s}', color='orange', fontsize=7, ha='center', va='center')


# --- 4. LÍNEAS DE VOLUMEN ESPECÍFICO CONSTANTE (Isocoras) ---
# Valores típicos para CO2 gas en m3/kg
volumenes = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1] 
for v in volumenes:
    h_v, p_v = isochoric(fluido, v)
    plt.plot(h_v, p_v, color='green', linestyle=':', linewidth=0.8, alpha=0.7)
    if len(h_v) > 0:
        plt.text(h_v[0], p_v[0]+.1, f'v={v}', color='green', fontsize=7, ha='center', va='center')


# --- 5. FORMATO FINAL ---
plt.yscale('log')
plt.xlabel('Entalpía (kJ/kg)')
plt.ylabel('Presión (Bar)')
plt.title('Diagrama Mollier Completo para CO2 (R-744)')
plt.grid(True, which="both", alpha=0.2)


# --- 6. DIBUJAR UN CICLO TRANSCRÍTICO DE EJEMPLO ---

# A. Definir Inputs del ciclo
T_evap = -10           # °C (Temperatura objetivo de frío)
superheat = 10         # K  (Seguridad para el compresor)
P_alta_bar = 95        # Bar (Presión de descarga, >73.8 bar para transcrítico)
T_gas_cooler_out = 35  # °C (Temperatura a la salida del enfriador)
efficiency = 0.75      # 75% (valor típico para compresor CO2)

# B. Cálculos de los 4 Puntos

# PUNTO 1: Aspiración (Salida Evaporador + Recalentamiento)
# Presión de baja dada por la T de evaporación
P_baja = CP.PropsSI('P', 'T', T_evap + T_Kelvin, 'Q', 1, fluido) 
T_aspiracion = T_evap + superheat + T_Kelvin
h1 = CP.PropsSI('H', 'T', T_aspiracion, 'P', P_baja, fluido)
s1 = CP.PropsSI('S', 'T', T_aspiracion, 'P', P_baja, fluido) # Necesitamos s1 para el compresor

# PUNTO 2: Descarga (Compresión Isentrópica)
P_alta = P_alta_bar * 1e5
# Asumimos s2 = s1 (Ideal). En la realidad s2 > s1 por eficiencia.
h2_ideal = CP.PropsSI('H', 'P', P_alta, 'S', s1, fluido)
h2 = h1 + (h2_ideal - h1) / efficiency
T_descarga = CP.PropsSI('T', 'P', P_alta, 'H', h2, fluido)

# PUNTO 3: Salida Gas Cooler
# Se enfría a P constante hasta T_gas_cooler_out
h3 = CP.PropsSI('H', 'P', P_alta, 'T', T_gas_cooler_out + T_Kelvin, fluido)

# PUNTO 4: Entrada Evaporador (Expansión)
# Expansión isoentálpica (h constante) hasta P_baja
h4 = h3 

# C. Graficar el Ciclo
# Organizamos los arrays para plotear: 1->2->3->4->1
cycle_h = [h1, h2, h3, h4, h1]
cycle_p = [P_baja, P_alta, P_alta, P_baja, P_baja]

# Convertir unidades
cycle_h = np.array(cycle_h) / 1000
cycle_p = np.array(cycle_p) / 1e5

# Dibujar líneas del ciclo
plt.plot(cycle_h, cycle_p, 'k-', linewidth=2, label='Ciclo Transcrítico', zorder=15)

# Dibujar los puntos (esquinas)
plt.plot(cycle_h[:-1], cycle_p[:-1], 'ko', zorder=20, markersize=5)

# D. Etiquetas de los Puntos (1, 2, 3, 4)
offset_y = 5 # Pequeño desplazamiento para el texto
plt.text(cycle_h[0], cycle_p[0] - offset_y, '1', fontsize=9, fontweight='bold', color='k')
plt.text(cycle_h[1], cycle_p[1] + offset_y, '2', fontsize=9, fontweight='bold', color='k')
plt.text(cycle_h[2], cycle_p[2] + offset_y, '3', fontsize=9, fontweight='bold', color='k')
plt.text(cycle_h[3], cycle_p[3] - offset_y, '4', fontsize=9, fontweight='bold', color='k')

# Añadir cuadro de texto con datos de rendimiento
info_text = (
    f'Temp. cooler: {T_gas_cooler_out:.1f}ºC\n'
    f'Temp. descarga: {T_descarga - T_Kelvin:.1f}°C\n'
    f'Eficiencia Is.: {efficiency:.0%}\n'
    f'COP: {(h1-h4)/(h2-h1):.2f}'
)
plt.text(540, 140, info_text, bbox=dict(facecolor='white', alpha=0.9), fontsize=9)


# --- 7. MOSTRAR EL GRÁFICO ---
plt.show()

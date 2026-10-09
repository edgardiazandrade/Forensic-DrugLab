# Forensic DrugLab Pro - Audit Report

### 1. Errores encontrados
- **Falta de Trazabilidad:** La base de datos anterior (pH_vs_Ionizacion_Comparada_Datos.csv) combinaba datos bibliográficos con cálculos e interpretaciones en una sola sábana, sin vincular referencias específicas a cada celda.
- **Modelado Ácido-Base Impreciso:** El cálculo de pKa promediaba automáticamente valores múltiples de sustancias anfóteras o dipróticas. 
- **Interpretación IR Automática:** Las bandas se generaban por heurísticas (ej. "C=O" para cualquier banda 1650-1850) sin respaldo empírico forense estricto por sustancia.
- **Extracción Idealizada:** La extracción L-L se dictaminaba como posible con sólo un 90% de diferencia de especiación, ignorando el parámetro termodinámico crítico de extracción real (Coeficiente de Distribución, $D$).

### 2. Datos Corregidos y Separados
Se ha disociado la arquitectura monolítica en módulos forenses estandarizados:
- `substances.csv`: Identificación matriz, comportamiento (ácido, base, anfótero) comprobado bibliográficamente.
- `ionization.csv`: Múltiples pKa desglosados (pKa1, pKa2, pKa3) sin promedios engañosos.
- `ftir.csv` / `gcms.csv`: Base de datos de confirmación analítica estricta por ion/pico.
- `presumptive_tests.csv`: Transición léxica de "Identificado" a "Resultado compatible con".

### 3. Ecuaciones Corregidas
- **Especiación Exacta (Henderson-Hasselbalch Multivariado):** La especiación ahora se calcula mediante el balance de masas riguroso $\\alpha_0, \\alpha_1, \\alpha_2$ en equilibrio competitivo.
- **Extracción Fraccional (D):** Se ha insertado la Ecuación de Distribución $D = P \cdot f_{neutra}$ y el cálculo de recuperación $E = \frac{D \cdot \frac{V_{org}}{V_{aq}}}{1 + D \cdot \frac{V_{org}}{V_{aq}}}$. 

### 4. Cambios de Terminología e Interfaz
- Los textos afirmativos ("Identificado como cocaína") fueron cambiados al estándar forense ISO 17025 ("Resultado presuntivo compatible con...").
- Integración de indicadores de confianza (🟢 Verificado, 🟡 Requiere Revisión, 🔴 No establecido).
- Advertencia Disclaimer de validez judicial introducida en todas las secciones.

### 5. Pruebas Realizadas
Se introdujo `tests.py` validando exitosamente el comportamiento de $HA/A^-$ a los límites del pH y el colapso a 0% de extracción con volúmenes nulos.

### 6. Limitaciones Restantes
El software asume un coeficiente de partición LogP genérico de 2.0 cuando la literatura no lo provee. La extracción real depende fuertemente de la saturación salina (salting-out) y efectos de matriz incalculables teóricamente.

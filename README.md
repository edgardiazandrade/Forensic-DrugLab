# Forensic-DrugLab: Análisis Químico de Sustancias

Herramienta pericial e interactiva para la interpretación, perfilación presuntiva y planificación de extracción químico-forense de sustancias psicoactivas y adulterantes.

---

## 🔬 Características Principales

1. **Ficha Comparativa:** 
   - Modelado dinámico de ionización según pH del medio.
   - Espectros infrarrojos FTIR-ATR con bandas diagnósticas ($cm^{-1}$).
   - Espectros de masas GC-MS con iones característicos ($m/z$).
   - Pruebas presuntivas colorimétricas de cribado.
2. **Árbol de Decisión Forense:**
   - Flujo analítico secuencial para muestras vegetales y polvos.
   - Diferenciación orientativa entre alcaloides, opiáceos, anfetaminas, entactógenos y cannabinoides.
3. **Preparación de Reactivos:**
   - Procedimientos de formulación estandarizados (Marquis, Mecke, Simon, Scott, Duquenois-Levine, etc.).
   - Catálogo cromático de virajes esperados y reporte de interferencias/falsos positivos.
4. **Fisicoquímica de Extracción Líquido-Líquido (L-L):**
   - Curvas de especiación ácidobase basadas en las ecuaciones exactas de Henderson-Hasselbalch y modelos dipróticos.
   - Detección algorítmica de ventanas de separación ($\Delta \ge 90\%$).
   - Protocolo automatizado paso a paso para lavado de adulterantes y recuperación de analitos.
5. **Simulador Manual L-L:**
   - Modelado libre de parámetros fisicoquímicos ($pKa$, carácter ácido/base/diprótico y solventes).
   - Validaciones analíticas para pares de equilibrios.

---

## 🚀 Despliegue e Instalación Local

### Requisitos Previos
* Python 3.9 o superior.

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Ejecución de la Aplicación
```bash
streamlit run app.py
```

---

## 📚 Referencias Bibliográficas

1. **Clarke's Analysis of Drugs and Poisons:** Moffat AC, Osselton MD, Widdop B, Watts J. 4a ed. Londres: Pharmaceutical Press; 2011.
2. **UNODC (ST/NAR/13/Rev.1):** *Métodos para el ensayo inmediato de drogas de uso indebido*. Manual para laboratorios nacionales de estupefacientes. Naciones Unidas; 2006.

---

**Autor:** QFB Edgar Oswaldo Díaz Andrade  
*Herramienta técnica de apoyo para laboratorio pericial y químico-farmacéutico.*

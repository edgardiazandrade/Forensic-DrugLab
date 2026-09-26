# Forensic DrugLab: Plataforma Pericial de Química Forense

Herramienta analítica e interactiva diseñada para peritos químicos y profesionales de las ciencias forenses. Facilita la toma de decisiones metodológicas en el análisis de sustancias controladas, modelando el comportamiento fisicoquímico de extracción líquido-líquido (L-L), la separación de sustancias de corte, el tamizaje presuntivo colorimétrico y la confirmación espectroscópica.

---

## Características Principales

* **Fisicoquímica y Extracción Líquido-Líquido (L-L):**
  - Modelado dinámico de curvas de ionización (% Ionizado vs. pH) basado en las ecuaciones de Henderson-Hasselbalch.
  - Simulación de partición entre fase acuosa y orgánica según el $pK_a$ y el carácter ácido-base de la molécula.
  - Algoritmo de separación selectiva entre **Sustancia Objetivo** y **Sustancia de Corte / Adulterante**, identificando la ventana óptima de $\Delta\text{pH}$ para aislamiento y purificación.
  - Visualización estructural dinámica (forma ionizada vs. base libre/neutra).

* **Tamizaje y Colorimetría Presuntiva:**
  - Árbol de decisión interactivo basado en baterías presuntivas estandarizadas (Mayer, Marquis, Mecke, Scott, Ehrlich, Duquenois-Levine).
  - Fichas técnicas con muestras cromáticas de viraje positivo (códigos HEX / Pantone) y esquemas de fases para ensayos bifásicos.
  - Advertencias sobre falsos positivos comunes y precauciones de seguridad reactiva.

* **Confirmación Instrumental:**
  - **Espectroscopía Infrarroja (FTIR):** Despliegue del espectro de referencia con asignación de bandas características ($cm^{-1}$) y modos de vibración molecular.
  - **Cromatografía de Gases con Espectrometría de Masas (GC-MS):** Espectro de masas con tabla de relaciones masa/carga ($m/z$), identificando ion base, ion molecular y fragmentos clave.

---

## Arquitectura Técnica

- **Framework:** Streamlit
- **Lenguaje:** Python 3 (motor nativo sin dependencias de compilación C pesadas, optimizado para compatibilidad con entornos restringidos y despliegue rápido).
- **Visualización:** Altair / Componentes CSS nativos.

---

## Instalación y Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/chemflow-forense.git](https://github.com/tu-usuario/chemflow-forense.git)
   cd chemflow-forense

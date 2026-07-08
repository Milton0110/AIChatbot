# Fuentes de la base de conocimiento — Nutrición y planes de comidas

Documentos públicos oficiales usados como corpus para la base vectorial (ChromaDB + Gemini Embeddings).
Combinan fuentes españolas/UE y anglosajonas/OMS para dar robustez, ya que ninguna fuente única
cubre a la vez calorías, macros, micronutrientes y fórmulas de cálculo personalizado.

| # | Archivo | Organismo | Año | Idioma | Aporta al agente |
|---|---------|-----------|-----|--------|-------------------|
| 1 | `01_AESAN_recomendaciones_dieteticas_saludables_sostenibles_2022.pdf` | AESAN (Agencia Española de Seguridad Alimentaria y Nutrición) | 2022 | ES | Recomendaciones prácticas por grupo de alimentos (frutas, verduras, legumbres, cereales, proteína, grasas) para población española. Base para construir menús concretos. |
| 2 | `02_SENC_FESNAD_guia_alimentacion_saludable.pdf` | SENC / FESNAD (Sociedad Española de Nutrición Comunitaria) | — | ES | Pirámide/rueda de alimentación saludable, frecuencias de consumo recomendadas por grupo de alimentos. |
| 3 | `03_EFSA_dietary_reference_values_summary_2017.pdf` | EFSA (European Food Safety Authority) | 2017 | EN | Valores de referencia (PRI/AR/AI) de macronutrientes, vitaminas y minerales para adultos — necesarios para validar que un menú cumple los micronutrientes. |
| 4 | `04_USDA_HHS_dietary_guidelines_americans_2020_2025.pdf` | USDA / HHS (EEUU) | 2020-2025 | EN | Tablas de necesidades calóricas estimadas por edad/sexo/nivel de actividad (Apéndice 2) y rangos de distribución de macronutrientes (AMDR). Muy útil para dimensionar el menú diario. |
| 5 | `05_WHO_healthy_diet_fact_sheet.pdf` | OMS (Organización Mundial de la Salud) | — | EN | Principios generales de dieta saludable: límites de azúcar, sal y grasas saturadas/trans. |
| 6 | `06_FAO_WHO_UNU_human_energy_requirements_2001.pdf` | FAO/WHO/UNU | 2001 | EN | Ecuaciones de Tasa Metabólica Basal (TMB) y multiplicadores de Nivel de Actividad Física (PAL) para calcular el Gasto Energético Total (GET) personalizado del usuario. |

## Nota sobre acceso

Todos los PDF son documentos públicos y de libre descarga. El PDF oficial de `dietaryguidelines.gov` no fue accesible directamente desde este entorno de desarrollo (posible restricción de red a dominios `.gov`), por lo que el documento 4 se obtuvo de un mirror público idéntico alojado por ASPHN (Association of State Public Health Nutritionists). Si al ejecutar el proyecto se prefiere la fuente original, puede sustituirse por `https://www.dietaryguidelines.gov/sites/default/files/2020-12/Dietary_Guidelines_for_Americans_2020-2025.pdf`.

## Cobertura respecto al MVP

El enunciado pide un mínimo de 3 documentos o ~20 páginas equivalentes. Estos 6 documentos suman varios cientos de páginas combinadas, cubriendo con holgura: grupos de alimentos y frecuencias (docs 1-2), valores de referencia de macro/micronutrientes (doc 3), calorías por perfil y AMDR (doc 4), principios generales (doc 5) y la fórmula de cálculo personalizado (doc 6).

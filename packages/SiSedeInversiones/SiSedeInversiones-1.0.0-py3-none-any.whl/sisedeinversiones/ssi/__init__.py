"""
La clase ScrapingMainSSI, esta diseñada para extrar la información que se encuentra en la 
página del Sistema de Seguimiento de Inversiones (SSI) del gobierno peruano.
Se usa el Código Único de Inversión (CUI) para filtrar la información que corresponde al
proyecto de inversion que se tiene identifciado con el CUI.


+------------------------+--------------------------+----------------------------------------------------------+-----------------------------+
| Sección                | Subsecciones             | Nombre en SSI                                            | Código exportado            |
+========================+==========================+==========================================================+=============================+
|                        |                          | Código único                                             | dg_cui                      |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Código SNIP                                              | dg_codio_snip               |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Fecha de registro                                        | dg_fecha_registro           |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Nombre de la inversión                                   | dg_nombre_inversion         |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Estado de la inversión                                   | dg_estado_inversion         |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Tipo de inversión                                        | dg_tipo_inversion           |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Programa PMI                                             | dg_programado_pmi           |
+                        +--------------------------+----------------------------------------------------------+-----------------------------+
|                        |                          | Oficina de Programación Multianual de Inversiones (OPMI) | dg_opmi                     |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        | I. Institucionalidad     | Unidad Formuladora (UF)                                  | dg_uf                       |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Unidad Ejecutora de Inversiones (UEI)                    | dg_uei                      |
+                        +--------------------------+----------------------------------------------------------+-----------------------------+
|  DATOS GENERALES       |                          | Situación de la inversión                                | dg_situcion                 |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Fecha de viabilidad/aprobación                           | dg_fecha_viabilidad         |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Decreto de emergencia                                    | dg_decreto_emergencia       |
+                        + II. Datos de la fase de  +----------------------------------------------------------+-----------------------------+
|                        | formulación y evaluación | Cadena funcional                                         | dg_cadena_funcional         |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Costo de inversión aprobado                              | dg_costo_inversion_aprobado |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Número de beneficiarios                                  | dg_numero_beneficiarios     |
+                        +--------------------------+----------------------------------------------------------+-----------------------------+
|                        |                          | ¿Tiene expediente técnico o documento equivalente        | dg_expediente_tecnico       |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | ¿Tiene registro de seguimiento?                          | dg_registro_seguimiento     |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Fecha de inicio de ejecución                             | dg_inicio_ejecucion         |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        | III. Datos de la fase de | Fecha de fin de ejecución                                | dg_fin_ejecucion            |
+                        + ejecución                +----------------------------------------------------------+-----------------------------+
|                        |                          | Costo de inversión actualizada (S/)                      | dg_inversion_actualizada    |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Costo de controversias (S/)                              | dg_costo_controversias      |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Monto de carta fianza (S/)                               | dg_monto_carta_fianza       |
+                        +                          +----------------------------------------------------------+-----------------------------+
|                        |                          | Costo total actualizado (S/)                             | dg_costo_total_actualizado  |
+------------------------+--------------------------+----------------------------------------------------------+-----------------------------+

"""

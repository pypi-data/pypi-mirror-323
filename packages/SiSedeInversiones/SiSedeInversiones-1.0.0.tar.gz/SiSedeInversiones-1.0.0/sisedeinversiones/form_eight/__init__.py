"""
Formulario N°8
==============

Este subpaquete esta diseñado para extraer información 
del "*Formato N°08-A Registros en la Fase de Ejecución*"
que se encuentra dentro del Sistema de Seguimiento de Inversiones.


.. image:: _static/form8.jpg

Información que se extrae del formulario N°8
--------------------------------------------

La información que se extrae de la página por medio de los CUI, 
es el siguiente:

Sección: Datos generales
^^^^^^^^^^^^^^^^^^^^^^^^

- Codigo Unico de Inversiones
- Nombre de la inversión

Sección: Datos de la fase de Formulación y Evaluación, modificados en la fase de Ejecución
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.- Responsabilidad funcional del proyecto de inversión
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Función
- División funcional
- Grupo funcional 
- Sector responsable
- Tipología del proyecto

2.- Articulación con el programa Multianual de inversiones (PMI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Servicio Público con Brecha identificada y priorizada
- Indicador de brechas de acceso a servicios
- Unidad de medida
- Espacio geográfico
- Contribución de cierre de brechas

3.- Institucionalidad
^^^^^^^^^^^^^^^^^^^^^

- OPMI
- UF
- UEI
- UEP

4.- Localización geográfica del proyecto de inversión
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- GPS
- Departamento
- Provincia
- Distrito
- Centro poblado




"""

__all__ = ["eight"]

# from . import eight

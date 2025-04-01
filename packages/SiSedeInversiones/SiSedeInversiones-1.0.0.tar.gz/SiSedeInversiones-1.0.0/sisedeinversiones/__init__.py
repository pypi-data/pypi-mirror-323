"""
Sistema de Seguimiento de Inversiones (SSI)
===========================================

Es una herramienta informática de acceso público que permite el seguimiento de
las inversiones públicas e integra información de las diferentes fases del ciclo de
inversión como Programación Multianual de Inversiones, Formulación y
del Estado como Sistema Nacional de Programacion Multianual y Gestión de
Evaluación, y Ejecución. Además, está vinculado con varios sistemas informáticos
Inversiones – Invierte.pe, SEACE, InfObras y SIAF. [#]_ 

.. [#] Extraido de (S/f). Gob.pe. Recuperado el 19 de enero de 2025, de https://www.mef.gob.pe/contenidos/inv_publica/docs/Instructivo_BI/2024/Seguimiento_2_Manual_SSI.pdf.

1. Objetivos del SSI
--------------------

+--------+---------------------------------------------------------------------------------------------------------------------------------------------+
| N°     | Objetivos                                                                                                                                   | 
+========+=============================================================================================================================================+
| 01     | Mostrar información sistematizada de las inversiones públicas, para un adecuado seguimiento                                                 |
+--------+---------------------------------------------------------------------------------------------------------------------------------------------+
| 02     | Optimizar el tiempo de búsqueda a través de los vinculos de acceso con los formatos de las diferentes fases del Ciclo de Inversión          |
+--------+---------------------------------------------------------------------------------------------------------------------------------------------+
| 03     | Brindar información actualizada de las inversiones con la finalidad de facilitar la elaboración de reportes de seguimiento.                 |
+--------+---------------------------------------------------------------------------------------------------------------------------------------------+
| 04     | Conocer los actores que intervienen en la gestión de la Inversión Pública (UEI, UF y OPMI)                                                  |
+--------+---------------------------------------------------------------------------------------------------------------------------------------------+


2. Entorno del SSI
------------------

.. image:: _static/ssi.png

3. Secciones del SSI
--------------------

3.1 Sección: Datos generales
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/datosGenerales.png


3.1 Sección: Ejecución financiera
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/ejecucionFinanciera.png

3.1 Sección: Contrataciones
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/Contrataciones.png

3.1 Sección: InfObras
^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/InfObras.png

Paquete SiSedeInversiones 
=========================

1. Instalación
--------------

Para usar SiSedeInversiones, primero debes instalarlo usando pip:

.. code-block:: console

    (.venv) $ pip install SiSedeInversiones

"""

__all__ = ["main", "form_eight", "lista_ejecucion"]

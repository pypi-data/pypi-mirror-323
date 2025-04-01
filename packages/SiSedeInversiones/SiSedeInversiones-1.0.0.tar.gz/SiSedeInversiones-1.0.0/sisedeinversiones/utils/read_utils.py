"""
*Class ReadsFiles*
==================
Este método es usado de manera transversal, puesto que se encarga de leer los archivos .csv o .xlsx
que extrae la información de los CUI's almacenados en ellos. Esto es necesario porque se requiere
dichos CUI's para realizar las consultas a las secciones del portal SSI.
"""

import pandas as pd


class ReadsFiles:
    def __init__(self, file_read, num_range):
        """La clase se inicializa con los atributos file_read y num_range

        Args:
            file_read (str): Es la dirección del archvio a leer que puede ser .csv o .xlsx
            num_range (str): Aqui indicamos el rango de registros que se tiene que trabajar, bajo el formato "[num_inicio]_[num_fin]", se debe mantener la forma de separar con un guión bajo.
        """
        self.file_read = file_read
        self.num_range = num_range

    def read_file_csv(self):
        """Este método se encarga de leer los archivos .csv para extraer los CUI's, asimismo filtra la cantidad de registros que se trabajará.

        Returns:
            list: Genera una lista con los CUI's que se trabajarán
        """
        start_range, end_range = self.num_range.split("_")
        cui0 = pd.read_csv(self.file_read, encoding="latin-1")
        cui1 = cui0["cui"][int(start_range): int(end_range)]
        list_cui = list(map(str, cui1.values.tolist()))
        print(f"El total de CUIs a scrapear es: {len(list_cui)}")
        return list_cui

    def read_file_xlsx(self):
        """Este método se encarga de leer los archivos .xlsx para extraer los CUI's, asimismo filtra la cantidad de registros que se trabajará.

        Returns:
            list: Genera una lista con los CUI's que se trabajarán
        """
        start_range, end_range = self.num_range.split("_")
        cui0 = pd.read_excel(self.file_read, encoding="latin-1")
        cui1 = cui0["cui"][int(start_range): int(end_range)]
        list_cui = list(map(str, cui1.values.tolist()))
        print(f"El total de CUIs a scrapear es: {len(list_cui)}")
        return list_cui

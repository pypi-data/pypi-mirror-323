"""
Clases SSI
==========

En esta sección, se construye una clase general que hereda los métodos de las clases específicas
para cada sección del portal (Formato8, lista de ejecución y el SSI).

"""

from .form_eight.eight import ScrapingEight
from .lista_ejecucion.lista_ejecucion_simple import ScrapingListaEjecucion
from .ssi.main_ssi import ScrapingMainSSI


class SSI(ScrapingEight, ScrapingListaEjecucion, ScrapingMainSSI):
    """Con esta clase unimos los métodos principales de las clases específicas para cada
        seccion del SSI.

    Args:
        ScrapingEight (string): tiene los atributos file_read, num_range, path_export, file_type, year.
        ScrapingListaEjecucion (string): tiene los atributos file_read, num_range, path_export, file_type, year.
        ScrapingMainSSI (string): tiene los atributos file_read, num_range, path_export, file_type, year.
    """

    def __init__(self, file_read, num_range, path_export, file_type, year):
        ScrapingEight.__init__(self, file_read, num_range, path_export, file_type, year)
        ScrapingListaEjecucion.__init__(
            self, file_read, num_range, path_export, file_type, year
        )
        ScrapingMainSSI.__init__(
            self, file_read, num_range, path_export, file_type, year
        )

    def format_eight(self):
        """Método que descarga los datos de la sección Formato 8 del SSI.

        Returns:
            xlsx: Un archivo xlsx con lso datos almancenados del formato 8
        """
        return ScrapingEight(
            self.file_read, self.num_range, self.path_export, self.file_type, self.year
        ).download_data()

    def list_ejecucion(self):
        """Método que descarga los datos de la sección Lista de Ejecución del SSI.

        Returns:
            xlsx: Genera un archivo xlsx con los datos almacenados de la lista
        """
        return ScrapingListaEjecucion(
            self.file_read, self.num_range, self.path_export, self.file_type, self.year
        ).download_data()

    def main_ssi(self):
        """Método que descarga los datos de la sección principal del SSI.

        Returns:
            xlsx: Genera un archivc xlsx con los datos almacenados de la sección principal
        """
        return ScrapingMainSSI(
            self.file_read, self.num_range, self.path_export, self.file_type, self.year
        ).download_data()

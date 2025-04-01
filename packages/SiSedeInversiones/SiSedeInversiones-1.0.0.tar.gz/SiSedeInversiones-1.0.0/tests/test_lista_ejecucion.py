from sisedeinversiones.lista_ejecucion.lista_ejecucion_simple import \
    ScrapingListaEjecucion

file_read = "E:/otrosTrabajosSTATA-practicas/proyectStataPythonToGitHub/scrapingFunctions/SiSedeInversiones/CUI_2019_dep7.csv"
path_export = "E:/otrosTrabajosSTATA-practicas/proyectStataPythonToGitHub/pruebas"
num_range = "5_10"
file_type = ".xlsx"
year = "2019"

scraping_lista_ejecucion = ScrapingListaEjecucion(
    file_read, num_range, path_export, file_type, year
)

"""
Test the ScrapingListaEjecucion class of method read_file.
"""


def test_scraping_lista_ejecucion_read_file_csv():
    result = scraping_lista_ejecucion.read_file()
    assert result is not None


def test_scraping_lista_ejecucion_read_file_type_file_csv():

    result = scraping_lista_ejecucion.read_file()
    assert type(result) is list


def test_scraping_lista_ejecucion_results_registers_not_empty():
    results = scraping_lista_ejecucion.read_file()
    for result in results:
        assert result[0] != ""

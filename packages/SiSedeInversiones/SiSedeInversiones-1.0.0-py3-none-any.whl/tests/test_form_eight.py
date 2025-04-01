from sisedeinversiones.form_eight.eight import ScrapingEight

file_read = "E:/otrosTrabajosSTATA-practicas/proyectStataPythonToGitHub/scrapingFunctions/SiSedeInversiones/CUI_2019_dep7.csv"
path_export = "E:/otrosTrabajosSTATA-practicas/proyectStataPythonToGitHub/pruebas"
num_range = "5_10"
file_type = ".xlsx"
year = "2019"

scraping_eight = ScrapingEight(file_read, num_range, path_export, file_type, year)


def test_scraping_eight_read_file_csv():
    """
    Test the ScrapingEight class of method read_file.
    """
    result = scraping_eight.read_file()
    assert result is not None


def test_scraping_eight_read_file_type_file_csv():

    result = scraping_eight.read_file()
    assert type(result) is list


def test_scraping_eight_results_registers_not_empty():
    results = scraping_eight.read_file()
    for result in results:
        assert result[0] != ""


# def test_scraping_eight_results_download_data():
#     results = scraping_eight.download_data()
#     assert Path(results).suffix == '.xlsx'
# assert results is not None

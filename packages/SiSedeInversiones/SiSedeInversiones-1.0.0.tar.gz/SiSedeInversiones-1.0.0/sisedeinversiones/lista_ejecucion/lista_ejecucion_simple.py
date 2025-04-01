"""
*Class ScrapingListaEjecucion*
==============================
"""

import time

import pandas as pd
import rpa as r

from ..utils.read_utils import ReadsFiles


class ScrapingListaEjecucion(ReadsFiles):
    """_summary_

    Args:
        file_read (str): Este atributo indica la dirección del archivo a leer. Para este caso un csv.
        num_range (str): Indicamos el rango de registros que se trabajara, el formato para indicar dicho rango es [num_inicio]_[num_final], es importante separarlos por un guin bajo. Sino se tendra problemas.
        path_export (str): Aqui indicamos la dirección de la carpeta donde se quiere exportar el archivo generado.
        file_type (str): Aqui indicamos el tipo de archivo que se quiere descargar. De momento solo se tiene habilitado el formato .xlsx para exportar la información.
        year (str): Indicamos el año de los registros que se estan trabajando.
    """

    def __init__(self, file_read, num_range, path_export, file_type, year):
        ReadsFiles.__init__(self, file_read=file_read, num_range=num_range)
        self.path_export: str = path_export
        self.file_type: str = file_type
        self.year: str = year

    def read_file(self):
        """Aqui se lee los archivos CUI's y se filtra la cantidad de registros a trabajar

        Returns:
            list: Lista de los CUI's que se trabajaran
        """
        return ReadsFiles(self.file_read, self.num_range).read_file_csv()

    def scrape_info(self):
        """Este método se encarga de automatizar el proceso de extracción de los datos

        Returns:
            Tupla: Genera una tupla con la información que se reunio durante el proceso.
        """

        lista_cui = self.read_file()

        # ---------------------------------------------------------------------
        # ---- Creamos los objetos de listas para almacenar la información ----
        # ---------------------------------------------------------------------

        # Datos generales
        ssi_cui = []
        ssi_pip = []
        ssi_monto_inversion = []
        ssi_monto_actualizado = []
        # Lista de modificaciones en Fase de Ejecución
        ssi_fecha_ultimamodificacion = []
        ssi_comentarios = []
        ssi_usuario = []
        ssi_tipo_documento = []
        ssi_historico = []

        # --------------------------------
        # ---- Comenzamos el scraping ----
        # --------------------------------

        r.init()
        # r.init(turbo_mode=True)

        for one_cui in range(len(lista_cui)):
            r.url(
                f"https://ofi5.mef.gob.pe/invierte/ejecucion/traeListaEjecucionSimplePublica/{lista_cui[one_cui]}"
            )
            time.sleep(3)

            element_exist = r.present(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[1]/div[2]/div[1]'
            )
            if not element_exist:
                time.sleep(2)

            print(
                f"Se esta trabajando el regtistro {one_cui} con el CUI {lista_cui[one_cui]} y el elemento existe {element_exist}"
            )
            # Datos generales del proyecto o inversión
            cui = r.read(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[1]/div[2]/div[2]'
            )
            pip = r.read(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[1]/div[3]/div[2]'
            )
            monto_inversion = r.read(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[1]/div[4]/div[2]'
            )
            monto_actualizado = r.read(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[1]/div[5]/div[2]'
            )
            # Lista de modificaciones en Fase de Ejecución

            if r.present(
                '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody'
            ):
                time.sleep(1)
                fecha_ultimamodificacion = r.read(
                    '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td[1]'
                )
                comentarios = r.read(
                    '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td[3]'
                )
                usuario = r.read(
                    '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td[4]'
                )
                tipo_documento = r.read(
                    '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td[5]'
                )
                historico = r.read(
                    '//*[@id="main-container"]/div[1]/div/div/div/div/div[2]/table/tbody/tr/td[6]'
                )

            else:
                fecha_ultimamodificacion = "0"
                comentarios = "0"
                usuario = "0"
                tipo_documento = "0"
                historico = "0"

            ssi_cui.append(cui)
            ssi_pip.append(pip)
            ssi_monto_inversion.append(monto_inversion)
            ssi_monto_actualizado.append(monto_actualizado)
            ssi_fecha_ultimamodificacion.append(fecha_ultimamodificacion)
            ssi_comentarios.append(comentarios)
            ssi_usuario.append(usuario)
            ssi_tipo_documento.append(tipo_documento)
            ssi_historico.append(historico)

        time.sleep(1)
        r.close()
        time.sleep(2)

        return (
            ssi_cui,
            ssi_pip,
            ssi_monto_inversion,
            ssi_monto_actualizado,
            ssi_fecha_ultimamodificacion,
            ssi_comentarios,
            ssi_usuario,
            ssi_tipo_documento,
            ssi_historico,
        )

    def download_data(self):
        """Aqui exportamos la información reunida con el metodo scrape_info()

        Returns:
            xlsx: Se recibe la tupla que luego se exporta en formato .xslx
        """
        (
            ssi_cui,
            ssi_pip,
            ssi_monto_inversion,
            ssi_monto_actualizado,
            ssi_fecha_ultimamodificacion,
            ssi_comentarios,
            ssi_usuario,
            ssi_tipo_documento,
            ssi_historico,
        ) = self.scrape_info()
        print(
            f"El total de CUIs scrapeados es: {len(ssi_cui)} y se esta exportando a Excel"
        )
        ssi_lista_ejecucion = pd.DataFrame(
            {
                "cui": ssi_cui,
                "nombre_pip": ssi_pip,
                "monto_inversion": ssi_monto_inversion,
                "monto_actualizado": ssi_monto_actualizado,
                "fecha_ultima_modificacion": ssi_fecha_ultimamodificacion,
                "comentarios": ssi_comentarios,
                "usuario": ssi_usuario,
                "tipo_documento": ssi_tipo_documento,
                "historico": ssi_historico,
            }
        )

        return ssi_lista_ejecucion.to_excel(
            f"{self.path_export}/ssi_ListaEjecucionSimplePublica_{self.year}_regts_{self.num_range}{self.file_type}",
            index=False,
            header=True,
        )

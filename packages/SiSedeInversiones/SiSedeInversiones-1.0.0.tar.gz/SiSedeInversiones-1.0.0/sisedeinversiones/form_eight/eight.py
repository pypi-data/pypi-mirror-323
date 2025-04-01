"""
*Class ScrapingEight*
=====================

"""

import time

import pandas as pd
import rpa as r

from ..utils.read_utils import ReadsFiles


class ScrapingEight(ReadsFiles):
    """Scraping Class Attributes

    Args:
        file_read (_type_): It is the address where the file with the CUI codes that we are going to consume is located.
        path_export (_type_): Address where the information generated after data extraction will be exported.
        num_range (_type_): Indicates the range of records that will be worked on, separated by a "_" between the upper and lower limits.
        file_type (_type_): This is the type of file you want to export. At the moment it is programmed to generate .xlsx files.
        year (_type_): Indicate the year of the records, this information will be used to generate the name of the .xlsx file that will be exported with the collected information.
    """

    def __init__(self, file_read, num_range, path_export, file_type, year):
        ReadsFiles.__init__(self, file_read=file_read, num_range=num_range)
        self.path_export: str = path_export
        self.file_type: str = file_type
        self.year: str = year

    def read_file(self):
        """We import the .csv file with the CUI's

        Returns:
            _type_: _description_
        """
        return ReadsFiles(self.file_read, self.num_range).read_file_csv()

    def scrape_info(self):
        """_summary_

        Returns:
            _type_: _description_
        """

        lista_cui = self.read_file()

        # ---------------------------------------------------------------------
        # ---- Creamos los objetos de listas para almacenar la información ----
        # ---------------------------------------------------------------------

        # Responsabilidad funcional del proyecto de inversion
        ssi_cui = []
        ssi_pip = []
        ssi_funcion = []
        ssi_divfuncional = []
        ssi_grupfuncional = []
        ssi_sectorresponsable = []
        ssi_tipologiaproyecto = []
        # Articulacion con el programa multianual de inversiones (PMI)
        ssi_brecha = []
        ssi_brecha_indicador = []
        ssi_brecha_um = []
        ssi_brecha_espaciogeografico = []
        ssi_brecha_contribucioncierre = []
        # Institucionalidad
        ssi_opmi = []
        ssi_uf = []
        ssi_uei = []
        ssi_uep = []
        # Localizacion de la inversion publica
        ssi_gps = []
        ssi_departamento = []
        ssi_provincia = []
        ssi_distrito = []
        ssi_centro_poblado = []

        # --------------------------------
        # ---- Comenzamos el scraping ----
        # --------------------------------

        r.init()
        # r.init(turbo_mode=True)

        for one_cui in range(len(lista_cui)):
            r.url(
                f"https://ofi5.mef.gob.pe/invierte/ejecucion/verFichaEjecucion/{lista_cui[one_cui]}"
            )
            time.sleep(3)

            element_exist = r.present(
                '//*[@id="divVistaPreliminar"]/table[1]/tbody/tr[1]/td[1]'
            )
            if not element_exist:
                time.sleep(2)

            print(
                f"Se esta trabajando el regtistro {one_cui} con el CUI {lista_cui[one_cui]} y el elemento existe {element_exist}"
            )
            # Identificar y almacenar la información de la página
            cui = r.read('//*[@id="divVistaPreliminar"]/table[1]/tbody/tr[1]/td[2]/div')
            pip = r.read('//*[@id="divVistaPreliminar"]/table[1]/tbody/tr[2]/td[2]/div')
            funcion = r.read('//*[@id="divVistaPreliminar"]/table[2]/tbody/tr[1]/td[3]')
            divfuncional = r.read(
                '//*[@id="divVistaPreliminar"]/table[2]/tbody/tr[2]/td[3]'
            )
            grupfuncional = r.read(
                '//*[@id="divVistaPreliminar"]/table[2]/tbody/tr[3]/td[3]'
            )
            sectorresponsable = r.read(
                '//*[@id="divVistaPreliminar"]/table[2]/tbody/tr[4]/td[3]'
            )
            tipologiaproyecto = r.read(
                '//*[@id="divVistaPreliminar"]/table[2]/tbody/tr[5]/td[3]'
            )

            brecha = r.read('//*[@id="divVistaPreliminar"]/table[3]/tbody/tr/td[1]')
            brecha_indicador = r.read(
                '//*[@id="divVistaPreliminar"]/table[3]/tbody/tr/td[2]'
            )
            brecha_um = r.read('//*[@id="divVistaPreliminar"]/table[3]/tbody/tr/td[3]')
            brecha_espaciogeografico = r.read(
                '//*[@id="divVistaPreliminar"]/table[3]/tbody/tr/td[4]'
            )
            brecha_contribucioncierre = r.read(
                '//*[@id="divVistaPreliminar"]/table[3]/tbody/tr/td[5]'
            )

            opmi = r.read('//*[@id="divVistaPreliminar"]/table[4]/tbody/tr[1]/td[3]')
            uf = r.read('//*[@id="divVistaPreliminar"]/table[4]/tbody/tr[2]/td[3]')
            uei = r.read('//*[@id="divVistaPreliminar"]/table[4]/tbody/tr[3]/td[3]')
            uep = r.read('//*[@id="divVistaPreliminar"]/table[4]/tbody/tr[4]/td[3]')

            if r.present('//*[@id="divVistaPreliminar"]/table[5]/tbody/tr'):
                time.sleep(1)
                gps = r.read('//*[@id="divVistaPreliminar"]/table[5]/tbody/tr/td[1]')
                departamento = r.read(
                    '//*[@id="divVistaPreliminar"]/table[5]/tbody/tr/td[2]'
                )
                provincia = r.read(
                    '//*[@id="divVistaPreliminar"]/table[5]/tbody/tr/td[3]'
                )
                distrito = r.read(
                    '//*[@id="divVistaPreliminar"]/table[5]/tbody/tr/td[4]'
                )
                centro_poblado = r.read(
                    '//*[@id="divVistaPreliminar"]/table[5]/tbody/tr/td[5]'
                )
            else:
                gps = "0"
                departamento = "0"
                provincia = "0"
                distrito = "0"
                centro_poblado = "0"

            ssi_cui.append(cui)
            ssi_pip.append(pip)
            ssi_funcion.append(funcion)
            ssi_divfuncional.append(divfuncional)
            ssi_grupfuncional.append(grupfuncional)
            ssi_sectorresponsable.append(sectorresponsable)
            ssi_tipologiaproyecto.append(tipologiaproyecto)

            ssi_brecha.append(brecha)
            ssi_brecha_indicador.append(brecha_indicador)
            ssi_brecha_um.append(brecha_um)
            ssi_brecha_espaciogeografico.append(brecha_espaciogeografico)
            ssi_brecha_contribucioncierre.append(brecha_contribucioncierre)

            ssi_opmi.append(opmi)
            ssi_uf.append(uf)
            ssi_uei.append(uei)
            ssi_uep.append(uep)

            ssi_gps.append(gps)
            ssi_departamento.append(departamento)
            ssi_provincia.append(provincia)
            ssi_distrito.append(distrito)
            ssi_centro_poblado.append(centro_poblado)
        time.sleep(1)
        r.close()
        time.sleep(2)

        return (
            ssi_cui,
            ssi_pip,
            ssi_funcion,
            ssi_divfuncional,
            ssi_grupfuncional,
            ssi_sectorresponsable,
            ssi_tipologiaproyecto,
            ssi_brecha,
            ssi_brecha_indicador,
            ssi_brecha_um,
            ssi_brecha_espaciogeografico,
            ssi_brecha_contribucioncierre,
            ssi_opmi,
            ssi_uf,
            ssi_uei,
            ssi_uep,
            ssi_gps,
            ssi_departamento,
            ssi_provincia,
            ssi_distrito,
            ssi_centro_poblado,
        )

    def download_data(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        (
            ssi_cui,
            ssi_pip,
            ssi_funcion,
            ssi_divfuncional,
            ssi_grupfuncional,
            ssi_sectorresponsable,
            ssi_tipologiaproyecto,
            ssi_brecha,
            ssi_brecha_indicador,
            ssi_brecha_um,
            ssi_brecha_espaciogeografico,
            ssi_brecha_contribucioncierre,
            ssi_opmi,
            ssi_uf,
            ssi_uei,
            ssi_uep,
            ssi_gps,
            ssi_departamento,
            ssi_provincia,
            ssi_distrito,
            ssi_centro_poblado,
        ) = self.scrape_info()
        print(
            f"El total de CUIs scrapeados es: {len(ssi_cui)} y se esta exportando a Excel"
        )
        ssi_formato8 = pd.DataFrame(
            {
                "cui": ssi_cui,
                "nombre_pip": ssi_pip,
                "funcion": ssi_funcion,
                "division_funcional": ssi_divfuncional,
                "grupo_funcional": ssi_grupfuncional,
                "sector_responsable": ssi_sectorresponsable,
                "tipologia_proyecto": ssi_tipologiaproyecto,
                "brecha_identificada": ssi_brecha,
                "brecha_indicador": ssi_brecha_indicador,
                "brecha_unidad": ssi_brecha_um,
                "brecha_geografico": ssi_brecha_espaciogeografico,
                "cierra_brecha": ssi_brecha_contribucioncierre,
                "opmi": ssi_opmi,
                "uf": ssi_uf,
                "uei": ssi_uei,
                "uep": ssi_uep,
                "gps": ssi_gps,
                "departamento": ssi_departamento,
                "provincia": ssi_provincia,
                "distrito": ssi_distrito,
                "centro_poblado": ssi_centro_poblado,
            }
        )

        return ssi_formato8.to_excel(
            f"{self.path_export}/ssi_formato8_{self.year}_regts_{self.num_range}{self.file_type}",
            index=False,
            header=True,
        )

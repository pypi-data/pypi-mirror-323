"""
*Clase ScrapingMainSSI*
=======================

Esta clase se encarga de extraer información de las secciones:

- Datos generales
- Ejecución financiera
- Contrataciones

"""

import time

import pandas as pd
import rpa as r

from ..utils.read_utils import ReadsFiles


class ScrapingMainSSI(ReadsFiles):
    """_summary_

    Args:
        file_read (str): Este atributo indica la dirección del archivo a leer. Para este caso un csv.
        num_range (str): Indicamos el rango de registros que se trabajara, el formato para indicar dicho rango es [num_inicio]_[num_final], es importante separarlos por un guin bajo. Sino se tendra problemas.
        path_export (str): Aqui indicamos la dirección de la carpeta donde se quiere exportar el archivo generado.
        file_type (str): Aqui indicamos el tipo de archivo que se quiere descargar. De momento solo se tiene habilitado el formato .xlsx para exportar la información.
        year (str): Indicamos el año de los registros que se estan trabajando.
    """

    def __init__(self, file_read, num_range, path_export, file_type, year):
        ReadsFiles.__init__(self, file_read, num_range)
        self.path_export = path_export
        self.file_type = file_type
        self.year = year

    def read_file(self):
        return ReadsFiles(self.file_read, self.num_range).read_file_csv()

    def scrape_info(self):
        lista_cui = self.read_file()

        # -----------------------------------------------------------------------------------------
        # ----------------------CREAMOS LAS LISTAS PARA ALMACENAR LA INFORMACIÓN-------------------
        # -----------------------------------------------------------------------------------------

        # --------------------DATOS GENERALES----------------------
        # 0.- información general
        ssi_cui = []
        ssi_snip = []
        ssi_fecha_registro = []
        ssi_nombre_inversion = []
        ssi_estado = []
        ssi_tipo_inversion = []
        ssi_programa_pmi = []
        # 1.- institucionalidad
        ssi_opmi = []
        ssi_uf = []
        ssi_uei = []
        # 2.- datos de la fase ejecucion
        ssi_situacion = []
        ssi_decreto_emergencia = []
        ssi_cadena_funcional = []
        ssi_viabilidad_aprobacion = []
        ssi_costo_aprobado = []
        ssi_beneficiarios = []
        ssi_inicio_ejecucion = []
        ssi_fin_ejecucion = []
        # 3.- datos de la fase ejecucion
        ssi_expediente_tecnico = []
        ssi_reg_seguimiento = []
        ssi_registro_cierre = []
        # ssi_inicio_ejecucion = []
        ssi_inversion_actualizado = []
        ssi_sol_controversias = []
        ssi_carta_fianza = []
        ssi_inv_total = []

        # --------------------EJECUCION FINANCIERA----------------------
        ssi_cost_inversion = []
        ssi_devengado_acumulado = []
        ssi_avance_financiero_acum = []
        ssi_saldo = []
        ssi_fecha_primerdevengado = []
        ssi_fecha_ultimodevengado = []

        # --------------------CONTRATACIONES----------------------
        ssi_seaceobra = []
        ssi_seaceconsul = []
        ssi_seacebien = []
        ssi_seaceserv = []

        # ssi_contrato         = []
        # ssi_contratista      = []
        # ssi_n_contrato       = []
        # ssi_fechasuscripcion = []
        # ssi_monto_contrato   = []
        # ssi_monto_item       = []

        r.init()

        for one_cui in range(len(lista_cui)):
            r.url("https://ofi5.mef.gob.pe/ssi/ssi/Index")
            time.sleep(2)
            r.type('//*[@id="txt_cu"]', lista_cui[one_cui])
            r.click(
                '//*[@id="divContainer"]/div[1]/div[1]/div/table/tbody/tr[3]/td[1]/ul/li[1]/div/span'
            )
            time.sleep(3)

            if not r.present(
                '//*[@id="divVistaPreliminar"]/table[1]/tbody/tr[1]/td[1]'
            ):
                time.sleep(2)

            print(
                f"Se esta trabajando el registro {one_cui} con el CUI {lista_cui[one_cui]}"
            )

            # --------------------DATOS GENERALES----------------------
            cui = r.read('//*[@id="td_cu"]')
            snip = r.read('//*[@id="td_snip"]')
            fecha_registro = r.read('//*[@id="td_fecreg"]')
            nombre_inversion = r.read('//*[@id="td_nominv"]')
            estado = r.read('//*[@id="td_estcu"]')
            tipo_inversion = r.read('//*[@id="td_tipinv"]')
            programa_pmi = r.read('//*[@id="td_indpmi"]')
            # 1.- institucionalidad
            opmi = r.read('//*[@id="td_opmi"]')
            uf = r.read('//*[@id="td_uf"]')
            uei = r.read('//*[@id="td_uei"]')
            # 2.- datos de la fase ejecucion
            situacion = r.read('//*[@id="td_situinv"]')
            decreto_emergencia = r.read('//*[@id="td_emergds"]')
            cadena_funcional = r.read('//*[@id="td_cadfun"]')
            viabilidad_aprobacion = r.read('//*[@id="td_fecviab"]')
            costo_aprobado = r.read('//*[@id="td_mtoviab"]')
            beneficiarios = r.read('//*[@id="td_benif"]')
            # 3.- datos de la fase ejecucion
            expediente_tecnico = r.read('//*[@id="td_indet"]')
            reg_seguimiento = r.read('//*[@id="td_indseg"]')
            registro_cierre = r.read('//*[@id="td_f9"]')
            inicio_ejecucion = r.read('//*[@id="fec_iniejec"]')
            fin_ejecucion = r.read('//*[@id="fec_finejec"]')
            inversion_actualizado = r.read('//*[@id="val_cta"]')
            sol_controversias = r.read('//*[@id="td_laudo"]')
            carta_fianza = r.read('//*[@id="td_carfza"]')
            inv_total = r.read('//*[@id="td_mtototal"]')

            # 1.1.-ALMACENAMOS la información en las listas
            ssi_cui.append(cui)
            ssi_snip.append(snip)
            ssi_fecha_registro.append(fecha_registro)
            ssi_nombre_inversion.append(nombre_inversion)
            ssi_estado.append(estado)
            ssi_tipo_inversion.append(tipo_inversion)
            ssi_programa_pmi.append(programa_pmi)
            ssi_opmi.append(opmi)
            ssi_uf.append(uf)
            ssi_uei.append(uei)
            ssi_situacion.append(situacion)
            ssi_decreto_emergencia.append(decreto_emergencia)
            ssi_cadena_funcional.append(cadena_funcional)
            ssi_viabilidad_aprobacion.append(viabilidad_aprobacion)
            ssi_costo_aprobado.append(costo_aprobado)
            ssi_beneficiarios.append(beneficiarios)
            ssi_expediente_tecnico.append(expediente_tecnico)
            ssi_reg_seguimiento.append(reg_seguimiento)
            ssi_registro_cierre.append(registro_cierre)
            ssi_inicio_ejecucion.append(inicio_ejecucion)
            ssi_fin_ejecucion.append(fin_ejecucion)
            ssi_inversion_actualizado.append(inversion_actualizado)
            ssi_sol_controversias.append(sol_controversias)
            ssi_carta_fianza.append(carta_fianza)
            ssi_inv_total.append(inv_total)

            # --------------------EJECUCION FINANCIERA----------------------
            # pasamos a la seccion ejecucion financiera
            r.click('//*[@id="img_financ"]')
            # scrapeamos la información
            cost_inversion = r.read('//*[@id="td_mtototal2"]')
            devengado_acumulado = r.read('//*[@id="val_efin"]')
            avance_financiero_acum = r.read('//*[@id="por_avanacum"]')
            saldo = r.read('//*[@id="sdo_ejecacum"]')
            fecha_primerdevengado = r.read('//*[@id="pridev"]')
            fecha_ultimodevengado = r.read('//*[@id="ultdev"]')
            # agregamos a las listas de información
            ssi_cost_inversion.append(cost_inversion)
            ssi_devengado_acumulado.append(devengado_acumulado)
            ssi_avance_financiero_acum.append(avance_financiero_acum)
            ssi_saldo.append(saldo)
            ssi_fecha_primerdevengado.append(fecha_primerdevengado)
            ssi_fecha_ultimodevengado.append(fecha_ultimodevengado)

            time.sleep(1)

            # --------------------CONTRATACIONES----------------------
            # pasamos a la seccion de contrataciones
            r.click('//*[@id="btn_seace"]')
            # scraping de la información
            seaceobra = r.read('//*[@id="tb_seaceobra"]')
            seaceconsul = r.read('//*[@id="tb_seaceconsul"]')
            seacebien = r.read('//*[@id="tb_seacebien"]')
            seaceserv = r.read('//*[@id="tb_seaceserv"]')

            #     contrato           = r.read('//*[@id="tb_seaceserv"]/tr/td[2]')
            #     contratista        = r.read('//*[@id="tb_seaceserv"]/tr/td[3]')
            #     n_contrato         = r.read('//*[@id="tb_seaceserv"]/tr/td[4]')
            #     fechasuscripcion   = r.read('//*[@id="tb_seaceserv"]/tr/td[5]')
            #     monto_contrato     = r.read('//*[@id="tb_seaceserv"]/tr/td[6]')
            #     monto_item         = r.read('//*[@id="tb_seaceserv"]/tr/td[7]')

            # agregamos la informacion a las listas
            ssi_seaceobra.append(seaceobra)
            ssi_seaceconsul.append(seaceconsul)
            ssi_seacebien.append(seacebien)
            ssi_seaceserv.append(seaceserv)

            #     ssi_contrato.append(contrato)
            #     ssi_contratista.append(contratista)
            #     ssi_n_contrato.append(n_contrato)
            #     ssi_fechasuscripcion.append(fechasuscripcion)
            #     ssi_monto_contrato.append(monto_contrato)
            #     ssi_monto_item.append(monto_item)

        r.close()

        return (
            # Datos generales
            ssi_cui,
            ssi_snip,
            ssi_fecha_registro,
            ssi_nombre_inversion,
            ssi_estado,
            ssi_tipo_inversion,
            ssi_programa_pmi,
            ssi_opmi,
            ssi_uf,
            ssi_uei,
            ssi_situacion,
            ssi_decreto_emergencia,
            ssi_cadena_funcional,
            ssi_viabilidad_aprobacion,
            ssi_costo_aprobado,
            ssi_beneficiarios,
            ssi_expediente_tecnico,
            ssi_reg_seguimiento,
            ssi_registro_cierre,
            ssi_inicio_ejecucion,
            ssi_fin_ejecucion,
            ssi_inversion_actualizado,
            ssi_sol_controversias,
            ssi_carta_fianza,
            ssi_inv_total,
            # Ejecución financiera
            ssi_cost_inversion,
            ssi_devengado_acumulado,
            ssi_avance_financiero_acum,
            ssi_saldo,
            ssi_fecha_primerdevengado,
            ssi_fecha_ultimodevengado,
            # Contrataciones
            ssi_seaceobra,
            ssi_seaceconsul,
            ssi_seacebien,
            ssi_seaceserv,
        )

    def download_data(self):
        (
            # Datos generales
            ssi_cui,
            ssi_snip,
            ssi_fecha_registro,
            ssi_nombre_inversion,
            ssi_estado,
            ssi_tipo_inversion,
            ssi_programa_pmi,
            ssi_opmi,
            ssi_uf,
            ssi_uei,
            ssi_situacion,
            ssi_decreto_emergencia,
            ssi_cadena_funcional,
            ssi_viabilidad_aprobacion,
            ssi_costo_aprobado,
            ssi_beneficiarios,
            ssi_expediente_tecnico,
            ssi_reg_seguimiento,
            ssi_registro_cierre,
            ssi_inicio_ejecucion,
            ssi_fin_ejecucion,
            ssi_inversion_actualizado,
            ssi_sol_controversias,
            ssi_carta_fianza,
            ssi_inv_total,
            # Ejecución financiera
            ssi_cost_inversion,
            ssi_devengado_acumulado,
            ssi_avance_financiero_acum,
            ssi_saldo,
            ssi_fecha_primerdevengado,
            ssi_fecha_ultimodevengado,
            # Contrataciones
            ssi_seaceobra,
            ssi_seaceconsul,
            ssi_seacebien,
            ssi_seaceserv,
        ) = self.scrape_info()
        print(
            f"El total de CUIs scrapeados es: {len(ssi_cui)} y se esta exportando a Excel"
        )
        ssi_mainssi = pd.DataFrame(
            {
                # Datos generales - dg
                "dg_cui": ssi_cui,
                "dg_codio_snip": ssi_snip,
                "dg_fecha_registro": ssi_fecha_registro,
                "dg_nombre_inversion": ssi_nombre_inversion,
                "dg_estado_inversion": ssi_estado,
                "dg_tipo_inversion": ssi_tipo_inversion,
                "dg_programado_pmi": ssi_programa_pmi,
                "dg_opmi": ssi_opmi,
                "dg_uf": ssi_uf,
                "dg_uei": ssi_uei,
                "dg_situcion": ssi_situacion,
                "dg_decreto_emergencia": ssi_decreto_emergencia,
                "dg_cadena_funcional": ssi_cadena_funcional,
                "dg_fecha_viabilidad": ssi_viabilidad_aprobacion,
                "dg_costo_inversion_aprobado": ssi_costo_aprobado,
                "dg_numero_beneficiarios": ssi_beneficiarios,
                "dg_expediente_tecnico": ssi_expediente_tecnico,
                "dg_registro_seguimiento": ssi_reg_seguimiento,
                "dg_registro_cierre": ssi_registro_cierre,
                "dg_inicio_ejecucion": ssi_inicio_ejecucion,
                "dg_fin_ejecucion": ssi_fin_ejecucion,
                "dg_inversion_actualizada": ssi_inversion_actualizado,
                "dg_costo_controversias": ssi_sol_controversias,
                "dg_monto_carta_fianza": ssi_carta_fianza,
                "dg_costo_total_actualizado": ssi_inv_total,
                # Ejecución financiera
                "fin_costo_total_actualizado": ssi_cost_inversion,
                "fin_devengado_acumulado": ssi_devengado_acumulado,
                "fin_avance_financiero_acumulado": ssi_avance_financiero_acum,
                "fin_saldo_por_ejecutar": ssi_saldo,
                "fin_fecha_primer_devengado": ssi_fecha_primerdevengado,
                "fin_fecha_ultimo_devengado": ssi_fecha_ultimodevengado,
                # Contrataciones
                "seaceobra": ssi_seaceobra,
                "seaceconsul": ssi_seaceconsul,
                "seacebien": ssi_seacebien,
                "seaceserv": ssi_seaceserv,
            }
        )
        return ssi_mainssi.to_excel(
            f"{self.path_export}/ssi_SSI_{self.year}_regts_{self.num_range}{self.file_type}",
            index=False,
            header=True,
        )

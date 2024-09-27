tables = {
    "Hricotransa": {
        "campos": [
            "Record_id",
            "FONDO",
            "TIPO",
            "FECHA",
            "CLIENTE",
            "RED",
            "OFICINA",
            "FIDEICOMISO",
            "comprobante",
            "VALOR",
            "unidades",
            "concta",
            "USUARIO",
            "Retencion",
            "Tipo_de_Aporte",
            "CODIGOBPM",
            "HORA",
            "FechaPago",
            "SwImpuesto",
            "CodigoSistema",
            "Maquina",
            "IP",
            "SaldoDespuesMovimiento"
        ],
        "campo_fecha": "FECHA",
        "years":{
            2020:{"meses":[1,2,3,5,6,8]},
            2021:{"meses":[1,2,4,5,7,8,10,11]},
            2021:{"meses":[1,2,4,5,7,8]}
        }
    },
    "Tbl_Log": {
        "campos": [
            "Id",
            "Fecha",
            "IdProceso",
            "Usuario",
            "Ip",
            "Maquina",
            "Descripcion",
            "Objeto",
            "ProcesoExitoso",
            "IDObjeto",
            "EstadoAnteriorObjeto"
        ],
        "campo_fecha": "Fecha",
        "years":{
            2022:{"meses":[11]}
        }
    }, 
    "Tbl_sif_hrico_saldodisponible": {
        "campos": [
            "HSDI_IN_ID",
            "HSDI_IN_FONDO",
            "HSDI_IN_IDENCARGO",
            "HSDI_DT_FECHA",
            "HSDI_DE_RTEXAPLICAR",
            "HSDI_DE_RETENCIONDIA",
            "HSDI_DE_SALDO_DISPONIBLE"
        ],
        "campo_fecha": "HSDI_DT_FECHA",
        "years":{
            2020:{"meses":[1,2,3,4,9]}
        }
    }
}
import streamlit as st
import requests
import json
import pandas as pd  # Asegúrate de tener instalada esta librería
from io import BytesIO
from data import tables

# Configuración del endpoint de la API de Athena
api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/dev/query"

def generar_select(tabla, campos_seleccionados, where_clause, limite):
    campos_str = ", ".join(campos_seleccionados)
    select_query = f"SELECT {campos_str} FROM {tabla}"

    if limite:
        select_query = f"SELECT TOP {limite} {campos_str} FROM {tabla}"
    else:
        select_query = f"SELECT {campos_str} FROM {tabla}"

    if where_clause:
        select_query += f" WHERE {where_clause}"

    return select_query

def generar_where(tabla_seleccionada, selected_years_months):
    campo_fecha = tables[tabla_seleccionada]["campo_fecha"]
    conditions = []

    # Generar condiciones para los años y meses seleccionados
    year_month_conditions = []
    for year, months in selected_years_months.items():
        if months:
            months_str = ", ".join(str(month) for month in months)
            year_month_conditions.append(f"(year({campo_fecha}) = {year} AND month({campo_fecha}) IN ({months_str}))")
    
    # Añadir condiciones de año y mes
    if year_month_conditions:
        conditions.append(f"({' OR '.join(year_month_conditions)})")

    where_clause = " AND ".join(conditions)
    return where_clause if where_clause else None

def get_download_link(output_location):
    api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/dev/dev-us-east-2-data-hist-lbda_s3_dwl_link"
    payload = {"s3_path": output_location}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        download_link = response.json().get("url")
        return download_link
    else:
        st.error(f"Error en la solicitud: {response.status_code}")
        return None

def get_optimizes_query(query, asterisco, fechaField):
    api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/prod/transforQuery"
    payload = {
        "query": query,
        "asterisco": asterisco,
        "fechaField": fechaField
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        transformedQuery = response.json().get("transformedQuery")
        return transformedQuery
    else:
        st.error(f"Error en la solicitud: {response.status_code}")
        return None

def download_and_convert_csv_to_excel(csv_url):
    try:
        # Descargar el archivo CSV desde el enlace
        csv_data = requests.get(csv_url).content
        # Leer el CSV usando pandas
        df = pd.read_csv(BytesIO(csv_data))
        
        # Convertir DataFrame a Excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        return excel_buffer
    except Exception as e:
        st.error(f"Error al descargar o convertir el archivo: {e}")
        return None

def main():
    # Cargar y mostrar el logo
    logo_path = "imagenes/logo.png"
    st.image(logo_path)

    st.title("Temperatura de los Datos")
    st.subheader("Generador de Consultas Athena")

    # Seleccionar una tabla
    tabla_seleccionada = st.selectbox("Selecciona una tabla", list(tables.keys()))

    if tabla_seleccionada:
        # Seleccionar los campos de la tabla
        campos_seleccionados = st.multiselect(
            "Selecciona los campos", tables[tabla_seleccionada]["campos"]
        )

        # Campo opcional para límite
        limite = st.number_input(
            "Especifica el límite de registros (opcional, por defecto es 10)",
            min_value=1, step=1, value=10
        )

        # Filtros por fecha (años y meses disponibles en el JSON)
        st.subheader("Filtros por año y mes")

        available_years = list(tables[tabla_seleccionada]["years"].keys())
        selected_years = st.multiselect("Selecciona los años", available_years)

        selected_years_months = {}
        for year in selected_years:
            available_months = tables[tabla_seleccionada]["years"][year]["meses"]
            selected_months = st.multiselect(f"Selecciona los meses para el año {year}", available_months)
            if selected_months:
                selected_years_months[year] = selected_months

        # Generar cláusula WHERE
        where_clause = generar_where(tabla_seleccionada, selected_years_months)

        # Mostrar la consulta generada
        if campos_seleccionados:
            consulta_sql = generar_select(tabla_seleccionada, campos_seleccionados, where_clause, limite)
            st.write(f"Consulta generada: `{consulta_sql}`")

            # Botón para ejecutar la consulta
            if st.button("Ejecutar consulta"):
                # Paso previo de optimización de la consulta
                campo_fecha = tables[tabla_seleccionada]["campo_fecha"]
                consulta_sql = get_optimizes_query(consulta_sql, campos_seleccionados, campo_fecha)

                st.write(f"Consulta Optimizada: `{consulta_sql}`")

                # Payload para el API Gateway
                payload = {
                    "sql": consulta_sql,
                    "database": "dev-us-east-2-data-hist-athena-dbfondos",
                    "bucketName": "dev-us-east-2-data-hist-s3-dbfondos"
                }

                # Realizar la llamada a la API
                response = requests.post(api_endpoint, json=payload)

                if response.status_code == 200:
                    resultado = response.json()
                    output_location = resultado.get("output_location")
                    if output_location:
                        st.success(f"Consulta ejecutada. Output location: {output_location}")
                        download_link = get_download_link(output_location)
                        if download_link:
                            # Descargar y convertir CSV a Excel
                            excel_file = download_and_convert_csv_to_excel(download_link)
                            if excel_file:
                                st.download_button(
                                    label="Descargar archivo",
                                    data=excel_file,
                                    file_name="consulta.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.error("No se pudo obtener el enlace de descarga.")
                    else:
                        st.error("No se pudo obtener el output_location")
                else:
                    st.write("Error al ejecutar la consulta:", response.text)

if __name__ == "__main__":
    main()

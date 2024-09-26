import streamlit as st
import requests
from data import tables
import json

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

def generar_where(tabla_seleccionada, year, month, day):
    campo_fecha = tables[tabla_seleccionada]["campo_fecha"]
    conditions = []
    
    if year:
        conditions.append(f"year({campo_fecha}) = {year}")
    if month:
        conditions.append(f"month({campo_fecha}) = {month}")
    if day:
        conditions.append(f"day({campo_fecha}) = {day}")
    
    where_clause = " AND ".join(conditions)
    return where_clause if where_clause else None

def get_download_link(output_location):
    api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/dev/dev-us-east-2-data-hist-lbda_s3_dwl_link"
    payload = {"s3_path": output_location}
    headers = {"Content-Type": "application/json"}
    
    # Realizar la solicitud POST al API
    response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        download_link = response.json().get("url")  # Asegúrate de que la respuesta tiene la clave 'download_link'
        return download_link
    else:
        st.error(f"Error en la solicitud: {response.status_code}")
        return None

def get_optimizes_query(query, asterisco, fechaField):
    api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/prod/transforQuery"
    payload={
              "query": query,
              "asterisco": asterisco,
              "fechaField": fechaField
            }
    headers = {"Content-Type": "application/json"}
    
    # Realizar la solicitud POST al API
    response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        print('response.json()',response.json())
        transformedQuery = response.json().get("transformedQuery")  # Asegúrate de que la respuesta tiene la clave 'download_link'

        print('transformedQuery:',transformedQuery)

        return transformedQuery
    else:
        st.error(f"Error en la solicitud: {response.status_code}")
        return None

def main():

    # Cargar y mostrar el logo
    logo_path = "imagenes/logo.png"  # Cambia esta ruta a la ubicación de tu logo
    st.image(logo_path) 

    st.title("Temperatura de los Datos")

    st.subheader("Generador de Consultas Athena")

    consulta_sql = ''

    

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

        # Filtros por fecha (año, mes, día)
        st.subheader("Filtros por fecha")
        year = st.number_input("Año", min_value=2000, max_value=2030, step=1, value=None, format="%d")
        month = st.number_input("Mes", min_value=1, max_value=12, step=1, value=None, format="%d")
        day = st.number_input("Día", min_value=1, max_value=31, step=1, value=None, format="%d")

        # Generar cláusula WHERE
        where_clause = generar_where(tabla_seleccionada, year, month, day)

        # Mostrar la consulta generada
        if campos_seleccionados:

            consulta_sql = generar_select(tabla_seleccionada, campos_seleccionados, where_clause, limite)
            st.write(f"Consulta generada: `{consulta_sql}`")

            # Botón para ejecutar la consulta
            if st.button("Ejecutar consulta"):

                #Paso previo de optimización de la consulta.

                campo_fecha = tables[tabla_seleccionada]["campo_fecha"]

                print('consulta_sql:',consulta_sql)
                print('campo_fecha:',campo_fecha)
                print('campos_seleccionados:',campos_seleccionados)

                consulta_sql = get_optimizes_query(consulta_sql,campos_seleccionados,campo_fecha)

                print('consulta_sql:',consulta_sql)
                st.write("")
                st.write(f"Consulta Optimizada: `{consulta_sql}`")


                # Payload para el API Gateway
                payload = {
                    "sql": consulta_sql,
                    "database": "dev-us-east-2-data-hist-athena-dbfondos",
                    "bucketName": "dev-us-east-2-data-hist-s3-dbfondos"
                }

                # Realizar la llamada a la API
                response = requests.post(api_endpoint, json=payload)

                print('response:',response)

                # Mostrar el resultado de la consulta
                if response.status_code == 200:
                    resultado = response.json()


                    output_location = resultado.get("output_location")

                    print('output_location:',output_location)

                    if output_location:
                        st.success(f"Consulta ejecutada. Output location: {output_location}")

                        # Obtener el enlace de descarga
                        download_link = get_download_link(output_location)

                        if download_link:
                            st.markdown(f"[Haz clic aquí para descargar el archivo]({download_link})")
                    else:
                        st.error("No se pudo obtener el output_location")


                    print('resultado:',resultado)
                    st.write("Resultado:", resultado)
                else:
                    st.write("Error al ejecutar la consulta:", response.text)

if __name__ == "__main__":
    main()

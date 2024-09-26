import streamlit as st
import requests
from data import tables

# Configuración del endpoint de la API de Athena
api_endpoint = "https://tlu537m7x9.execute-api.us-east-2.amazonaws.com/dev/query"

def generar_select(tabla, campos_seleccionados, where_clause, limite):
    campos_str = ", ".join(campos_seleccionados)
    select_query = f"SELECT {campos_str} FROM {tabla}"
    if where_clause:
        select_query += f" WHERE {where_clause}"
    if limite:
        select_query += f" LIMIT {limite}"
    else:
        select_query += " LIMIT 10"
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

def main():
    st.title("Generador de Consultas Athena")

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
                # Payload para el API Gateway
                payload = {
                    "sql": consulta_sql,
                    "database": "dev-us-east-2-data-hist-athena-dbfondos",
                    "bucketName": "dev-us-east-2-data-hist-s3-dbfondos"
                }

                # Realizar la llamada a la API
                response = requests.post(api_endpoint, json=payload)

                # Mostrar el resultado de la consulta
                if response.status_code == 200:
                    resultado = response.json()
                    st.write("Resultado:", resultado)
                else:
                    st.write("Error al ejecutar la consulta:", response.text)

if __name__ == "__main__":
    main()

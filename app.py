import streamlit as st
import requests

# Importar las tablas del archivo data.py
from data import tables

# Configuración del endpoint de la API de Athena
api_endpoint = "https://<tu-api-id>.execute-api.<region>.amazonaws.com/<stage>"

def generar_select(tabla, campos_seleccionados, limite):
    campos_str = ", ".join(campos_seleccionados)
    select_query = f"SELECT {campos_str} FROM {tabla}"
    if limite:
        select_query += f" LIMIT {limite}"
    else:
        select_query += " LIMIT 10"
    return select_query

def main():
    st.title("Generador de Consultas Athena")

    # Seleccionar una tabla
    tabla_seleccionada = st.selectbox("Selecciona una tabla", list(tables.keys()))

    if tabla_seleccionada:
        # Seleccionar los campos de la tabla
        campos_seleccionados = st.multiselect(
            "Selecciona los campos", tables[tabla_seleccionada]
        )

        # Campo opcional para límite
        limite = st.number_input(
            "Especifica el límite de registros (opcional, por defecto es 10)",
            min_value=1, step=1, value=10
        )

        # Mostrar la consulta generada
        if campos_seleccionados:
            consulta_sql = generar_select(tabla_seleccionada, campos_seleccionados, limite)
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

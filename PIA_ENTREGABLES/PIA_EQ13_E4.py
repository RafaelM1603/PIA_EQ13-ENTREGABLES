import os
import re
import requests
import sys
from datetime import datetime
from openpyxl import Workbook
import matplotlib.pyplot as plt

# Parámetros de la API
api_key = 'y40nh635mKlLiWm2v4UZvXeaT2fkxVqzZTplhlLC'
base_url = 'https://api.nasa.gov/neo/rest/v1/feed'

def obtener_d(start_date, end_date, api_key):
    url = f"{base_url}?start_date={start_date}&end_date={end_date}&api_key={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def extraer(datos):
    asteroides = []
    if not datos or "near_earth_objects" not in datos:
        return asteroides

    for fecha, objetos in datos["near_earth_objects"].items():
        for objeto in objetos:
            acercamientos = objeto.get("close_approach_data", [])
            primer_acercamiento = acercamientos[0] if acercamientos else {}

            asteroide = {
                "id": objeto.get("id"),
                "name": objeto.get("name"),
                "absolute_magnitude_h": objeto.get("absolute_magnitude_h"),
                "estimated_diameter": objeto.get("estimated_diameter", {}).get("kilometers", {}).get("estimated_diameter_max", 0),
                "is_potentially_hazardous_asteroid": objeto.get("is_potentially_hazardous_asteroid"),
                "close_approach_date": primer_acercamiento.get("close_approach_date", "N/A"),
                "velocity_kph": primer_acercamiento.get("relative_velocity", {}).get("kilometers_per_hour", "0"),
                "miss_distance_km": primer_acercamiento.get("miss_distance", {}).get("kilometers", "0")
            }
            asteroides.append(asteroide)
    return asteroides

def validar_datos(asteroides):
    validados = []
    for a in asteroides:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", a["close_approach_date"]):
            continue
        try:
            float(a["velocity_kph"])
            float(a["miss_distance_km"])
            float(a["estimated_diameter"])
            validados.append(a)
        except ValueError:
            continue
    return validados

def guardar_en_excel(asteroides, start_date, end_date):
    carpeta = os.path.dirname(os.path.abspath(__file__))
    archivo_excel = os.path.join(carpeta, f"asteroides_{start_date}_a_{end_date}.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Asteroides"

    ws.append(["ID", "Nombre", "Magnitud", "Diámetro (km)", "Peligroso?", "Fecha Aproximación", "Velocidad (km/h)", "Distancia mínima (km)"])
    for a in asteroides:
        ws.append([
            a["id"], a["name"], a["absolute_magnitude_h"], a["estimated_diameter"],
            a["is_potentially_hazardous_asteroid"], a["close_approach_date"],
            a["velocity_kph"], a["miss_distance_km"]
        ])

    wb.save(archivo_excel)
    print(f"Datos guardados en {archivo_excel}")

def generar_graficas(asteroides, start_date, end_date):
    import matplotlib.pyplot as plt

    fechas = [a["close_approach_date"] for a in asteroides]
    diametros = [float(a["estimated_diameter"]) for a in asteroides]
    velocidades = [float(a["velocity_kph"]) for a in asteroides]
    distancias = [float(a["miss_distance_km"]) for a in asteroides]
    nombres = [a["name"] for a in asteroides]

    peligrosos = sum(1 for a in asteroides if a["is_potentially_hazardous_asteroid"])
    no_peligrosos = len(asteroides) - peligrosos

    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Análisis de Asteroides Cercanos a la Tierra", fontsize=16)

    # Gráfico de líneas
    axs[0, 0].plot(fechas, velocidades, marker='o', color='blue')
    axs[0, 0].set_title("Velocidad vs Fecha")
    axs[0, 0].set_xlabel("Fecha")
    axs[0, 0].set_ylabel("Velocidad (km/h)")
    axs[0, 0].tick_params(axis='x', rotation=45)
    axs[0, 0].grid(True)

    # Gráfico de barras
    axs[0, 1].bar(nombres, diametros, color='green')
    axs[0, 1].set_title("Diámetro por Asteroide")
    axs[0, 1].set_xlabel("Nombre")
    axs[0, 1].set_ylabel("Diámetro (km)")
    axs[0, 1].tick_params(axis='x', rotation=90)
    axs[0, 1].grid(axis='y')

    # Diagrama de dispersión
    axs[1, 0].scatter(diametros, distancias, c='red')
    axs[1, 0].set_title("Diámetro vs Distancia mínima")
    axs[1, 0].set_xlabel("Diámetro (km)")
    axs[1, 0].set_ylabel("Distancia mínima (km)")
    axs[1, 0].grid(True)

    # Gráfico de pastel
    axs[1, 1].pie([peligrosos, no_peligrosos],
                 labels=["Peligrosos", "No peligrosos"],
                 autopct='%1.1f%%',
                 colors=['red', 'lightgreen'],
                 startangle=90)
    axs[1, 1].set_title("Proporción de Asteroides Peligrosos")

    # Ajustar diseño y guardar
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("graficas_asteroides.png")
    plt.close()
    print("Gráficas guardadas en graficas_asteroides.png")

def validar_fechas(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        print("Error: Formato de fecha incorrecto. Usa YYYY-MM-DD.")
        sys.exit(1)

    if start_date > end_date:
        print("Error: La fecha de inicio no puede ser posterior a la fecha de fin.")
        sys.exit(1)

    if (end_date - start_date).days > 7:
        print("Error: El rango entre fechas no puede exceder los 7 días.")
        sys.exit(1)

    return start_date_str, end_date_str

def main():
    print("Consulta de asteroides y cometas cercanos a la Tierra - API de NASA")

    start_date = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
    end_date = input("Ingrese la fecha de fin (YYYY-MM-DD): ")

    # Validación de fechas
    start_date, end_date = validar_fechas(start_date, end_date)

    print("\nObteniendo datos de la NASA...\n")
    datos = obtener_d(start_date, end_date, api_key)
    asteroides = extraer(datos)
    asteroides = validar_datos(asteroides)

    if asteroides:
        guardar_en_excel(asteroides, start_date, end_date)
        generar_graficas(asteroides, start_date, end_date)
    else:
        print("No se encontraron asteroides válidos para graficar.")

if __name__ == '__main__':
    main()  

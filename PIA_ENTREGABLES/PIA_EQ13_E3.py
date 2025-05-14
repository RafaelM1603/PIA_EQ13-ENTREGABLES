import requests
from datetime import datetime

# Parámetros de la API
api_key = 'y40nh635mKlLiWm2v4UZvXeaT2fkxVqzZTplhlLC'
base_url = 'https://api.nasa.gov/neo/rest/v1/feed'
"""start_date = '2025-04-20'  
end_date = '2025-04-22'    # La fecha final debe estar dentro de los 7 días del inicio"""

def obtener_d(start_date, end_date, api_key):
    url = f"{base_url}?start_date={start_date}&end_date={end_date}&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        datos = response.json()
        return datos
    elif response.status_code == 400:
        print("Error: Solicitud incorrecta. Verifique los parámetros de entrada.")
        return None
    elif response.status_code == 404:
        print("Error: No se encontraron datos para las fechas proporcionadas.")
        return None
    elif response.status_code == 408:
        print("Error: Tiempo de espera agotado. Intente nuevamente.")
        return None
    elif response.status_code == 444:
        print("Error: No se encontraron datos para las fechas proporcionadas.")
        return None
    elif response.status_code == 500:
        print("Error: Error interno del servidor. Intente nuevamente más tarde.")
        return None
    elif response.status_code == 502:
        print("Error: Puerta de enlace incorrecta. Intente nuevamente más tarde.")
        return None
    elif response.status_code == 503:
        print("Error: Servicio no disponible. Intente nuevamente más tarde.")
        return None
    elif response.status_code == 521:
        print("Error: El servidor está caído. Intente nuevamente más tarde.")
        return None
    elif response.status_code == 522:
        print("Error: Tiempo de espera agotado. Intente nuevamente más tarde.")
        return None
    else:
        print(f"Error: {response.status_code}")
        return None
    
def extraer(datos):
    asteroides = []
    if not datos or "near_earth_objects" not in datos:
        print("No se han encontraron datos.")
        return asteroides
    
    for fecha, objetos in datos["near_earth_objects"].items():
        for objeto in objetos:
            asteroide = {
                "id": objeto.get("id"),
                "name": objeto.get("name"),
                "nasa_jpl_url": objeto.get("nasa_jpl_url"),
                "absolute_magnitude_h": objeto.get("absolute_magnitude_h"),
                "estimated_diameter": objeto.get("estimated_diameter"),
                "is_potentially_hazardous_asteroid": objeto.get("is_potentially_hazardous_asteroid"),
                "close_approach_data": [],
                "orbital_data": objeto.get("orbital_data")
            }

            for acercamiento in objeto.get("close_approach_data", []):
                acercamiento_info = {
                    "close_approach_date": acercamiento.get("close_approach_date"),
                    "relative_velocity": acercamiento.get("relative_velocity"),
                    "miss_distance": acercamiento.get("miss_distance"),
                    "orbiting_body": acercamiento.get("orbiting_body")
                }
                asteroide["close_approach_data"].append(acercamiento_info)

            asteroides.append(asteroide)

    return asteroides

def fechaa(prom):
    while True:
        fecha = input(prom)
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
            return fecha
        except ValueError:
            print("Formato de fecha incorrecto. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")

def main():
    print("Consulta de asteroides y cometas cercanos a la Tierra - API de NASA")

    start_date = fechaa("Ingrese la fecha de inicio (YYYY-MM-DD): ")
    end_date = fechaa("Ingrese la fecha de fin (YYYY-MM-DD): ")

    print("\nObteniendo datos de la NASA...\n")
    datos = obtener_d(start_date, end_date, api_key)
    asteroides = extraer(datos)
    
    nombre_archivo = f"asteroides_{start_date}_a_{end_date}.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        resumen = f"\nSe encontraron {len(asteroides)} asteroides entre {start_date} y {end_date}.\n"
        print(resumen)
        archivo.write(resumen + "\n")

        for a in asteroides:
            texto = (
                "Asteroide\n"
                f"ID: {a['id']}\n"
                f"Nombre: {a['name']}\n"
                f"URL NASA: {a['nasa_jpl_url']}\n"
                f"Magnitud: {a['absolute_magnitude_h']}\n"
                f"Peligroso?: {a['is_potentially_hazardous_asteroid']}\n"
            )
            if a['close_approach_data']:
                acercamiento = a['close_approach_data'][0]
                texto += f"Aproximación más cercana: {acercamiento['close_approach_date']}\n"
                texto += f"Velocidad relativa (km/h): {acercamiento['relative_velocity']['kilometers_per_hour']}\n"
                texto += f"Distancia mínima (km): {acercamiento['miss_distance']['kilometers']}\n"
                texto += f"Cuerpo orbital: {acercamiento['orbiting_body']}\n"
            texto += "-" * 40 + "\n"

            print(texto)
            archivo.write(texto)

    print(f"\nDatos guardados en el archivo: {nombre_archivo}")

if __name__ == '__main__':
    main()



"""
id: Identificador único del objeto asignado por la NASA.
name: Nombre del asteroide o cometa.
nasa_jpl_url: URL al perfil del objeto en el sistema JPL Small-Body Database.
absolute_magnitude_h: Magnitud absoluta del objeto, que indica su brillo intrínseco.
estimated_diameter: Estimación del diámetro del objeto en varios rangos de unidades: kilómetros, metros, 
millas y pies. Cada uno proporciona valores mínimos y máximos.
is_potentially_hazardous_asteroid: Indica si el objeto es potencialmente peligroso para la Tierra (true o false).
close_approach_data: Lista de acercamientos cercanos del objeto a la Tierra, incluyendo:

close_approach_date: Fecha del acercamiento.
relative_velocity: Velocidad relativa del objeto respecto a la Tierra, en km/h, km/s y mph.
miss_distance: Distancia mínima entre el objeto y la Tierra durante el acercamiento, en unidades como 
kilómetros, millas, unidades astronómicas (au) y distancias lunares.
orbiting_body: Cuerpo celeste alrededor del cual orbita el objeto durante el acercamiento (por ejemplo, 
la Tierra).

orbital_data: Información sobre la órbita del objeto, incluyendo parámetros como:

orbit_id: Identificador de la órbita.
eccentricity: Excentricidad de la órbita.
semi_major_axis: Semieje mayor de la órbita.
inclination: Inclinación orbital.
ascending_node_longitude: Longitud del nodo ascendente.
orbital_period: Período orbital del objeto."""
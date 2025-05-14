import re
import numpy as np
import statistics
from collections import defaultdict
import PIA_EQ13_E3

def leer_archivo(PIA_EQ13_E3):
    try:
        with open(PIA_EQ13_E3, "r", encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {PIA_EQ13_E3}")
        return ""

def extraer_datos(texto):
    patron = r"""
        ID:\s(?P<id>\d+)\n
        Nombre:\s(?P<nombre>.+?)\n
        URL\sNASA:\s(?P<url>https?://[^\n]+)\n
        Magnitud:\s(?P<magnitud>[\d.]+)\n
        Peligroso\?\:\s(?P<peligroso>True||False)\n
        Aproximación\smás\scercana:\s(?P<fecha>\d{4}-\d{2}-\d{2})\n
        Velocidad\srelativa\s\(km/h\):\s(?P<velocidad>[\d.]+)\n
        Distancia\smínima\s\(km\):\s(?P<distancia>[\d.]+)\n
        Cuerpo\sorbital:\s(?P<cuerpo>\w+)
    """
    datos = []
    for match in re.finditer(patron, texto, re.VERBOSE):
        datos.append({
            "id": int(match.group("id")),
            "nombre": match.group("nombre"),
            "url": match.group("url"),
            "magnitud": float(match.group("magnitud")),
            "peligroso": match.group("peligroso") == "True",
            "fecha": match.group("fecha"),
            "velocidad_kmh": float(match.group("velocidad")),
            "distancia_km": float(match.group("distancia")),
            "cuerpo_orbital": match.group("cuerpo")
        })
    return datos

def analizar_datos(datos):
    velocidades = [d["velocidad_kmh"] for d in datos]
    distancias = [d["distancia_km"] for d in datos]
    magnitudes = [d["magnitud"] for d in datos]

    resumen = {
        "velocidad_media": np.mean(velocidades),
        "velocidad_mediana": np.median(velocidades),
        "velocidad_moda": statistics.mode(velocidades) if len(set(velocidades)) != len(velocidades) else "No hay moda",
        "velocidad_std": np.std(velocidades),

        "distancia_media": np.mean(distancias),
        "distancia_mediana": np.median(distancias),
        "distancia_moda": statistics.mode(distancias) if len(set(distancias)) != len(distancias) else "No hay moda",
        "distancia_std": np.std(distancias),

        "magnitud_media": np.mean(magnitudes),
        "magnitud_std": np.std(magnitudes),
    }

    return resumen

def preparar_datos_visualizacion(datos):
    por_dia = defaultdict(list)
    for d in datos:
        por_dia[d["fecha"]].append({
            "nombre": d["nombre"],
            "velocidad": d["velocidad_kmh"],
            "distancia": d["distancia_km"],
            "peligroso": d["peligroso"]
        })
    return dict(por_dia)

def main():
    nombre_archivo = input("Ingrese el nombre del archivo de datos generado por el primer script: ")
    texto = leer_archivo(nombre_archivo)

    print("\nProcesando datos...")
    datos = extraer_datos(texto)

    if not datos:
        print("No se encontraron datos válidos.")
        return

    print(f"\nSe procesaron {len(datos)} registros.")
    
    resumen = analizar_datos(datos)
    for k, v in resumen.items():
        print(f"{k.replace('_', ' ').capitalize()}: {v}")

    datos_visualizacion = preparar_datos_visualizacion(datos)
    print("\nDatos listos para visualización (estructura por fecha con velocidad/distancia/peligro).")

if __name__ == '__main__':
    main()

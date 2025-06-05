import json
import os

ARCHIVO_IDS = "mensajes_recientes.json"

def cargar_ids():
    if not os.path.exists(ARCHIVO_IDS):
        return set()
    with open(ARCHIVO_IDS, "r", encoding="utf-8") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()

def guardar_ids(ids):
    with open(ARCHIVO_IDS, "w", encoding="utf-8") as f:
        json.dump(list(ids)[-500:], f)  # Guarda solo los últimos 500

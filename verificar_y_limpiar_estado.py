import json
import os

RUTA_JSON = "dalgoro-webhook1\\estado_usuarios.json"

def cargar_estados():
    if not os.path.exists(RUTA_JSON):
        print("❌ No existe el archivo estado_usuarios.json")
        return {}

    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("_default", {})
        except Exception as e:
            print(f"❌ Error al leer el archivo: {e}")
            return {}

def guardar_estados(registros):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump({"_default": registros}, f, indent=2)
        print("✅ Archivo actualizado correctamente.")

def listar_estados(registros):
    if not registros:
        print("✅ No hay registros actualmente.")
        return

    print(f"📊 Hay {len(registros)} registros:")
    for k, estado in registros.items():
        print(f" - ID interno: {k} | chat_id: {estado.get('chat_id')} | etapa: {estado.get('etapa')} | actividad: {estado.get('actividad')}")

def eliminar_chat_id(registros, chat_id_objetivo):
    claves_a_eliminar = [k for k, e in registros.items() if e.get("chat_id") == chat_id_objetivo]
    if not claves_a_eliminar:
        print("❌ No se encontró ese chat_id en los registros.")
        return registros

    for k in claves_a_eliminar:
        print(f"🗑 Eliminando entrada: {registros[k]}")
        registros.pop(k)

    return registros

if __name__ == "__main__":
    estados = cargar_estados()
    listar_estados(estados)

    opcion = input("¿Deseas eliminar algún chat_id específico? (s/n): ").strip().lower()
    if opcion == "s":
        chat_id = input("🔢 Ingresa el chat_id completo (ej: 593xxxxxxxxx@c.us): ").strip()
        nuevos_estados = eliminar_chat_id(estados, chat_id)
        guardar_estados(nuevos_estados)

import os
import json
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware # Opcional, pero puede ayudar con el rendimiento
from datetime import datetime # Asegurar que datetime se importe así
from pytz import timezone as pytz_timezone # Para definir la zona horaria de Ecuador
from dateutil.parser import isoparse
from json.decoder import JSONDecodeError

# --- Configuration ---
db_directory = "data" # Carpeta para almacenar la base de datos
db_path = os.path.join(db_directory, 'estado_usuarios.json')
ZONA_ECUADOR = pytz_timezone('America/Guayaquil')

# --- Google Sheets Integration (Optional) ---
CAN_USE_SHEETS = False
try:
    from google_sheets_utils import cargar_estados_desde_sheets, guardar_estado_en_sheets
    CAN_USE_SHEETS = True
    print("INFO: Integración con Google Sheets habilitada.")
except ImportError:
    print("ADVERTENCIA: `google_sheets_utils` no encontrado o no se pudo importar. La carga/guardado de estado en Sheets estará deshabilitada.")
    # Define funciones dummy si no se pueden importar para evitar errores NameError más adelante
    def cargar_estados_desde_sheets():
        print("DEBUG: `cargar_estados_desde_sheets` (dummy) llamada.")
        return []
    def guardar_estado_en_sheets(chat_id, estado):
        print(f"DEBUG: `guardar_estado_en_sheets` (dummy) llamada para {chat_id}.")
        pass # No hacer nada

def _ensure_db_directory():
    """Asegura que el directorio para la base de datos exista."""
    if not os.path.exists(db_directory):
        try:
            os.makedirs(db_directory)
            print(f"INFO: Directorio de base de datos creado en '{db_directory}'")
        except OSError as e:
            print(f"ERROR: No se pudo crear el directorio de la base de datos '{db_directory}': {e}")
            raise

def _create_empty_db_file(path):
    """Crea un archivo JSON vacío y válido para TinyDB."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"_default": {}}, f) # Estructura base de TinyDB con la tabla por defecto
    print(f"INFO: Archivo de base de datos vacío creado en '{path}'")

def cargar_db_instance():
    """
    Carga o inicializa la base de datos TinyDB 'estado_usuarios.json'.
    Intenta reconstruir desde Google Sheets si el archivo local no existe o está corrupto.
    """
    _ensure_db_directory()

    needs_reconstruction = False
    backup_path = None

    if not os.path.exists(db_path):
        print(f"INFO: {db_path} no existe.")
        needs_reconstruction = True
    else:
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"INFO: {db_path} existe pero está vacío.")
                    needs_reconstruction = True
                else:
                    data = json.loads(content)
                    if not isinstance(data, dict) or (len(data) > 0 and "_default" not in data and not all(isinstance(k, str) and isinstance(v, dict) for k, v in data.items())):
                        print(f"ERROR: {db_path} parece corrupto (estructura interna no esperada por TinyDB).")
                        needs_reconstruction = True
        except json.JSONDecodeError:
            print(f"ERROR: {db_path} corrupto (JSON inválido).")
            needs_reconstruction = True
        except Exception as e:
            print(f"ERROR: Error inesperado al verificar {db_path}: {e}.")
            needs_reconstruction = True

        if needs_reconstruction and os.path.exists(db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{db_path}.corrupt.{timestamp}"
            try:
                os.rename(db_path, backup_path)
                print(f"INFO: Archivo corrupto renombrado a {backup_path}")
            except OSError as e:
                print(f"ERROR: No se pudo renombrar el archivo corrupto {db_path}: {e}")

    if needs_reconstruction:
        if CAN_USE_SHEETS:
            print("INFO: Intentando reconstruir/poblar base de datos desde Google Sheets...")
            try:
                estados_desde_sheets = cargar_estados_desde_sheets()
                _create_empty_db_file(db_path) # Asegura que el archivo base exista y esté vacío
                # Usar CachingMiddleware para potencialmente mejorar el rendimiento en escrituras/lecturas frecuentes
                temp_db = TinyDB(db_path, storage=CachingMiddleware(JSONStorage), encoding='utf-8', ensure_ascii=False, indent=4)
                if estados_desde_sheets:
                    # Asegurarse que estados_desde_sheets es una lista de diccionarios
                    if isinstance(estados_desde_sheets, list) and all(isinstance(item, dict) for item in estados_desde_sheets):
                        temp_db.table(TinyDB.DEFAULT_TABLE_NAME).truncate()
                        temp_db.table(TinyDB.DEFAULT_TABLE_NAME).insert_multiple(estados_desde_sheets)
                        print(f"INFO: {len(estados_desde_sheets)} estados cargados desde Sheets y guardados en {db_path}.")
                    else:
                        print("ERROR: `cargar_estados_desde_sheets` no devolvió una lista de diccionarios. No se poblará la DB.")
                else:
                    print(f"ADVERTENCIA: No se cargaron estados desde Sheets o la lista estaba vacía.")
                # No cerramos temp_db aquí porque la vamos a retornar para uso global
                return temp_db
            except Exception as e:
                print(f"ERROR: Error crítico durante la reconstrucción desde Sheets: {e}. Se creará una DB vacía.")
                _create_empty_db_file(db_path)
                return TinyDB(db_path, storage=CachingMiddleware(JSONStorage), encoding='utf-8', ensure_ascii=False, indent=4)
        else:
            print("INFO: Google Sheets no disponible. Creando base de datos local vacía.")
            _create_empty_db_file(db_path)
            return TinyDB(db_path, storage=CachingMiddleware(JSONStorage), encoding='utf-8', ensure_ascii=False, indent=4)
    else:
        print(f"INFO: Usando base de datos existente: {db_path}")
        return TinyDB(db_path, storage=CachingMiddleware(JSONStorage), encoding='utf-8', ensure_ascii=False, indent=4)

# --- Inicialización Global ÚNICA y Correcta ---
db = cargar_db_instance()
Conversacion = Query()

def _get_default_new_state(chat_id_str):
    """Genera un estado nuevo por defecto para un chat_id."""
    return {
        "chat_id": chat_id_str,
        "actividad": None,
        "etapa": None,
        "fase": "inicio",
        "ultima_interaccion": datetime.now(ZONA_ECUADOR).isoformat(), # Guardar como ISO string
        "intentos_negativos": 0,
        "ultimo_mensaje_id": None
    }

def obtener_estado(chat_id):
    chat_id_str = str(chat_id)
    resultado = db.get(Conversacion.chat_id == chat_id_str)

    if resultado:
        # Convertir 'ultima_interaccion' de string a datetime al cargar
        if "ultima_interaccion" in resultado and isinstance(resultado["ultima_interaccion"], str):
            try:
                resultado["ultima_interaccion"] = isoparse(resultado["ultima_interaccion"])
            except ValueError:
                print(f"ADVERTENCIA: No se pudo convertir 'ultima_interaccion' a datetime para {chat_id_str}: {resultado['ultima_interaccion']}. Usando ahora.")
                resultado["ultima_interaccion"] = datetime.now(ZONA_ECUADOR)
        elif not isinstance(resultado.get("ultima_interaccion"), datetime):
             resultado["ultima_interaccion"] = datetime.now(ZONA_ECUADOR)

        # Asegurar campos por defecto si faltan
        resultado.setdefault("actividad", None)
        resultado.setdefault("etapa", None)
        resultado.setdefault("fase", "inicio")
        resultado.setdefault("intentos_negativos", 0)
        resultado.setdefault("ultimo_mensaje_id", None)
        resultado["chat_id"] = chat_id_str # Asegurar que el chat_id sea el correcto
        return resultado
    else:
        return _get_default_new_state(chat_id_str)

def guardar_estado(chat_id, estado_a_guardar):
    chat_id_str = str(chat_id)
    estado_actualizado = estado_a_guardar.copy()

    estado_actualizado["chat_id"] = chat_id_str # Asegurar que el chat_id esté y sea string

    # Convertir 'ultima_interaccion' a string ISO antes de guardar si es datetime
    ultima_interaccion_val = estado_actualizado.get("ultima_interaccion")
    if isinstance(ultima_interaccion_val, datetime):
        estado_actualizado["ultima_interaccion"] = ultima_interaccion_val.isoformat()
    elif ultima_interaccion_val is None: # Si es None, establecer a ahora
         estado_actualizado["ultima_interaccion"] = datetime.now(ZONA_ECUADOR).isoformat()
    # Si ya es un string, se asume que está en formato ISO (o se validó antes)

    # Asegurar otros campos por defecto antes de guardar
    estado_actualizado.setdefault("actividad", None)
    estado_actualizado.setdefault("etapa", None)
    estado_actualizado.setdefault("fase", "inicio")
    estado_actualizado.setdefault("intentos_negativos", 0)
    estado_actualizado.setdefault("ultimo_mensaje_id", None)

    # print(f"DEBUG: Estado a guardar en DB para {chat_id_str}: {estado_actualizado}")
    db.upsert(estado_actualizado, Conversacion.chat_id == chat_id_str)

    if CAN_USE_SHEETS:
        try:
            guardar_estado_en_sheets(chat_id_str, estado_actualizado)
        except Exception as e:
            print(f"ERROR: No se pudo guardar estado en Sheets para {chat_id_str}: {e}")

def reiniciar_estado(chat_id):
    chat_id_str = str(chat_id)
    print(f"INFO: Reiniciando estado para {chat_id_str}")
    db.remove(Conversacion.chat_id == chat_id_str)
    estado_inicial = _get_default_new_state(chat_id_str)
    guardar_estado(chat_id_str, estado_inicial)
    print(f"INFO: Estado reiniciado y guardado para {chat_id_str}.")

def obtener_estado_seguro(chat_id):
    chat_id_str = str(chat_id)
    try:
        return obtener_estado(chat_id_str)
    except Exception as e:
        print(f"ERROR: Error crítico al obtener estado para {chat_id_str}: {e}. Devolviendo estado por defecto.")
        return _get_default_new_state(chat_id_str)

def mensaje_ya_procesado(chat_id, mensaje_id):
    chat_id_str = str(chat_id)
    mensaje_id_str = str(mensaje_id) if mensaje_id is not None else None
    if not mensaje_id_str:
        return False
    estado = obtener_estado_seguro(chat_id_str)
    return estado.get("ultimo_mensaje_id") == mensaje_id_str

def registrar_mensaje_procesado(chat_id, mensaje_id):
    chat_id_str = str(chat_id)
    mensaje_id_str = str(mensaje_id) if mensaje_id is not None else None
    if not mensaje_id_str:
        return
    estado = obtener_estado_seguro(chat_id_str)
    estado["ultimo_mensaje_id"] = mensaje_id_str
    guardar_estado(chat_id_str, estado)

# --- Bloque de prueba (opcional) ---
if __name__ == '__main__':
    print("Ejecutando pruebas de estado_storage.py...")
    # Simular que google_sheets_utils no está disponible para algunas pruebas
    # o mockear sus funciones si se quiere probar la lógica de reconstrucción.

    # global CAN_USE_SHEETS
    # CAN_USE_SHEETS = False # Descomentar para probar sin Sheets
    # print(f"CAN_USE_SHEETS for testing: {CAN_USE_SHEETS}")

    test_chat_id1 = "test_user_1"
    test_chat_id2 = "test_user_2"

    # Limpiar archivos de db de pruebas anteriores si existen
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(db_directory) and not os.listdir(db_directory):
        os.rmdir(db_directory) # Eliminar si está vacío
    elif os.path.exists(db_directory) and os.listdir(db_directory) == [os.path.basename(db_path)]:
        # Si solo contiene el archivo db y este fue eliminado, también eliminar dir
        if not os.path.exists(db_path): os.rmdir(db_directory)

    print(f"\n--- Prueba 1: Inicialización de DB (archivo no existente) ---")
    # db es global, se inicializa al cargar el módulo. Si el archivo no existe, cargar_db_instance() lo maneja.
    # Para forzar una nueva carga y ver los prints, tendríamos que reimportar o llamar directamente.
    # Por ahora, asumimos que la carga inicial del módulo ya llamó a cargar_db_instance()
    if not os.path.exists(db_path):
        print(f"ERROR DE PRUEBA: {db_path} no fue creado en la carga inicial del módulo.")
    else:
        print(f"INFO: {db_path} existe después de la carga inicial del módulo.")

    print(f"\n--- Prueba 2: Obtener y guardar estado para {test_chat_id1} ---")
    reiniciar_estado(test_chat_id1) # Asegurar estado limpio
    estado = obtener_estado_seguro(test_chat_id1)
    print(f"Estado inicial para {test_chat_id1}: {estado}")
    assert estado["fase"] == "inicio", f"Estado inicial no es 'inicio'"
    assert estado["chat_id"] == test_chat_id1

    estado["actividad"] = "mineria"
    estado["etapa"] = "permiso_no"
    estado["ultimo_mensaje_id"] = "msg_abc"
    guardar_estado(test_chat_id1, estado)

    estado_recuperado = obtener_estado_seguro(test_chat_id1)
    print(f"Estado recuperado para {test_chat_id1}: {estado_recuperado}")
    assert estado_recuperado["actividad"] == "mineria"
    assert estado_recuperado["etapa"] == "permiso_no"
    assert estado_recuperado["ultimo_mensaje_id"] == "msg_abc"
    assert isinstance(estado_recuperado["ultima_interaccion"], datetime)

    print(f"\n--- Prueba 3: Manejo de mensaje procesado para {test_chat_id1} ---")
    assert not mensaje_ya_procesado(test_chat_id1, "msg_xyz")
    registrar_mensaje_procesado(test_chat_id1, "msg_xyz")
    assert mensaje_ya_procesado(test_chat_id1, "msg_xyz")

    print(f"\n--- Prueba 4: Estado para nuevo usuario {test_chat_id2} ---")
    estado_otro_usuario = obtener_estado_seguro(test_chat_id2)
    print(f"Estado inicial para {test_chat_id2}: {estado_otro_usuario}")
    assert estado_otro_usuario["fase"] == "inicio"
    assert estado_otro_usuario["chat_id"] == test_chat_id2

    print("\n--- Prueba 5: Simulación de archivo DB corrupto/eliminado ---")
    db.close() # Cerrar la instancia actual
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"INFO: {db_path} eliminado para simular corrupción.")

    # Recargar la instancia (esto es lo que haría el script al reiniciarse)
    db_reloaded = cargar_db_instance()
    estado_post_reconstruccion = db_reloaded.get(Conversacion.chat_id == test_chat_id1)
    if CAN_USE_SHEETS:
        print("INFO: Se esperaría recuperación desde Sheets si hubiera datos allí.")
        # Aquí podrías añadir aserciones si mockeas `cargar_estados_desde_sheets` para devolver algo.
    else:
        assert estado_post_reconstruccion is None, "El estado no debería existir después de eliminar DB y sin carga de Sheets."
        print("INFO: DB recreada como vacía (sin Sheets), estado anterior no encontrado, como se esperaba.")

    # Probar obtener estado después de la recreación forzará la creación de uno nuevo por defecto
    estado_nuevo_despues_recreacion = obtener_estado(test_chat_id1) # Usa la 'db' global que fue reasignada por cargar_db_instance si se llama de nuevo
                                                                # Para que esta prueba sea más fiel, la db global debería reasignarse:
                                                                # global db, Conversacion
                                                                # db = cargar_db_instance()
                                                                # Conversacion = Query()
    # Para la prueba actual, vamos a operar sobre db_reloaded directamente
    estado_nuevo_directo_reloaded_db = db_reloaded.get(Conversacion.chat_id == test_chat_id1)
    if estado_nuevo_directo_reloaded_db is None:
        estado_nuevo_directo_reloaded_db = _get_default_new_state(test_chat_id1)
        db_reloaded.insert(estado_nuevo_directo_reloaded_db)

    print(f"Estado para {test_chat_id1} después de recreación y obtención: {estado_nuevo_directo_reloaded_db}")
    assert estado_nuevo_directo_reloaded_db["fase"] == "inicio"

    db_reloaded.close()
    # Limpieza final para no dejar el archivo de prueba si se ejecuta múltiples veces
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(db_directory) and not os.listdir(db_directory):
        os.rmdir(db_directory)

    print("\nPruebas de estado_storage.py completadas.")

# test_sistema_integrado.py

from datetime import datetime
from zona_horaria import ZONA_HORARIA_EC
from gestor_conversacion import manejar_conversacion, reiniciar_conversacion
from estado_storage import obtener_estado_seguro
from pprint import pprint

def probar_flujo_completo(chat_id, mensajes_usuario):
    print(f"\n📲 Iniciando simulación para: {chat_id}")
    reiniciar_conversacion(chat_id)

    for mensaje in mensajes_usuario:
        print(f"\n👤 Usuario: {mensaje}")
        respuesta = manejar_conversacion(chat_id, mensaje, actividad=None, fecha_actual=datetime.now(ZONA_HORARIA_EC))
        if respuesta:
            print(f"🤖 Bot: {respuesta}")
        else:
            print("🤖 Bot no respondió (posible bloqueo o duplicado)")

    print("\n📦 Estado final almacenado:")
    estado = obtener_estado_seguro(chat_id)
    pprint(estado)

# 🧪 Escenarios de prueba
pruebas = {
    "cliente_1": [
        "Hola",  # Activación inicial
        "Tengo una finca bananera",  # Detectar actividad
        "Sí tengo permiso",  # Etapa permiso_si
        "Puedo el jueves a las 10am en oficina",  # Agenda
    ],
    "cliente_2": [
        "Hola, necesito ayuda",  # Activación
        "es una camaronera",  # Detectar actividad
        "No tengo ningún permiso aún",  # Etapa permiso_no
        "pueden venir el viernes a las 8am a la finca",  # Agenda
    ],
    "cliente_3": [
        "Hola",  # Activación
        "Trabajo con cacao",  # Actividad ambigua: espera detectar como cacaotera
        "ya tengo todo en regla",  # Etapa permiso_si
        "el lunes a las 14:00 está bien en oficina",  # Agenda
    ],
    "cliente_4": [
        "buenas tardes",  # Activación
        "ninguna de las anteriores",  # Actividad no reconocida
        "cultivo de ciclo corto",  # Aclaración
        "sí, tengo permiso",  # permiso_si
        "agendemos el martes a las 9am",  # Agenda
    ],
}

# 🔁 Ejecutar todas las pruebas
for chat_id, mensajes in pruebas.items():
    probar_flujo_completo(chat_id, mensajes)

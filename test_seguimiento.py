
# test_seguimiento.py

from seguimiento_silencio import obtener_mensaje_seguimiento
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import RESPUESTA_INICIAL
from datetime import datetime, timedelta

def simular_interaccion(minutos_silencio, cliente_reaparece):
    ahora = datetime.now()
    ultima_interaccion = ahora - timedelta(minutes=minutos_silencio)

    print(f"⏱ Tiempo sin respuesta: {minutos_silencio} min")

    if cliente_reaparece:
        if debe_reiniciar_flujo(ultima_interaccion, ahora):
            print("🔁 Cliente respondió después del límite. Reiniciar flujo.")
            print("Mensaje de reinicio:", RESPUESTA_INICIAL.strip())
        else:
            print("✅ Cliente respondió dentro del flujo. Continuar normalmente.")
    else:
        seguimiento = obtener_mensaje_seguimiento(minutos_silencio)
        if seguimiento:
            print("📩 Enviar seguimiento:", seguimiento)
        else:
            print("🛑 No se debe enviar más seguimientos.")

    print("—" * 60)

if __name__ == "__main__":
    escenarios = [
        (10, False),
        (30, False),
        (60, False),
        (4320, False),     # 3 días
        (4351, False),     # 3 días + 31 min sin respuesta
        (4351, True),      # cliente reaparece después de 3 días + 31 min
        (60, True)         # cliente reaparece dentro del flujo
    ]

    for minutos, reaparece in escenarios:
        simular_interaccion(minutos, reaparece)

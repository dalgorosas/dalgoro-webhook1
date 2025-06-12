from datetime import datetime
from gestor_conversacion import enviar_alerta_a_personal

# ✅ Simulación de datos ambiguos del cliente
chat_id_prueba = "593984770663@c.us@c.us"  # No agregar otro @c.us aquí
mensaje_prueba = "Podría ser la próxima semana en la tarde"
actividad_prueba = "camaronera"
etapa_prueba = "cierre"
fase_prueba = "esperando_cita"
fecha_actual = datetime.now()
nombre_cliente = "Cliente de prueba"

# ✅ Ejecutar función como si fuera parte del flujo normal
enviar_alerta_a_personal(
    chat_id=chat_id_prueba.replace("@c.us@c.us", "@c.us"),  # Protección adicional
    mensaje=mensaje_prueba,
    actividad=actividad_prueba,
    etapa=etapa_prueba,
    fase=fase_prueba,
    fecha=fecha_actual,
    nombre=nombre_cliente
)

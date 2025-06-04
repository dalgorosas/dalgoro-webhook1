
# test_agradecimiento.py

from respuestas_finales import obtener_mensaje_agradecimiento

# Actividades de prueba
actividades = ["bananera", "camaronera", "minería", "hoteles", "industria", "otros", "actividad_no_definida"]

for actividad in actividades:
    mensaje = obtener_mensaje_agradecimiento(actividad)
    print(f"Actividad: {actividad}")
    print("Mensaje:", mensaje)
    print("-" * 50)

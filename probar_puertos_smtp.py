import socket

def probar_puerto(servidor, puerto):
    try:
        with socket.create_connection((servidor, puerto), timeout=5):
            print(f"✅ Puerto {puerto} en {servidor} está ABIERTO")
    except Exception as e:
        print(f"❌ Puerto {puerto} en {servidor} está CERRADO o BLOQUEADO")
        print("   → Detalle:", e)

if __name__ == "__main__":
    servidor = "smtp.gmail.com"
    puertos = [465, 587]
    for puerto in puertos:
        probar_puerto(servidor, puerto)

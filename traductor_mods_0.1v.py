from deep_translator import GoogleTranslator
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# 🌟 Caché para no traducir lo mismo varias veces
cache = {}

# Hilo para manejar timeout
executor = ThreadPoolExecutor(max_workers=1)

# ======================
# Función de traducción con timeout
# ======================
def traducir(texto, linea_num=None):
    if texto in cache:
        return cache[texto]

    try:
        future = executor.submit(GoogleTranslator(source='auto', target='es').translate, texto)
        traduccion = future.result(timeout=5)  # 5 segundos de timeout
    except TimeoutError:
        traduccion = texto
        if linea_num:
            print(f"\n[Timeout] Línea {linea_num} no respondió, se usa texto original.")
    except Exception as e:
        traduccion = texto
        if linea_num:
            print(f"\n[Error] Línea {linea_num} omitida: {e}")

    cache[texto] = traduccion
    return traduccion

# ======================
# Traduce una línea CSV segura
# ======================
def traducir_linea(linea, linea_num):
    if ";" not in linea:
        return linea

    partes = linea.split(";")
    if len(partes) < 6:
        return linea

    original = partes[1].strip()

    # 🔹 No traducir si:
    # - está vacío
    # - es "x"
    # - es "..."
    # - contiene solo símbolos sin al menos una letra
    if (original == "" 
        or original.lower() in ["x", "..."] 
        or not any(c.isalpha() for c in original)):
        print(f"\n⚠️ Línea {linea_num} no se traducirá (contenido: '{original}')")
        return linea

    # 🔹 Traducción normal
    traduccion = traducir(original, linea_num)
    partes[5] = traduccion
    return ";".join(partes)

# ======================
# Leer archivo con distintos encoding
# ======================
def leer_archivo(ruta):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(ruta, "r", encoding=encoding) as f:
                return f.readlines()
        except:
            continue
    raise Exception(f"No se pudo leer: {ruta}")

# ======================
# Procesa un archivo CSV
# ======================
def procesar_archivo(ruta):
    if ruta.endswith("_es.csv"):
        return

    try:
        lineas = leer_archivo(ruta)
    except:
        print(f"❌ Error leyendo: {ruta}")
        return

    total = len(lineas)
    print(f"\n📄 {os.path.basename(ruta)} ({total} líneas)")

    nuevas = []
    ruta_nueva = ruta.replace(".csv", "_es.csv")
    guardar_cada = max(1, total // 3)  # cada 33%
    
    for i, linea in enumerate(lineas, 1):
        nuevas.append(traducir_linea(linea.strip(), i))

        # 🔥 Barra de progreso
        progreso = int((i / total) * 30)
        barra = "█" * progreso + "-" * (30 - progreso)
        porcentaje = int((i / total) * 100)
        print(f"\r[{barra}] {porcentaje}% ({i}/{total})", end="", flush=True)

        # 💾 Guardado cada 33% directamente en el archivo final
        if i % guardar_cada == 0:
            with open(ruta_nueva, "w", encoding="utf-8") as f:
                f.write("\n".join(nuevas))
            print(f"\n💾 Guardado automático al {int((i/total)*100)}%")

    # Guardado final
    with open(ruta_nueva, "w", encoding="utf-8") as f:
        f.write("\n".join(nuevas))

    try:
        os.remove(ruta)
    except:
        pass

    print(f"✔ Terminado: {os.path.basename(ruta)}")

# ======================
# Procesa todos los CSV de una carpeta
# ======================
def procesar_carpeta(ruta):
    if not os.path.exists(ruta):
        print("❌ Carpeta no válida")
        return

    archivos = []
    for root, dirs, files in os.walk(ruta):
        for file in files:
            if file.endswith(".csv") and not file.endswith("_es.csv"):
                archivos.append(os.path.join(root, file))

    print(f"📦 {len(archivos)} archivos\n")

    for archivo in archivos:
        procesar_archivo(archivo)

    print("\n🎉 TERMINADO TODO")
    print(f"🧠 Traducciones únicas: {len(cache)}")

# ======================
# EJECUCIÓN PRINCIPAL
# ======================
if __name__ == "__main__":
    ruta = input("📂 Carpeta del mod: ").strip().strip('"')
    procesar_carpeta(ruta)
    input("\nPresiona ENTER para salir...")
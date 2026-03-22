from deep_translator import GoogleTranslator
import os
import sys

cache = {}

def traducir(texto):
    if texto in cache:
        return cache[texto]

    try:
        traduccion = GoogleTranslator(source='auto', target='es').translate(texto)
    except:
        traduccion = texto

    cache[texto] = traduccion
    return traduccion

def traducir_linea(linea):
    if ";" not in linea:
        return linea

    partes = linea.split(";")

    if len(partes) < 6:
        return linea

    original = partes[1].strip()

    if original == "" or original.lower() == "x":
        return linea

    traduccion = traducir(original)

    partes[5] = traduccion

    return ";".join(partes)

def leer_archivo(ruta):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(ruta, "r", encoding=encoding) as f:
                return f.readlines()
        except:
            continue
    raise Exception(f"No se pudo leer: {ruta}")

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
    for i, linea in enumerate(lineas, 1):
        nuevas.append(traducir_linea(linea.strip()))

        # 🔥 BARRA DE PROGRESO
        progreso = int((i / total) * 30)
        barra = "█" * progreso + "-" * (30 - progreso)
        porcentaje = int((i / total) * 100)

        print(f"\r[{barra}] {porcentaje}% ({i}/{total})", end="", flush=True)

    print()  # salto de línea limpio

    ruta_nueva = ruta.replace(".csv", "_es.csv")

    with open(ruta_nueva, "w", encoding="utf-8") as f:
        f.write("\n".join(nuevas))

    try:
        os.remove(ruta)
    except:
        pass

    print(f"✔ Terminado: {os.path.basename(ruta)}")

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

# ▶️ EJECUCIÓN
if __name__ == "__main__":
    ruta = input("📂 Carpeta del mod: ").strip().strip('"')
    procesar_carpeta(ruta)

    input("\nPresiona ENTER para salir...")
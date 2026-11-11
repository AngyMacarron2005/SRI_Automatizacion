
import os
import sys
import time
import zipfile
import platform
import subprocess
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from playwright.sync_api import sync_playwright


# ==========================================
# CONFIGURACION GENERAL
# ==========================================

URL_LOGIN_SRI = "https://srienlinea.sri.gob.ec/"
PUERTO_CDP = 9222
URL_CDP = f"http://127.0.0.1:{PUERTO_CDP}/json/version"


def obtener_directorio():
    """Obtiene la carpeta del programa, tanto en Python como en EXE."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def buscar_chrome():
    """Busca la instalación de Google Chrome en Windows."""

    posibles_rutas = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
        / "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
        / "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/Application/chrome.exe"
    ]

    for ruta in posibles_rutas:
        if ruta.is_file():
            return ruta

    return None


def comprobar_chrome():
    """Comprueba que Chrome responde correctamente mediante CDP."""

    try:
        with urllib.request.urlopen(URL_CDP, timeout=2) as respuesta:
            import json

            datos = json.loads(respuesta.read().decode("utf-8"))

            print("-> Chrome detectado:", datos.get("Browser"))
            print("-> WebSocket disponible:",
                  bool(datos.get("webSocketDebuggerUrl")))

            return (
                respuesta.status == 200
                and datos.get("Browser", "").startswith("Chrome/")
                and bool(datos.get("webSocketDebuggerUrl"))
            )

    except Exception as e:
        print("-> Chrome todavía no esta disponible:", e)
        return False


def preparar_chrome():
    """Inicia Chrome con depuracion si todavía no está disponible."""

    if comprobar_chrome():
        print("-> Chrome ya esta preparado.")
        return True

    chrome = buscar_chrome()

    if chrome is None:
        messagebox.showerror(
            "Error",
            "No se encontro Google Chrome instalado."
        )
        return False

    perfil = (
        Path(os.environ["LOCALAPPDATA"])
        / "SRI_Chrome_Debug"
    )
    
    print("==========================================")
    print(" DIAGNOSTICO DE INICIO DE CHROME")
    print("==========================================")
    print(f"Chrome encontrado: {chrome}")
    print(f"Perfil utilizado: {perfil}")
    print(f"Puerto CDP: {PUERTO_CDP}")
    print(f"Directorio del programa: {obtener_directorio()}")
    print("==========================================")

    perfil.mkdir(parents=True, exist_ok=True)

    print("-> Iniciando Google Chrome...")

    try:
        subprocess.Popen([
            str(chrome),
            f"--remote-debugging-port={PUERTO_CDP}",
            f"--user-data-dir={perfil}",
            "--new-window",
            URL_LOGIN_SRI
        ])
    except Exception as e:
        messagebox.showerror(
            "Error al iniciar Chrome",
            str(e)
        )
        return False

    print("-> Esperando conexion con Chrome...")

    for intento in range(30):
        if comprobar_chrome():
            print("-> Chrome esta listo.")
            return True

        time.sleep(1)

    messagebox.showerror(
        "Error de conexion",
        "Chrome no respondio en el puerto 9222.\n\n"
        "Comprueba que el navegador se haya iniciado correctamente."
    )

    return False


def preparar_chrome():
    """Prepara Chrome utilizando Ejecutar_SRI.bat."""

    directorio = obtener_directorio()
    archivo_bat = directorio / "Ejecutar_SRI.bat"

    if not archivo_bat.is_file():
        messagebox.showerror(
            "Error",
            f"No se encontro el archivo:\n{archivo_bat}"
        )
        return False

    print("-> Preparando Chrome mediante Ejecutar_SRI.bat...")

    try:
        resultado = subprocess.run(
            ["cmd.exe", "/c", str(archivo_bat), "PREPARAR"],
            cwd=str(directorio),
            check=False
        )

        if resultado.returncode != 0:
            messagebox.showerror(
                "Error",
                "No se pudo preparar Google Chrome."
            )
            return False

        print("-> Chrome preparado correctamente.")
        return True

    except Exception as e:
        messagebox.showerror(
            "Error al ejecutar BAT",
            str(e)
        )
        return False

# ==========================================
# AUTOMATIZACION SRI
# ==========================================

def automatizar_descargas():

    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Robot SRI - Finetic C.L.",
        "¡Hola! Vamos a preparar Google Chrome.\n\n"
        "1. Inicia sesion en el SRI.\n"
        "2. Resuelve el reCAPTCHA.\n"
        "3. Navega a 'Comprobantes electronicos recibidos'.\n"
        "4. Selecciona tus fechas y haz clic en CONSULTAR.\n\n"
        "Cuando las facturas aparezcan en pantalla, haz clic en OK."
    )

    script_dir = obtener_directorio()

    print("\n==========================================")
    print("       ROBOT SRI - FINETIC C.L.")
    print("==========================================")

    # Preparar Chrome automáticamente
    if not preparar_chrome():
        return

    print("\n-> Conectando con Google Chrome mediante CDP...")

    # IMPORTANTE: Playwright permanece activo durante todo el proceso
    with sync_playwright() as p:

        try:
            browser = p.chromium.connect_over_cdp(
                URL_CDP.replace("/json/version", ""),
                timeout=15000
            )

            if not browser.contexts:
                raise Exception(
                    "No se encontro un contexto de navegador."
                )

            browser_context = browser.contexts[0]

            pages = browser_context.pages

            page = next(
                (
                    pestaña for pestaña in pages
                    if "srienlinea.sri.gob.ec" in pestaña.url
                ),
                None
            )

            if page is None:
                page = browser_context.new_page()
                page.goto(URL_LOGIN_SRI)

            page.bring_to_front()

            print("-> Conexion con Chrome establecida correctamente.")
            print("-> Pestana actual:", page.url)

        except Exception as e:
            messagebox.showerror(
                "Error de conexion",
                "No se pudo conectar con Google Chrome.\n\n"
                f"Detalle del error:\n{e}"
            )
            return

        # ==========================================
        # BUCLE CONTINUO DE DESCARGA
        # ==========================================

        while True:

            messagebox.showinfo(
                "Sincronizacion Lista",
                "Realiza tu consulta de fechas en el SRI "
                "y cuando las facturas aparezcan en pantalla, "
                "haz clic en OK para descargar."
            )

            # Seleccionar la carpeta de destino
            carpeta_destino = filedialog.askdirectory(
                parent=root,
                title="Selecciona dónde guardar las facturas",
                mustexist=True
            )

            if not carpeta_destino:
                messagebox.showinfo(
                    "Operación cancelada",
                    "No seleccionaste una carpeta de destino."
                )
                continue

            # Solicitar nombre del respaldo
            nombre_mes = simpledialog.askstring(
                "Nombre del Respaldo",
                "Ingresa el nombre para esta carpeta y su ZIP\n"
                "(ej. noviembre_2026):",
                initialvalue="Nombre_Carpeta",
                parent=root
            )

            if nombre_mes is None:
                continue

            nombre_mes = nombre_mes.strip()

            # Evitar caracteres no permitidos en nombres de Windows
            nombre_mes = "".join(
                "_" if c in '<>:"/\\|?*' else c
                for c in nombre_mes
            ).strip(" .")

            if not nombre_mes:
                nombre_mes = "respaldo_general"

            # Convertir la ubicación seleccionada en una ruta
            base_destino = Path(carpeta_destino)

            # Crear las carpetas de respaldo
            respaldo_pdf_dir = base_destino / f"respaldo_{nombre_mes}"
            xml_temp_dir = base_destino / f"xml_temp_{nombre_mes}"
            zip_dest_dir = base_destino / "facturas_descargadas"

            print(f"-> Carpeta seleccionada: {base_destino}")
            print(f"-> Nombre del respaldo: {nombre_mes}")

            # Preparar directorios
            respaldo_pdf_dir.mkdir(parents=True, exist_ok=True)
            xml_temp_dir.mkdir(parents=True, exist_ok=True)
            zip_dest_dir.mkdir(parents=True, exist_ok=True)

            # Limpiar archivos anteriores del mismo respaldo
            for directorio in (respaldo_pdf_dir, xml_temp_dir):
                for archivo in directorio.iterdir():
                    if archivo.is_file():
                        archivo.unlink()

            print(
                f"-> Analizando filas visibles para '{nombre_mes}'..."
            )

            try:
                page.wait_for_load_state("load", timeout=15000)
                page.wait_for_selector(
                    "table tbody tr",
                    timeout=30000
                )
            except Exception:
                pass

            try:
                filas = page.locator(
                    "table tbody tr:visible"
                ).all()

            except Exception as e:
                messagebox.showerror(
                    "Error de pagina",
                    "No se pudo leer la tabla del SRI.\n\n"
                    f"Detalle: {e}"
                )
                continue

            if len(filas) == 0:
                messagebox.showwarning(
                    "Sin resultados",
                    "No se encontraron facturas visibles "
                    "para las fechas consultadas.\n"
                    "Verifica tu consulta en el SRI."
                )
                continue

            print(f"-> Se encontraron {len(filas)} filas.")

            exitos_xml = 0
            exitos_pdf = 0

            # ==========================================
            # DESCARGAR XML Y PDF
            # ==========================================

            for i, fila in enumerate(filas, start=1):

                try:
                    xml_link = fila.locator(
                        "td"
                    ).nth(9).locator("a")

                    if xml_link.count() > 0:

                        with page.expect_download() as download_info:
                            xml_link.click()

                        download = download_info.value

                        ruta_xml = (
                            xml_temp_dir / download.suggested_filename
                        )

                        if ruta_xml.exists():
                            ruta_xml = (
                                xml_temp_dir
                                / f"{i}_{download.suggested_filename}"
                            )

                        download.save_as(ruta_xml)
                        exitos_xml += 1

                    ride_link = fila.locator(
                        "td"
                    ).nth(10).locator("a")

                    if ride_link.count() > 0:

                        with page.expect_download() as download_info:
                            ride_link.click()

                        download = download_info.value

                        nombre_pdf = download.suggested_filename
                        ruta_pdf = respaldo_pdf_dir / nombre_pdf

                        if ruta_pdf.exists():
                            ruta_pdf = (
                                respaldo_pdf_dir
                                / f"factura_{i}_{nombre_pdf}"
                            )

                        download.save_as(ruta_pdf)
                        exitos_pdf += 1

                    time.sleep(0.8)

                except Exception as ex:
                    print(
                        f"AVISO en la factura {i}: {ex}"
                    )

            # ==========================================
            # COMPRIMIR XML
            # ==========================================

            print("-> Comprimiendo archivos XML...")

            zip_path = (
                zip_dest_dir / f"facturas_xml_{nombre_mes}.zip"
            )

            with zipfile.ZipFile(
                zip_path,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zipf:

                for archivo_xml in xml_temp_dir.iterdir():

                    if archivo_xml.is_file():
                        zipf.write(
                            archivo_xml,
                            archivo_xml.name
                        )

            # ==========================================
            # ABRIR CARPETAS
            # ==========================================

            try:

                if platform.system() == "Windows":

                    os.startfile(str(zip_dest_dir))
                    os.startfile(str(respaldo_pdf_dir))

                else:

                    subprocess.run([
                        "xdg-open",
                        str(zip_dest_dir)
                    ])

                    subprocess.run([
                        "xdg-open",
                        str(respaldo_pdf_dir)
                    ])

            except Exception:
                pass

            # ==========================================
            # RESUMEN DEL PROCESO
            # ==========================================

            print("\n-> PROCESO COMPLETADO")
            print(f"-> XML descargados: {exitos_xml}")
            print(f"-> PDF descargados: {exitos_pdf}")

            repetir = messagebox.askyesno(
                "¡Proceso Completado!",
                f"Las facturas de '{nombre_mes}' fueron procesadas.\n\n"
                f"XML descargados: {exitos_xml}\n"
                f"PDF descargados: {exitos_pdf}\n\n"
                "¿Deseas descargar otro periodo o fecha?"
            )

            if not repetir:

                messagebox.showinfo(
                    "Robot SRI",
                    "¡Gracias por usar el sistema de Finetic C.L. "
                    "Hasta luego!"
                )

                break


if __name__ == "__main__":
    if "--ejecutar" in sys.argv:
        automatizar_descargas()
    else:
        directorio = obtener_directorio()

        archivo_bat = directorio / "Ejecutar_SRI.bat"

        subprocess.Popen(
            ["cmd.exe", "/c", str(archivo_bat)],
            cwd=str(directorio)
        )
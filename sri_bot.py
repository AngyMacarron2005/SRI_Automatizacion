
import os
import time
import zipfile
import platform
import subprocess
from pathlib import Path

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

from playwright.sync_api import sync_playwright


def automatizar_descargas():

    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Robot SRI - Finetic C.L.",
        "¡Hola! Vamos a conectar con Google Chrome.\n\n"
        "1. Abre Chrome utilizando el acceso configurado para el SRI.\n"
        "2. Inicia sesión y resuelve el reCAPTCHA.\n"
        "3. Navega a 'Comprobantes electrónicos recibidos'.\n"
        "4. Selecciona tus fechas y haz clic en CONSULTAR.\n\n"
        "Cuando las facturas aparezcan en pantalla, haz clic en OK."
    )

    url_login_sri = "https://srienlinea.sri.gob.ec/"

    print("\n-> Conectando con Google Chrome mediante CDP...")

    # ==========================================
    # CONEXIÓN CON GOOGLE CHROME MEDIANTE CDP
    # ==========================================

    with sync_playwright() as p:

        try:
            browser = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222",
                timeout=10000
            )

            if not browser.contexts:
                raise Exception("No se encontró un contexto de navegador.")

            browser_context = browser.contexts[0]

            # Buscar una pestaña que tenga abierto el SRI
            pages = browser_context.pages

            page = next(
                (
                    pestaña for pestaña in pages
                    if "srienlinea.sri.gob.ec" in pestaña.url
                ),
                None
            )

            # Si no existe una pestaña del SRI, abrir una nueva
            if page is None:
                page = browser_context.new_page()
                page.goto(url_login_sri)

            page.bring_to_front()

            print("-> Conexión con Chrome establecida correctamente.")
            print("-> Pestaña actual:", page.url)

        except Exception as e:

            messagebox.showerror(
                "Error de conexión",
                "No se pudo conectar con Google Chrome.\n\n"
                "Comprueba lo siguiente:\n"
                "1. Chrome está abierto.\n"
                "2. Se inició con el puerto 9222.\n"
                "3. La dirección 127.0.0.1:9222/json/version funciona.\n\n"
                f"Detalle del error:\n{e}"
            )

            return

        # ==========================================
        # BUCLE CONTINUO DE DESCARGA
        # ==========================================

        while True:

            messagebox.showinfo(
                "Sincronización Lista",
                "Realiza tu consulta de fechas en el SRI y "
                "cuando las facturas aparezcan en pantalla, "
                "haz clic en OK para descargar."
            )

            # ==========================================
            # SELECCIONAR CARPETA DE DESTINO
            # ==========================================

            ruta_seleccionada = filedialog.askdirectory(
                parent=root,
                title="Selecciona la carpeta donde guardar las facturas",
                mustexist=True
            )

            if not ruta_seleccionada:
                continue

            # ==========================================
            # SOLICITAR NOMBRE DEL RESPALDO
            # ==========================================

            nombre_mes = simpledialog.askstring(
                "Nombre de Respaldo",
                "Ingresa el nombre para esta carpeta y su ZIP\n"
                "(ej. octubre, noviembre):",
                initialvalue="Nombre_Carpeta",
                parent=root
            )

            if nombre_mes is None:
                continue

            nombre_mes = nombre_mes.strip()

            if not nombre_mes:
                nombre_mes = "respaldo_general"

            # Evitar caracteres no permitidos en nombres de Windows
            caracteres_invalidos = '<>:"/\\|?*'

            if any(c in caracteres_invalidos for c in nombre_mes):
                messagebox.showerror(
                    "Nombre no válido",
                    "El nombre contiene caracteres no permitidos.\n"
                    "Por favor, utiliza otro nombre."
                )
                continue

            # ==========================================
            # DEFINIR RUTAS DE ALMACENAMIENTO
            # ==========================================

            base_dir = Path(ruta_seleccionada)

            respaldo_pdf_dir = base_dir / f"respaldo_{nombre_mes}"
            xml_temp_dir = base_dir / f"xml_temp_{nombre_mes}"
            zip_dest_dir = base_dir / "facturas_descargadas"

            # Limpiar archivos anteriores del mismo respaldo
            if respaldo_pdf_dir.exists():
                for archivo in respaldo_pdf_dir.iterdir():
                    if archivo.is_file():
                        archivo.unlink()

            if xml_temp_dir.exists():
                for archivo in xml_temp_dir.iterdir():
                    if archivo.is_file():
                        archivo.unlink()

            # Crear las carpetas
            respaldo_pdf_dir.mkdir(parents=True, exist_ok=True)
            xml_temp_dir.mkdir(parents=True, exist_ok=True)
            zip_dest_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n-> Carpeta seleccionada: {base_dir}")
            print(f"-> PDF: {respaldo_pdf_dir}")
            print(f"-> XML: {xml_temp_dir}")
            print(f"-> ZIP: {zip_dest_dir}")

            # ==========================================
            # ANALIZAR FACTURAS DEL SRI
            # ==========================================

            print(
                f"-> Analizando filas visibles en pantalla "
                f"para guardarlas en '{nombre_mes}'..."
            )

            try:
                page.wait_for_load_state("load", timeout=15000)
                page.wait_for_selector(
                    "table tbody tr",
                    timeout=30000
                )
            except Exception:
                pass

            filas = page.locator("table tbody tr:visible").all()

            if len(filas) == 0:

                messagebox.showwarning(
                    "Sin resultados",
                    "No se encontraron facturas visibles para "
                    "las fechas consultadas.\n"
                    "Por favor, verifica tu consulta en el SRI."
                )

                continue

            print(f"-> Se encontraron {len(filas)} filas.")

            # ==========================================
            # DESCARGAR XML Y PDF
            # ==========================================

            for i, fila in enumerate(filas, start=1):

                try:

                    # Descargar XML
                    xml_link = fila.locator("td").nth(9).locator("a")

                    if xml_link.count() > 0:

                        with page.expect_download() as download_info:
                            xml_link.click()

                        download = download_info.value

                        ruta_xml = (
                            xml_temp_dir / download.suggested_filename
                        )

                        if ruta_xml.exists():
                            ruta_xml = (
                                xml_temp_dir /
                                f"{i}_{download.suggested_filename}"
                            )

                        download.save_as(ruta_xml)

                    # Descargar PDF
                    ride_link = fila.locator("td").nth(10).locator("a")

                    if ride_link.count() > 0:

                        with page.expect_download() as download_info:
                            ride_link.click()

                        download = download_info.value

                        nombre_pdf = download.suggested_filename

                        ruta_pdf = respaldo_pdf_dir / nombre_pdf

                        if ruta_pdf.exists():
                            ruta_pdf = (
                                respaldo_pdf_dir /
                                f"factura_{i}_{nombre_pdf}"
                            )

                        download.save_as(ruta_pdf)

                    print(f"-> Factura {i} procesada.")

                    time.sleep(0.8)

                except Exception as ex:

                    print(
                        f"⚠️ Aviso en la factura {i}: {ex}"
                    )

            # ==========================================
            # COMPRIMIR ARCHIVOS XML
            # ==========================================

            print("-> Comprimiendo archivos XML...")

            zip_path = (
                zip_dest_dir /
                f"facturas_xml_{nombre_mes}.zip"
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
            # ABRIR CARPETAS DE DESTINO
            # ==========================================

            print("-> Abriendo carpetas de destino...")

            try:

                if platform.system() == "Windows":

                    os.startfile(str(zip_dest_dir.absolute()))
                    os.startfile(str(respaldo_pdf_dir.absolute()))

                else:

                    subprocess.run([
                        "xdg-open",
                        str(zip_dest_dir.absolute())
                    ])

                    subprocess.run([
                        "xdg-open",
                        str(respaldo_pdf_dir.absolute())
                    ])

            except Exception as e:

                print(f"⚠️ No se pudieron abrir las carpetas: {e}")

            # ==========================================
            # PREGUNTAR SI DESEA REPETIR EL PROCESO
            # ==========================================

            repetir = messagebox.askyesno(
                "¡Proceso Completado!",
                f"Las facturas de '{nombre_mes}' se descargaron.\n\n"
                f"Ubicación:\n{base_dir}\n\n"
                "¿Deseas descargar otro periodo o fecha?"
            )

            if not repetir:

                messagebox.showinfo(
                    "Robot SRI",
                    "¡Gracias por usar el sistema de Finetic C.L. "
                    "Hasta luego!"
                )

                break

    root.destroy()


if __name__ == "__main__":
    automatizar_descargas()

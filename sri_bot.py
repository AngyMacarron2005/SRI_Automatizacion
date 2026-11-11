import os
import time
import zipfile
import platform
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox
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
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("\n-> Conectando con Google Chrome mediante CDP...")

    with sync_playwright() as p:
        try:
            # Conectarse al Chrome que ya está abierto
            browser = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222",
                timeout=10000
            )

            # Obtener el contexto principal de Chrome
            if not browser.contexts:
                raise Exception("No se encontró un contexto de navegador.")

            browser_context = browser.contexts[0]

            # Buscar una pestaña que ya tenga abierto el SRI
            pages = browser_context.pages

            page = next(
                (
                    pestaña for pestaña in pages
                    if "srienlinea.sri.gob.ec" in pestaña.url
                ),
                None
            )

            # Si no existe una pestaña del SRI, crear una nueva
            if page is None:
                page = browser_context.new_page()
                page.goto(url_login_sri)

            # Llevar la pestaña del SRI al frente
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

    # A partir de aquí continúa tu código original:
    # Bucle continuo de descarga


        # 🔄 BUCLE CONTINUO DE DESCARGA
        while True:
            messagebox.showinfo(
                "Sincronización Lista", 
                "Realiza tu consulta de fechas en el SRI y cuando las facturas aparezcan en pantalla, haz clic en OK para descargar."
            )

            nombre_mes = simpledialog.askstring(
                "Nombre de Respaldo", 
                "Ingresa el nombre para esta carpeta y su ZIP\n(ej. octubre, noviembre):",
                initialvalue="Nombre_Carpeta"
            )
            
            if nombre_mes is None:
                continue

            nombre_mes = nombre_mes.strip()
            if not nombre_mes:
                nombre_mes = "respaldo_general"

            respaldo_pdf_dir = Path(script_dir) / f"respaldo_{nombre_mes}"
            xml_temp_dir = Path(script_dir) / "xml_temp"
            zip_dest_dir = Path(script_dir) / "facturas_descargadas"

            if respaldo_pdf_dir.exists():
                for f in respaldo_pdf_dir.iterdir():
                    if f.is_file(): f.unlink()
            if xml_temp_dir.exists():
                for f in xml_temp_dir.iterdir():
                    if f.is_file(): f.unlink()

            respaldo_pdf_dir.mkdir(exist_ok=True)
            xml_temp_dir.mkdir(exist_ok=True)
            zip_dest_dir.mkdir(exist_ok=True)

            print(f"-> Analizando filas visibles en pantalla para guardarlas en '{nombre_mes}'...")
            
            try:
                page.wait_for_load_state("load", timeout=15000)
                page.wait_for_selector("table tbody tr", timeout=30000)
            except Exception:
                pass

            filas = page.locator("table tbody tr:visible").all()

            if len(filas) == 0:
                messagebox.showwarning(
                    "Sin resultados", 
                    "No se encontraron facturas visibles para las fechas consultadas.\nPor favor, verifica tu consulta en el SRI."
                )
                continue

            for i, fila in enumerate(filas, start=1):
                try:
                    xml_link = fila.locator("td").nth(9).locator("a")
                    if xml_link.count() > 0:
                        with page.expect_download() as download_info:
                            xml_link.click()
                        download = download_info.value
                        ruta_xml = xml_temp_dir / download.suggested_filename
                        if ruta_xml.exists():
                            ruta_xml = xml_temp_dir / f"{i}_{download.suggested_filename}"
                        download.save_as(ruta_xml)

                    ride_link = fila.locator("td").nth(10).locator("a")
                    if ride_link.count() > 0:
                        with page.expect_download() as download_info:
                            ride_link.click()
                        download = download_info.value
                        nombre_pdf = download.suggested_filename
                        ruta_pdf = respaldo_pdf_dir / nombre_pdf
                        if ruta_pdf.exists():
                            ruta_pdf = respaldo_pdf_dir / f"factura_{i}_{nombre_pdf}"
                        download.save_as(ruta_pdf)

                    time.sleep(0.8)

                except Exception as ex:
                    print(f"⚠️ Aviso en la factura {i}: {ex}")

            print("-> Comprimiendo archivos XML...")
            zip_path = zip_dest_dir / f"facturas_xml_{nombre_mes}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for archivo_xml in xml_temp_dir.iterdir():
                    if archivo_xml.is_file():
                        zipf.write(archivo_xml, archivo_xml.name)
            
            try:
                if platform.system() == "Windows":
                    os.startfile(str(zip_dest_dir.absolute()))
                    os.startfile(str(respaldo_pdf_dir.absolute()))
                else:
                    subprocess.run(["xdg-open", str(zip_dest_dir.absolute())])
                    subprocess.run(["xdg-open", str(respaldo_pdf_dir.absolute())])
            except Exception:
                pass

            repetir = messagebox.askyesno(
                "¡Proceso Completado!", 
                f"Las facturas de '{nombre_mes}' se descargaron con éxito.\n\n¿Deseas descargar otro periodo o fecha?"
            )
            
            if not repetir:
                messagebox.showinfo("Robot SRI", "¡Gracias por usar el sistema de Finetic C.L. Hasta luego!")
                break

if __name__ == "__main__":
    automatizar_descargas()
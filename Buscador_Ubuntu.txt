import os
import time
import zipfile
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox
from playwright.sync_api import sync_playwright

def automatizar_descargas():
    # Inicializamos la ventanita oculta de tkinter para los popups
    root = tk.Tk()
    root.withdraw() # Oculta la ventana principal vacía
    
    # 1. Alerta visual de instrucciones iniciales
    messagebox.showinfo(
        "Robot SRI - Finetic C.L.", 
        "¡Hola! El navegador se abrirá a continuación.\n\n"
        "1. Inicia sesión en el portal.\n"
        "2. Navega a 'Comprobantes electrónicos recibidos'.\n"
        "3. Selecciona tus fechas y haz clic en CONSULTAR.\n\n"
        "Haz clic en OK una vez que estés viendo la tabla con las facturas listas."
    )
    
    url_login_sri = "https://srienlinea.sri.gob.ec/"

    print("\n-> Abriendo Brave...")
    cmd = [
        "brave-browser",
        "--remote-debugging-port=9222",
        f"--user-data-dir={os.path.expanduser('~')}/chrome_sri_profile",
        "--ozone-platform=x11",
        url_login_sri
    ]
    
    subprocess.Popen(cmd)
    time.sleep(3)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            default_context = browser.contexts[0]
            
            pages = default_context.pages
            page = pages[0] if pages else default_context.new_page()
            
            for p_extra in pages[1:]:
                try:
                    p_extra.close()
                except:
                    pass
            
            page.goto(url_login_sri)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al navegador: {e}")
            return

        # 🔄 BUCLE CONTINUO
        while True:
            # 2. Ventana emergente para confirmar que la tabla ya está lista
            messagebox.showinfo(
                "Sincronización Lista", 
                "Realiza tu consulta de fechas en el SRI y cuando las facturas aparezcan en pantalla, haz clic en OK para descargar."
            )

            # 3. Ventana emergente para pedir el nombre (con validación si hace clic en Cancelar)
            nombre_mes = simpledialog.askstring(
                "Nombre de Respaldo", 
                "Ingresa el nombre para esta carpeta y su ZIP\n(ej. octubre, noviembre):",
                initialvalue="Nombre_Carpeta"
            )
            
            # Si el usuario hace clic en "Cancelar", no rompe el programa, solo vuelve a preguntar
            if nombre_mes is None:
                continue

            nombre_mes = nombre_mes.strip()
            if not nombre_mes:
                nombre_mes = "respaldo_general"

            respaldo_pdf_dir = Path(f"./respaldo_{nombre_mes}")
            xml_temp_dir = Path("./xml_temp")
            zip_dest_dir = Path("./facturas_descargadas")

            # Limpieza automática de carpetas temporales para esta nueva iteración
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
            
            filas = page.locator("table tbody tr:visible").all()
            print(f"-> Se detectaron {len(filas)} facturas visibles para descargar.")

            # 🛡️ VALIDACIÓN: Si no hay facturas en la tabla, avisa y vuelve a empezar el ciclo sin error
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
            
            # Abrir carpetas de resultados
            subprocess.run(["xdg-open", str(zip_dest_dir.absolute())])
            subprocess.run(["xdg-open", str(respaldo_pdf_dir.absolute())])

            # ❓ Preguntar si desea realizar otra descarga
            repetir = messagebox.askyesno(
                "¡Proceso Completado!", 
                f"Las facturas de '{nombre_mes}' se descargaron con éxito.\n\n¿Deseas descargar otro periodo o fecha?"
            )
            
            if not repetir:
                messagebox.showinfo("Robot SRI", "¡Gracias por usar el sistema de Finetic C.L. Hasta luego!")
                break

if __name__ == "__main__":
    automatizar_descargas()
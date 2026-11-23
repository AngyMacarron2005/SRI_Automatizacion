import os
import sys
from pathlib import Path
import time
from playwright.sync_api import sync_playwright
import tkinter as tk
from tkinter import messagebox

def subir_a_odoo():
    root = tk.Tk()
    root.withdraw()
    
    print("[Odoo] Iniciando proceso de subida...")
    
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
    config_file = Path(script_dir) / "path_config.txt"
    
    if not config_file.exists():
        messagebox.showerror("Error Odoo", "No se encontró el archivo de ruta del ZIP (path_config.txt).")
        return
        
    with open(config_file, "r", encoding="utf-8") as f:
        archivo_zip = f.read().strip()
        
    if not os.path.exists(archivo_zip):
        messagebox.showerror("Error Odoo", f"No se encontró el archivo ZIP en la ruta:\n{archivo_zip}")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.new_page()
            page.bring_to_front()
            
            # 1. Ir directamente al tablero de Contabilidad en Odoo
            print("[Odoo] Abriendo módulo de Contabilidad...")
            page.goto(
                "https://finetic.odoosoluciones.com/web#view_type=kanban&model=account.journal&menu_id=150&action=198",
                wait_until="domcontentloaded"
            )
            
            # Buscamos específicamente el menú que está VISIBLE en la barra superior
            menu_comprobantes = page.locator("a.dropdown-toggle:visible:has-text('Comprobantes Electrónicos')").first
            menu_comprobantes.wait_for(state="visible", timeout=20000)
            time.sleep(1)
            
            # 2. Clic en Comprobantes Electrónicos
            print("[Odoo] Abriendo menú Comprobantes Electrónicos...")
            menu_comprobantes.click()
            time.sleep(1)
            
            # 3. Clic en Cargar ZIP Compr Electronicos
            print("[Odoo] Abriendo ventana de carga ZIP...")
            opcion_zip = page.locator("a:visible:has-text('Cargar ZIP')").first
            opcion_zip.wait_for(state="visible", timeout=5000)
            opcion_zip.click()
            
            # Esperamos a que aparezca el input exacto de Odoo en la ventana emergente
            input_odoo = page.locator("input.o_form_input_file[name='ufile']").last
            input_odoo.wait_for(state="attached", timeout=10000)
            time.sleep(1)
            
            # 4. Cargar el archivo ZIP directamente en el input nativo de Odoo
            print(f"[Odoo] Adjuntando archivo ZIP: {archivo_zip}")
            input_odoo.set_input_files(str(archivo_zip))
            
            # Esperamos a que Odoo lea el archivo y actualice el campo de texto en pantalla
            time.sleep(3)
            
            # 5. Clic en el botón Importar de la ventana emergente
            print("[Odoo] Haciendo clic en Importar...")
            btn_importar = page.locator("div.modal-content:visible button:has-text('Importar')").last
            btn_importar.wait_for(state="visible", timeout=5000)
            btn_importar.click()
            
            time.sleep(5)
            messagebox.showinfo("Odoo", "¡El archivo ZIP se ha subido e importado en Odoo con éxito!")
            print("¡Proceso de subida a Odoo finalizado con éxito!")
            
        except Exception as e:
            messagebox.showerror("Error Odoo", f"Ocurrió un error al subir a Odoo:\n{e}")

if __name__ == "__main__":
    subir_a_odoo()
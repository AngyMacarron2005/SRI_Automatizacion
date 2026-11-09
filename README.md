# 🤖 Robot Automatizador de Facturas SRI - Finetic C.L.

Sistema de automatización en Python utilizando **Playwright** y **Tkinter** para la descarga masiva y ordenada de comprobantes electrónicos (XML y RIDE/PDF) desde el portal del SRI en Ecuador.

---

## 📋 Requisitos Previos

Antes de ejecutar el programa en una computadora nueva, asegúrate de tener instalado:
1. **Google Chrome** instalado en su ruta por defecto.
2. **Python** (versión 3.8 o superior).

---

## ⚙️ Guía de Instalación (Paso a Paso)

### 1. Clonar o descargar el repositorio
Abre una terminal en la computadora y sitúate en la carpeta donde deseas tener el proyecto.

### 2. Instalar dependencias necesarias
Ejecuta el siguiente comando en la terminal para instalar las librerías obligatorias de automatización y entorno gráfico:

```bash
pip install playwright

```
Luego, instala los navegadores que utiliza Playwright por debajo ejecutando:

```bash
playwright install
```
(Nota para usuarios de Linux/Ubuntu): Si llegara a faltar el paquete gráfico de ventanas emergentes, instálalo con:

```bash
sudo apt install python3-tk
```
🚀 ¿Cómo Ejecutar el Programa?
Abre tu terminal en la carpeta del proyecto.

Ejecuta el script principal:

```bash
python sri_bot.py
```
Sigue las instrucciones en las ventanas emergentes:

Se abrirá Google Chrome automáticamente.

Inicia sesión en el portal del SRI, ve a Comprobantes electrónicos recibidos, filtra tus fechas y haz clic en Consultar.

Una vez que veas la tabla con las facturas en pantalla, haz clic en OK en la alerta del programa.

Ingresa el nombre con el que deseas guardar el respaldo (ej. octubre).

El robot descargará los XMLs (comprimiéndolos en un .zip dentro de facturas_descargadas/) y los PDFs en una carpeta de respaldo. Al finalizar, se abrirán las carpetas automáticamente y te preguntará si deseas realizar otra consulta.

###  Comando para ejecutar navegador según el equipo:

```bash
print("\n-> Abriendo Google Chrome...")
    
    if platform.system() == "Windows":
        user_dir = os.path.expanduser('~').replace('\\', '/')
        
        # Rutas habituales donde Windows instala Google Chrome
        rutas_chrome = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        
        # Buscar la ruta que realmente exista en el sistema del cliente
        chrome_path = next((ruta for ruta in rutas_chrome if os.path.exists(ruta)), "chrome")
        
        cmd = [
            chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={user_dir}/chrome_sri_profile",
            url_login_sri
        ]
    else:
        cmd = [
            "google-chrome",
            "--remote-debugging-port=9222",
            f"--user-data-dir={os.path.expanduser('~')}/chrome_sri_profile",
            "--ozone-platform=x11",
            url_login_sri
        ]
    
    subprocess.Popen(cmd)
    time.sleep(3)
```

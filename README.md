# SRI_Automatizacion
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

Luego, instala los navegadores que utiliza Playwright por debajo:
playwright install
(Nota para usuarios de Linux/Ubuntu): Si llegara a faltar el paquete gráfico de ventanas emergentes, instálalo con:
sudo apt install python3-tk
🚀 ¿Cómo Ejecutar el Programa?
Abre tu terminal en la carpeta del proyecto.

Ejecuta el script principal:

Bash
python sri_bot.py
Sigue las instrucciones en las ventanas emergentes:

Se abrirá Google Chrome automáticamente.

Inicia sesión en el portal del SRI, ve a Comprobantes electrónicos recibidos, filtra tus fechas y haz clic en Consultar.

Una vez que veas la tabla con las facturas en pantalla, haz clic en OK en la alerta del programa.

Ingresa el nombre con el que deseas guardar el respaldo (ej. octubre).

El robot descargará los XMLs (comprimiéndolos en un .zip dentro de facturas_descargadas/) y los PDFs en una carpeta de respaldo. Al finalizar, se abrirán las carpetas automáticamente y te preguntará si deseas realizar otra consulta.

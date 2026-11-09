#!/bin/bash
# Ir a la carpeta donde está guardado este script
cd "$(dirname "$0")"

# Activar el entorno virtual de Python (si lo usas)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar el robot de Python
python3 sri_bot.py

import sys
import os

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la app principal
from app import app

# Esta función maneja las requests de Vercel
def handler(event, context):
    return app

# Para desarrollo
if __name__ == "__main__":
    app.run()
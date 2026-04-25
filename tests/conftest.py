"""
Configuración global de pytest.
Establece variables de entorno necesarias ANTES de importar main.py.
"""
import os

os.environ.setdefault("API_SECRET", "test-secret-para-tests")

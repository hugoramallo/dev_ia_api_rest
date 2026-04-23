# Tareas API — Proyecto de entrenamiento Clase 2

API REST de gestión de tareas y usuarios.

## Stack

- Python 3.10+
- FastAPI
- SQLite
- pytest + httpx para tests

## Estructura

```
src/
  main.py         # API principal — endpoints, modelos, lógica
tests/
  test_main.py    # suite de tests
```

## Cómo ejecutar

```bash
pip install -r requirements.txt

# Ejecutar la API
uvicorn src.main:app --reload

# Ejecutar tests
pytest tests/ -v
```

## Documentación automática

Con la API corriendo, abre en el navegador:
- http://localhost:8000/docs — interfaz Swagger
- http://localhost:8000/redoc — documentación alternativa

## Contexto de negocio

- Los usuarios pueden ser de tipo `user` o `admin`
- Las tareas tienen prioridad: `normal`, `alta`, `urgente`
- Las passwords deben guardarse hasheadas con SHA-256
- Los endpoints de admin requieren autenticación real
- Nunca devolver passwords en respuestas de la API

## Constraints importantes

- No modificar el schema de la DB
- Mantener compatibilidad con SQLite
- Las firmas de los endpoints son fijas
- No añadir dependencias externas sin justificación

## Problemas conocidos

Ver issues del repo — hay vulnerabilidades de seguridad reales que el Security Scout detectará.

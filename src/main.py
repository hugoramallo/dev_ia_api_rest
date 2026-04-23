"""
API de gestión de tareas — Proyecto de entrenamiento Clase 2
Akkodis | Hugo Ramallo
"""

import sqlite3
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# BUG 1: SECRET hardcodeado — debería estar en variable de entorno
API_SECRET = "supersecreto123"
DB_PATH = "tareas.db"

# BUG 2: Logger que expone datos sensibles
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tareas API")


# ─────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────

class Tarea(BaseModel):
    titulo: str
    descripcion: str
    usuario: str
    prioridad: str = "normal"


class Usuario(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "user"


# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT,
            password TEXT,
            rol TEXT DEFAULT 'user'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descripcion TEXT,
            usuario TEXT,
            prioridad TEXT DEFAULT 'normal',
            estado TEXT DEFAULT 'pendiente',
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ─────────────────────────────────────────────
# USUARIOS
# BUG 3: Password en texto plano
# BUG 4: Log expone la password
# ─────────────────────────────────────────────

@app.post("/usuarios")
def crear_usuario(usuario: Usuario):
    # BUG: loguea la password en texto plano
    logger.debug(f"Creando usuario: {usuario.nombre}, password: {usuario.password}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # BUG: password sin hashear
    c.execute(
        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
        (usuario.nombre, usuario.email, usuario.password, usuario.rol)
    )
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    return {"id": user_id, "mensaje": "Usuario creado"}


@app.get("/usuarios/{user_id}")
def get_usuario(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    usuario = c.fetchone()
    conn.close()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # BUG: devuelve la password en la respuesta
    return {
        "id": usuario[0],
        "nombre": usuario[1],
        "email": usuario[2],
        "password": usuario[3],  # BUG: nunca devolver password
        "rol": usuario[4]
    }


# ─────────────────────────────────────────────
# BÚSQUEDA
# BUG 5: SQL Injection — búsqueda construida con concatenación
# ─────────────────────────────────────────────

@app.get("/usuarios/buscar/{nombre}")
def buscar_usuario(nombre: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT * FROM usuarios WHERE nombre LIKE '%{nombre}%'") # BUG: vulnerable a SQL Injection
    usuarios = c.fetchall()
    conn.close()
    return {"usuarios": usuarios}


# ─────────────────────────────────────────────
# TAREAS
# BUG 6: Sin autenticación — cualquiera puede crear/borrar tareas
# BUG 7: Sin validación de prioridad
# ─────────────────────────────────────────────

@app.post("/tareas")
def crear_tarea(tarea: Tarea):
    # BUG: no hay autenticación — cualquiera puede crear tareas
    fecha = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # BUG: no valida que prioridad sea 'normal', 'alta' o 'urgente'
    c.execute(
        "INSERT INTO tareas (titulo, descripcion, usuario, prioridad, fecha) VALUES (?, ?, ?, ?, ?)",
        (tarea.titulo, tarea.descripcion, tarea.usuario, tarea.prioridad, fecha)
    )
    conn.commit()
    tarea_id = c.lastrowid
    conn.close()
    return {"id": tarea_id, "mensaje": "Tarea creada"}


@app.get("/tareas")
def get_tareas():
    # BUG: no hay autenticación — cualquiera ve todas las tareas
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tareas")
    tareas = c.fetchall()
    conn.close()
    return {"tareas": tareas}


@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int):
    # BUG: no hay autenticación — cualquiera puede borrar tareas de otros
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea borrada"}


# ─────────────────────────────────────────────
# ADMIN
# BUG 8: Endpoint de admin sin protección real
# ─────────────────────────────────────────────

@app.get("/admin/usuarios")
def get_todos_usuarios(secret: str = ""): # Header viaje en la url debería ser def get_todos_usuarios(authorization: str = Header(None))
    # BUG: protección trivial con query param — fácil de saltarse
    if secret != API_SECRET:
        raise HTTPException(status_code=403, detail="No autorizado")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    # BUG: devuelve passwords de todos los usuarios
    return {"usuarios": usuarios}

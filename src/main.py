"""
API de gestión de tareas — Proyecto de entrenamiento Clase 2
Akkodis | Hugo Ramallo
"""

import os
import hashlib
import sqlite3
import logging
from datetime import datetime
from typing import Literal
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

# FIX 1: SECRET leído desde variable de entorno
API_SECRET = os.environ.get("API_SECRET")
if not API_SECRET:
    raise RuntimeError("La variable de entorno API_SECRET no está definida")
DB_PATH = "tareas.db"

# BUG 2: Logger que expone datos sensibles
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tareas API")


def verificar_auth(authorization: str = Header(None)):
    """Dependencia reutilizable que valida el header Authorization."""
    if authorization != API_SECRET:
        raise HTTPException(status_code=401, detail="No autorizado")


# ─────────────────────────────────────────────
# MODELOS
# ─────────────────────────────────────────────

class Tarea(BaseModel):
    titulo: str
    descripcion: str
    usuario: str
    prioridad: Literal["normal", "alta", "urgente"] = "normal"


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
    # FIX 2: log sin exponer password
    logger.debug(f"Creando usuario: {usuario.nombre}")

    # FIX 3: password hasheada con SHA-256
    hashed_pw = hashlib.sha256(usuario.password.encode()).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
        (usuario.nombre, usuario.email, hashed_pw, usuario.rol)
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
    # FIX 4: nunca devolver la password
    return {
        "id": usuario[0],
        "nombre": usuario[1],
        "email": usuario[2],
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
    # FIX 5: query parametrizada — no más SQL Injection
    c.execute("SELECT * FROM usuarios WHERE nombre LIKE ?", (f"%{nombre}%",))
    usuarios = c.fetchall()
    conn.close()
    return {"usuarios": usuarios}


# ─────────────────────────────────────────────
# TAREAS
# FIX 6: Autenticación requerida en todos los endpoints de tareas
# ─────────────────────────────────────────────

@app.post("/tareas")
def crear_tarea(tarea: Tarea, authorization: str = Header(None)):
    verificar_auth(authorization)
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
def get_tareas(authorization: str = Header(None)):
    verificar_auth(authorization)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tareas")
    tareas = c.fetchall()
    conn.close()
    return {"tareas": tareas}


@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int, authorization: str = Header(None)):
    verificar_auth(authorization)
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
def get_todos_usuarios(authorization: str = Header(None)):
    # FIX 7: secret en Header, no en query param; nunca exponer passwords
    if authorization != API_SECRET:
        raise HTTPException(status_code=403, detail="No autorizado")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nombre, email, rol FROM usuarios")
    rows = c.fetchall()
    conn.close()
    usuarios = [{"id": r[0], "nombre": r[1], "email": r[2], "rol": r[3]} for r in rows]
    return {"usuarios": usuarios}

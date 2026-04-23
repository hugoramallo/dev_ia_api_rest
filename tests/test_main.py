"""
Tests de la API de tareas.
Algunos pasan, otros fallan — igual que ayer.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from main import app, init_db, DB_PATH

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    db = str(tmp_path / "test.db")
    monkeypatch.setattr("main.DB_PATH", db)
    init_db()
    yield
    if os.path.exists(db):
        os.remove(db)


# ─────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────

def test_crear_usuario_basico():
    r = client.post("/usuarios", json={
        "nombre": "Hugo", "email": "hugo@test.com",
        "password": "1234", "rol": "user"
    })
    assert r.status_code == 200


def test_password_no_se_devuelve_en_respuesta():
    # FALLA — get_usuario devuelve la password
    client.post("/usuarios", json={
        "nombre": "Hugo", "email": "hugo@test.com",
        "password": "secreto123", "rol": "user"
    })
    r = client.get("/usuarios/1")
    assert "password" not in r.json(), "La password no debería devolverse nunca"


def test_password_no_se_guarda_en_plano():
    # FALLA — password sin hashear
    client.post("/usuarios", json={
        "nombre": "Hugo", "email": "hugo@test.com",
        "password": "secreto123", "rol": "user"
    })
    r = client.get("/usuarios/1")
    data = r.json()
    if "password" in data:
        assert data["password"] != "secreto123", "Password no debería guardarse en plano"


def test_busqueda_no_vulnerable_sql_injection():
    # FALLA — SQL injection en buscar_usuario
    r = client.get("/usuarios/buscar/' OR '1'='1")
    assert r.status_code != 500, "SQL injection no debería romper la API"
    assert len(r.json().get("usuarios", [])) == 0, "SQL injection no debería devolver datos"


# ─────────────────────────────────────────────
# TAREAS
# ─────────────────────────────────────────────

def test_crear_tarea_basico():
    r = client.post("/tareas", json={
        "titulo": "Revisar PR",
        "descripcion": "Revisar el PR de Hugo",
        "usuario": "ana",
        "prioridad": "normal"
    })
    assert r.status_code == 200


def test_prioridad_invalida_rechazada():
    # FALLA — no hay validación de prioridad
    r = client.post("/tareas", json={
        "titulo": "Test",
        "descripcion": "Test",
        "usuario": "hugo",
        "prioridad": "MEGA_URGENTE_AHORA"
    })
    assert r.status_code == 422, "Prioridad inválida debería rechazarse"


def test_borrar_tarea_requiere_autenticacion():
    # FALLA — no hay autenticación
    client.post("/tareas", json={
        "titulo": "Tarea importante",
        "descripcion": "No me borres",
        "usuario": "hugo"
    })
    r = client.delete("/tareas/1")
    assert r.status_code == 401, "Borrar tarea debería requerir autenticación"


# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────

def test_admin_sin_secret_bloqueado():
    r = client.get("/admin/usuarios")
    assert r.status_code == 403


def test_admin_secret_en_url_es_inseguro():
    # FALLA — el secret viaja en la URL
    r = client.get("/admin/usuarios?secret=supersecreto123")
    assert r.status_code == 403, "El secret en URL es inseguro y no debería funcionar"

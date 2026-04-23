# Documentación de endpoints — Tareas API

---

### `POST /usuarios`

Crea un nuevo usuario en el sistema.

**Body (JSON)**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombre` | `string` | ✓ | Nombre del usuario |
| `email` | `string` | ✓ | Correo electrónico |
| `password` | `string` | ✓ | Contraseña |
| `rol` | `string` | — | Rol del usuario. Default: `"user"` |

**Respuesta 200**
```json
{ "id": 1, "mensaje": "Usuario creado" }
```

---

### `GET /usuarios/{user_id}`

Recupera los datos de un usuario por su ID.

**Path params**

| Param | Tipo | Descripción |
|---|---|---|
| `user_id` | `int` | ID del usuario |

**Respuesta 200**
```json
{
  "id": 1,
  "nombre": "Hugo",
  "email": "hugo@test.com",
  "password": "secreto123",
  "rol": "user"
}
```

**Errores**

| Código | Motivo |
|---|---|
| `404` | Usuario no encontrado |

---

### `GET /usuarios/buscar/{nombre}`

Busca usuarios cuyo nombre contenga la cadena indicada (búsqueda parcial, case-sensitive según la colación de SQLite).

**Path params**

| Param | Tipo | Descripción |
|---|---|---|
| `nombre` | `string` | Fragmento del nombre a buscar |

**Respuesta 200**
```json
{
  "usuarios": [
    [1, "Hugo Ramallo", "hugo@test.com", "hash", "user"]
  ]
}
```

> Devuelve una lista de tuplas con todos los campos de la tabla `usuarios`.

---

### `POST /tareas`

Crea una nueva tarea.

**Body (JSON)**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `titulo` | `string` | ✓ | Título de la tarea |
| `descripcion` | `string` | ✓ | Descripción detallada |
| `usuario` | `string` | ✓ | Nombre del usuario asignado |
| `prioridad` | `string` | — | Prioridad. Default: `"normal"` |

**Respuesta 200**
```json
{ "id": 3, "mensaje": "Tarea creada" }
```

---

### `GET /tareas`

Devuelve todas las tareas almacenadas en el sistema.

**Sin parámetros.**

**Respuesta 200**
```json
{
  "tareas": [
    [1, "Revisar PR", "Revisar el PR de Hugo", "ana", "normal", "pendiente", "2026-04-23T10:00:00"]
  ]
}
```

> Devuelve una lista de tuplas con todos los campos de la tabla `tareas`: `id`, `titulo`, `descripcion`, `usuario`, `prioridad`, `estado`, `fecha`.

---

### `DELETE /tareas/{tarea_id}`

Elimina una tarea por su ID.

**Path params**

| Param | Tipo | Descripción |
|---|---|---|
| `tarea_id` | `int` | ID de la tarea a eliminar |

**Respuesta 200**
```json
{ "mensaje": "Tarea borrada" }
```

> No devuelve error si el ID no existe — la operación se completa silenciosamente.

---

### `GET /admin/usuarios`

Devuelve todos los usuarios del sistema. Requiere el secreto de administrador.

**Query params**

| Param | Tipo | Requerido | Descripción |
|---|---|---|---|
| `secret` | `string` | ✓ | Secreto de administrador |

**Respuesta 200**
```json
{
  "usuarios": [
    [1, "Hugo", "hugo@test.com", "secreto123", "user"]
  ]
}
```

**Errores**

| Código | Motivo |
|---|---|
| `403` | Secreto ausente o incorrecto |

---

> **Nota:** Varios endpoints presentan vulnerabilidades de seguridad activas (contraseñas en texto plano, ausencia de autenticación, exposición de credenciales en respuestas). Ver informe de auditoría para el detalle completo.

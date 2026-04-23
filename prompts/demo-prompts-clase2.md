# Prompts Clase 2 — Agentes, Skills y Hooks
# Instructor: Hugo Ramallo | Akkodis

---

## BLOQUE 1 — Security Scout (agente personalizado)

### Activar el agente
En Copilot Chat → selector de agentes (abajo a la derecha) → Security Scout

### Prompt 1: Auditoría completa
```
Audita el código de esta API y dame un informe completo de vulnerabilidades ordenadas por prioridad.
```

### Prompt 2: Auditoría específica
```
Revisa solo los endpoints que manejan passwords y dime qué riesgos tienen.
```

### Prompt 3: Multi-agente — pasar el informe al agente de arreglo
```
Tienes el informe del Security Scout. Ahora actúa como un desarrollador senior y dime en qué orden arreglarías estos problemas y por qué.
```

---

## BLOQUE 2 — Skill fix-bug-completo

### Prompt 4: Usar la skill
```
Usa la skill fix-bug-completo para arreglar el problema de SQL injection en buscar_usuario().
```

### Prompt 5: Verificar el proceso
```
¿Seguiste todos los pasos de la skill? ¿Generaste el test y el mensaje de commit?
```

### Prompt 6: Arreglar con constraints
```
Usa la skill fix-bug-completo para que get_usuario() no devuelva la password en la respuesta.
Constraint: no cambies la firma del endpoint ni el schema de la DB.
```

---

## BLOQUE 3 — Hooks

### Ver el hook en acción (Copilot CLI)
```bash
# Intenta hacer push — el hook lo bloquea
copilot -p "Haz git push de los cambios al repo remoto" -s
```

### Ver el log de auditoría
```bash
cat .github/hooks/logs/audit.log
```

### Prompt 7: Pedir al agente que proponga un hook nuevo
```
Propón un hook preToolUse que bloquee cualquier cambio en main.py 
si no existe al menos un test nuevo o modificado en la misma sesión.
Escribe el script bash completo.
```

---

## CIERRE

### Prompt 8: Reflexión final
```
Dado lo que hemos visto hoy — Security Scout, skill de fix completo y hooks — 
dame un ejemplo concreto de cómo aplicarías cada uno en tu proyecto actual.
```

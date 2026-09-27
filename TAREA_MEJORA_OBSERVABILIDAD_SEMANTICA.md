# 📋 Tarea de Mejora: Observabilidad Semántica Contextual con Micro-LLM

**Proyecto:** JARVIS - Real-Time Voice Telemetry & Dynamic Audio Ducking  
**Módulo:** Motor de Inferencia y Telemetría Semántica (`jarvis_voice.py`)  
**Estatus:** Propuesta de Innovación / En Diseño  
**Enfoque de Competencia:** InnovaFest Morelos (Noviembre) & Portafolio de Ingeniería de Agentes  

---

## 🎯 1. Planteamiento del Problema: "Ceguera Operativa" en Agentes Autónomos

Los entornos actuales de desarrollo con agentes (Cursor, Windsurf, Copilot, Antigravity) sufren de una brecha crítica:
1. **Pérdida de Observabilidad en Tiempo Real:** Cuando el modelo entra en inferencia pesada, el desarrollador queda ciego frente a un spinner de carga. Dado que el agente tiene permisos autónomos en consola, sistema de archivos y Git, el usuario no sabe si el modelo está leyendo, sobreescribiendo código crítico o trabado en un ciclo infinito.
2. **Jerga Técnica e Idiomática Ineficiente:** Las herramientas actuales muestran logs crudos en inglés (`"Running pytest..."`, `"Viewing sample row..."`). Para un desarrollador mexicano o hispanohablante, esto no comunica el *propósito de negocio* ni el impacto directo en el proyecto.

---

## 💡 2. La Innovación Propuesta: Micro-Evaluador Contextual Híbrido

En lugar de limitarse a una traducción estática por expresiones regulares (regex), se propone integrar un **Micro-Evaluador Contextual asistido por LLM ultraligero**:

### Flujo de Datos:
1. **Entradas:**
   * **Objetivo Actual (`USER_INPUT`):** La última instrucción dada por el desarrollador (ej. *"Estiliza la tabla de inventario para que tenga filtros automáticos"*).
   * **Acción Técnica (`tool_call`):** La herramienta que el agente activó (ej. `run_command: python estilizar_inventario.py`).
2. **Procesamiento de Inferencia Ultrarrápida (< 300 ms):**
   * Un modelo ultra-rápido (ej. Gemini 2.5 Flash / Groq Llama-3) sintetiza en **máximo 10 palabras** en español mexicano natural el *por qué* de la acción.
3. **Salida Auditiva (Edge-TTS + Ducking):**
   * Convierte la acción mecánica en comprensión humana de propósito:
     * *Antes (Mecánico):* `"Ejecutando la instrucción python estilizar_inventario.py"`
     * *Ahora (Semántico):* `"Señor Luis, voy a aplicar los formatos y filtros al catálogo de refacciones."`

---

## 🛡️ 3. Arquitectura Híbrida Tolerante a Fallos (Latencia Cero)

Para mantener la respuesta inmediata característica de JARVIS:

```text
       [ Evento de Tool Call detectado ]
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Consulta Micro-LLM ]      [ Temporizador 350ms ]
       │                               │
       ├──── ¿Respondió en <350ms? ────┤
       │                               │
     (SÍ)                             (NO / Error de red)
       │                               │
       ▼                               ▼
[ Frase Semántica Contextual ]  [ Fallback Heurístico Local ]
       │                               │
       └───────────────┬───────────────┘
                       ▼
         [ Síntesis de Voz Edge-TTS ]
                       ▼
           [ Audio Ducking Pygame ]
```

* **Garantía:** Si hay latencia alta o falla de internet, el sistema nunca se bloquea; salta de inmediato al diccionario heurístico local ya integrado en `jarvis_voice.py`.

---

## 🏆 4. Valor para InnovaFest Morelos (Noviembre)

| Criterio | Justificación Técnica |
| :--- | :--- |
| **Innovación en HCI (Interacción Humano-Computadora):** | Transforma la supervisión pasiva de agentes autónomos en un canal de auditoría sensorial continuo. |
| **Seguridad y Human-in-the-Loop:** | Devuelve el control al desarrollador al advertir en tiempo real qué archivos o comandos se van a alterar antes de su ejecución definitiva. |
| **Localización Cultural:** | Rompe la barrera del inglés técnico crudo con síntesis en español coloquial orientada a la ingeniería latinoamericana. |

---

## 📝 5. Tareas Técnicas para la Implementación (Checklist)

- [ ] **Módulo de Contexto:** Crear función en `jarvis_voice.py` para extraer la última meta activa del usuario desde el historial de sesión.
- [ ] **Conector API Asíncrono:** Diseñar función `evaluar_intencion_contextual(prompt_usuario, tool_call, timeout=0.35)`.
- [ ] **Prompt Engineering Estricto:** Definir prompt de sistema con restricción de tokens (`max_tokens: 25`, respuesta en primera persona, tono formal-coloquial *"Señor Luis..."*).
- [ ] **Control de Fallback:** Integración transparente con `narrar_accion_coloquial()` como respaldo determinista.
- [ ] **Pruebas de Latencia:** Benchmark comparativo (tiempo con fallback vs tiempo con micro-inferencia).

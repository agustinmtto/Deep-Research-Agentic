# 🔍 Deep Research Agentic

Sistema de **investigación profunda multi-agente** construido como mejora del proyecto original del **Curso Completo de Ingeniería de Agentes de IA**.

En lugar de un pipeline rígido (planner → search → write → email), este sistema usa un **agente orquestador agentic** que decide dinámicamente qué herramientas llamar, en qué orden y cuántas veces iterar.

---

## ✨ Qué mejora vs. el original

| Aspecto | Original | Esta versión |
|---|---|---|
| **Clarificación** | Ninguna (consulta cruda) | Agente clarificador genera 3 preguntas antes de investigar |
| **Orquestación** | Pipeline fijo en Python (`ResearchManager`) | Agente orquestador (LLM decide el flujo) |
| **Tools** | `Runner.run()` directo entre agentes | Agentes envueltos como `@function_tool` (agents-as-tools) |
| **Paralelismo** | Manual con `asyncio.gather` | El LLM emite múltiples tool calls en paralelo en un turno |
| **Iteración** | No (3 búsquedas fijas) | El orquestador puede evaluar evidencia y replanificar |
| **Trazabilidad** | `trace()` global | `trace()` + link visible en la UI |

---

## 🏗️ Arquitectura

```
deep_research.py          ← UI Gradio (entrada/salida)
   │
   ├─→ clarifying_agent.py        ← genera 3 preguntas (gpt-4o-mini)
   │
   └─→ orchestrator_agent.py      ← agente meta (gpt-4o)
         │
         └─→ tools.py             ← 4 tools (gpt-4o-mini c/u)
               ├─→ plan_searches       ─→ planner_agent.py
               ├─→ perform_search      ─→ search_agent.py
               ├─→ write_report        ─→ writer_agent.py
               └─→ send_email_tool     ─→ email_agent.py
```

### Flujo agentic

1. **Usuario ingresa tema** → `clarifying_agent` genera 3 preguntas para acotar la búsqueda.
2. **Usuario responde** → el sistema combina tema + respuestas en un único input estructurado.
3. **`orchestrator_agent` decide**:
   - Llama a `plan_searches` → obtiene 3 términos.
   - Llama a `perform_search` × 3 **en paralelo** (en un solo turno).
   - Evalúa resultados.
   - Llama a `write_report` → recibe markdown.
   - Llama a `send_email_tool` → envía el informe.
4. **UI muestra** el markdown del informe.

---

## 🧰 Tech stack

- **[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)** — orquestación multi-agente.
- **[Gradio](https://gradio.app/)** — UI web con flujo de 2 pasos (preguntas → informe).
- **[SendGrid](https://sendgrid.com/)** — envío del informe por email.
- **[uv](https://docs.astral.sh/uv/)** — gestión de dependencias y venv.
- **Python 3.12**

Modelos usados:
- `gpt-4o` → orquestador (razonamiento).
- `gpt-4o-mini` → agentes especialistas (tareas simples).

---

## 🚀 Instalación

```bash
# 1. Instalar uv (si no lo tenés)
#    Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clonar el repo y crear venv
git clone <repo-url>
cd deep_research
uv venv
uv pip install gradio openai-agents python-dotenv sendgrid

# 3. Activar venv
#    Windows:
.venv\Scripts\Activate.ps1
#    Linux/Mac:
source .venv/bin/activate
```

---

## ⚙️ Configuración

Crear un archivo `.env` en la raíz:

```env
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG....
```

Y editar los emails en `email_agent.py:12-13` (remitente y destinatario).

---

## ▶️ Uso

```bash
python deep_research.py
```

Se abre la UI en el navegador. Flujo:

1. Ingresá un tema (ej: *"cambio climático en Argentina"*).
2. Respondé las 3 preguntas clarificadoras generadas automáticamente.
3. Esperá ~1-2 minutos mientras el orquestador investiga.
4. Leé el informe generado (y revisalo en tu email).

Cada ejecución genera una **trace** en [OpenAI Traces](https://platform.openai.com/traces/) para inspeccionar todas las tool calls.

---

## 📂 Estructura del proyecto

```
deep_research.py         # UI Gradio
clarifying_agent.py      # Agente que genera preguntas
orchestrator_agent.py    # Agente meta que orquesta
tools.py                 # Wrappers @function_tool
planner_agent.py         # (sin cambios) planificador
search_agent.py          # (sin cambios) buscador web
writer_agent.py          # (sin cambios) redactor
email_agent.py           # (sin cambios) emisor de email
.env                     # API keys (no commitear)
```

---

## 🎓 Origen

Este proyecto es una **evolución del proyecto final de la semana 2** del **Curso Completo de Ingeniería de Agentes de IA** (original de Ed Donner). El código original usaba un orquestador imperativo en Python con `asyncio.gather`. Esta versión lo reemplaza por un **patrón agentic puro**: el LLM es quien decide el flujo, no el código.

Conceptos aplicados del curso:
- Multi-agent systems
- Tools & function calling
- Structured outputs (Pydantic)
- Tracing & observability
- Handoffs (considerados, no aplicados, se utilizaron agents-as-tools)

---

## 📜 Licencia

MIT

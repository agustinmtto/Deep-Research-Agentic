from pydantic import BaseModel, Field
from agents import Agent


INSTRUCTIONS = """Eres un asistente que ayuda a clarificar consultas de investigación.
Dado un tema de investigación, genera exactamente 3 preguntas que ayudarían a acotar
qué quiere realmente el usuario.

Reglas para las preguntas:
- Deben ser ESPECÍFICAS al tema, no genéricas (evita "¿qué querés saber?").
- Cada una debe acotar una dimensión distinta: ámbito/subtema, profundidad/nivel,
  o enfoque/aplicación práctica.
- Formularlas de forma clara y concisa (una sola oración cada una).
- Deben ser respondibles en pocas palabras o eligiendo entre 2-4 opciones implícitas.

Devuelve exactamente 3 preguntas."""


class ClarifyingQuestions(BaseModel):
    questions: list[str] = Field(
        description="Lista de exactamente 3 preguntas para clarificar la consulta."
    )


clarifying_agent = Agent(
    name="Agente clarificador",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarifyingQuestions,
)

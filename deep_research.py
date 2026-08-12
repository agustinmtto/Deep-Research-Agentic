import gradio as gr
from dotenv import load_dotenv
from agents import Runner, trace, gen_trace_id
from clarifying_agent import clarifying_agent, ClarifyingQuestions
from orchestrator_agent import orchestrator_agent

load_dotenv(override=True)


def empty_state():
    return {"topic": "", "questions": [], "answers": ["", "", ""]}


async def generate_questions(topic: str):
    """Llama al agente clarificador y muestra las 3 preguntas generadas."""
    if not topic.strip():
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value="", label="Pregunta 1"),
            gr.update(value="", label="Pregunta 2"),
            gr.update(value="", label="Pregunta 3"),
            "Por favor ingresá un tema para investigar.",
            empty_state(),
        )

    result = await Runner.run(clarifying_agent, topic)
    questions = result.final_output_as(ClarifyingQuestions).questions

    return (
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(label=questions[0], value=""),
        gr.update(label=questions[1], value=""),
        gr.update(label=questions[2], value=""),
        f"**Tema:** {topic}\n\nRespondé las 3 preguntas para acotar la búsqueda.",
        {"topic": topic, "questions": questions, "answers": ["", "", ""]},
    )


async def start_research(state: dict, a1: str, a2: str, a3: str):
    """Lanza la investigación agentic combinando tema + respuestas del usuario."""
    answers = [a1, a2, a3]
    qa_block = "\n".join(
        f"- {q}: {a or '(sin respuesta)'}"
        for q, a in zip(state["questions"], answers)
    )
    combined_input = (
        f"Consulta original: {state['topic']}\n\n"
        f"Contexto del usuario (respuestas a preguntas clarificadoras):\n{qa_block}"
    )

    trace_id = gen_trace_id()
    with trace("Investigación profunda", trace_id=trace_id):
        yield (
            f"**Investigando...** esto puede tardar unos minutos.\n\n"
            f"Trazabilidad: https://platform.openai.com/traces/trace?trace_id={trace_id}"
        )
        result = await Runner.run(orchestrator_agent, combined_input)
        yield result.final_output


with gr.Blocks() as ui:
    gr.Markdown("# Búsqueda Profunda")

    topic_textbox = gr.Textbox(label="¿Sobre qué tema te gustaría investigar?")
    generate_btn = gr.Button("Generar preguntas", variant="primary")

    status_md = gr.Markdown()

    with gr.Group(visible=False) as questions_group:
        q1 = gr.Textbox(label="Pregunta 1", lines=2, placeholder="Tu respuesta...")
        q2 = gr.Textbox(label="Pregunta 2", lines=2, placeholder="Tu respuesta...")
        q3 = gr.Textbox(label="Pregunta 3", lines=2, placeholder="Tu respuesta...")

    research_btn = gr.Button("Iniciar investigación", variant="primary", visible=False)

    report = gr.Markdown(label="Informe")

    state = gr.State(empty_state())

    generate_btn.click(
        fn=generate_questions,
        inputs=[topic_textbox],
        outputs=[questions_group, research_btn, q1, q2, q3, status_md, state],
    )

    research_btn.click(
        fn=start_research,
        inputs=[state, q1, q2, q3],
        outputs=[report],
    )

ui.launch(inbrowser=True, theme=gr.themes.Default(primary_hue="sky"))

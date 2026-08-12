from agents import Runner, function_tool

from planner_agent import planner_agent, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from email_agent import email_agent


@function_tool
async def plan_searches(query: str) -> str:
    """Genera un plan de búsquedas web para responder una consulta de investigación.

    Devuelve una lista de búsquedas sugeridas, una por línea, en el formato:
    "<término de búsqueda> -> <razón por la que es importante>"
    """
    result = await Runner.run(planner_agent, f"Consulta: {query}")
    plan = result.final_output_as(WebSearchPlan)
    return "\n".join(
        f"- {item.query} -> {item.reason}" for item in plan.searches
    )


@function_tool
async def perform_search(query: str, reason: str) -> str:
    """Realiza una búsqueda web con el término indicado y devuelve un resumen conciso.

    Args:
        query: el término exacto a buscar en la web.
        reason: por qué esta búsqueda es relevante para la consulta original
                (ayuda al buscador a enfocar el resumen).
    """
    try:
        result = await Runner.run(
            search_agent,
            f"Término de búsqueda: {query}\nRazón para buscar: {reason}",
        )
        return str(result.final_output)
    except Exception as e:
        return f"Sin resultados para '{query}': {e}"


@function_tool
async def write_report(query: str, search_results: str) -> str:
    """Escribe el informe final de investigación en formato markdown.

    Args:
        query: la consulta original del usuario.
        search_results: resultados de búsqueda concatenados, separados por líneas.
    """
    input_text = (
        f"Consulta original: {query}\n"
        f"Resultados de búsqueda resumidos:\n{search_results}"
    )
    result = await Runner.run(writer_agent, input_text)
    report = result.final_output_as(ReportData)
    return report.markdown_report


@function_tool
async def send_email_tool(report_markdown: str) -> str:
    """Envía el informe final por correo electrónico al destinatario configurado.

    Args:
        report_markdown: el informe en markdown que será convertido a HTML y enviado.
    """
    await Runner.run(email_agent, report_markdown)
    return "Correo enviado exitosamente"

import mapa
import integridade as integridade_service
import dashboard as dashboard_service
from datetime import datetime


def format_created_em(value):
    text = str(value).strip()
    if not text:
        return text

    if text.isdigit():
        try:
            number = int(text)
            if number > 10**12:
                number /= 1000
            return datetime.fromtimestamp(number).strftime("%Y-%m-%d")
        except Exception:
            return text

    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return text.split()[0]


def format_cell(value):
    text = str(value).strip()
    if not text:
        return text

    try:
        number = float(text.replace(",", "."))
        return f"{number:.4f}"
    except Exception:
        return value

def render_table(dados):
    if not dados:
        return "<p>Sem dados</p>"
    html = "<table border='1' cellpadding='2' cellspacing='0'><tr>"
    for h in dados[0]:
        html += f"<th>{h}</th>"
    html += "</tr>"
    criado_em_idx = next((i for i, h in enumerate(dados[0]) if str(h).strip().lower() == "criadoem"), None)
    for row in dados[1:]:
        cells = []
        for i, cell in enumerate(row):
            if criado_em_idx is not None and i == criado_em_idx:
                cell = format_created_em(cell)
            else:
                cell = format_cell(cell)
            cells.append(f"<td>{cell}</td>")
        html += "<tr>" + "".join(cells) + "</tr>"
    html += "</table>"
    return html

def oficinas(dados, categorias=None):
    return render_table(dados) + "<p> </p>" + mapa.mapa(dados, categorias)

def utilizadores(dados):
    return render_table(dados)

def categoriasOficinas(dados):
    return render_table(dados)

def compras(dados):
    return render_table(dados)

def integridade(dados):
    return integridade_service.relatorio_html(dados)

def dashboard(dados):
    return dashboard_service.dashboard_html(dados)

def generic_table(dados):
    if isinstance(dados, dict):
        return dashboard(dados)
    return render_table(dados)

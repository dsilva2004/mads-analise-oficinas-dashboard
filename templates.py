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


def normalize_header(value):
    return str(value).strip().lower()


def format_coordinate(value):
    text = str(value).strip()
    if not text:
        return text

    try:
        number = float(text.replace(",", "."))
        return f"{number:.4f}"
    except Exception:
        return value


def format_cell(value):
    return value

def render_table(dados):
    if not dados:
        return '<div class="no-data">Sem dados</div>'
    html = '<div class="table-wrapper"><table><thead><tr>'
    for h in dados[0]:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    criado_em_idx = next((i for i, h in enumerate(dados[0]) if str(h).strip().lower() == "criadoem"), None)
    coord_columns = {
        i
        for i, h in enumerate(dados[0])
        if normalize_header(h) in {"latitude", "lat", "longitude", "lon"}
    }
    for row in dados[1:]:
        cells = []
        for i, cell in enumerate(row):
            if criado_em_idx is not None and i == criado_em_idx:
                cell = format_created_em(cell)
            elif i in coord_columns:
                cell = format_coordinate(cell)
            else:
                cell = format_cell(cell)
            cells.append(f"<td>{cell}</td>")
        html += "<tr>" + "".join(cells) + "</tr>"
    html += "</tbody></table></div>"
    return html

def oficinas(dados, categorias=None):
    tabela_html = render_table(dados)
    mapa_html = mapa.mapa(dados, categorias)
    mapa_section = f'<div class="map-section"><div class="map-title">Localização Geográfica das Oficinas</div><div class="map-container">{mapa_html}</div></div>'
    return tabela_html + mapa_section

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

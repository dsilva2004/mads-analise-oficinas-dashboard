import mapa
import integridade as integridade_service
import dashboard as dashboard_service

def render_table(dados):
    if not dados:
        return "<p>Sem dados</p>"
    html = "<table border='1' cellpadding='2' cellspacing='0'><tr>"
    for h in dados[0]:
        html += f"<th>{h}</th>"
    html += "</tr>"
    for row in dados[1:]:
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
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

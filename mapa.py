from statistics import mean
import html

import folium
from folium import Element


# Normaliza texto para comparações consistentes (headers, categorias, etc.).
def norm(s):
    return str(s or "").strip().lower()


# Converte valores numéricos aceitando vírgula decimal; se falhar, devolve None.
def num(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None


# Procura o índice de uma coluna aceitando vários nomes possíveis.
def findeIndex(headers, *names):
    hmap = { norm(h): i for i, h in enumerate(headers) }
    for n in names:
        i = hmap.get(norm(n))
        if i is not None:
            return i
    return None


# Resolve a cor de uma categoria: tabela de categorias primeiro, fallback depois.
def color(cat, cat_map=None):
    if cat_map:
        return cat_map.get(norm(cat), "red")
    return {
        "artes": "red",
        "desporto": "blue",
        "culinaria": "green",
        "tecnologia": "purple",
        "musica": "orange",
        "idiomas": "cadetblue",
    }.get(norm(cat), "red")


def build_cat_map(categorias):
    if not categorias or len(categorias) < 2:
        return None
    h = categorias[0]
    icat = findeIndex(h, "categoria", "Categoria", "nome", "Nome")
    icor = findeIndex(h, "cor", "Cor", "color")
    if icat is None or icor is None:
        return None
    return {
        norm(r[icat]): str(r[icor]).strip()
        for r in categorias[1:]
        if icat < len(r) and icor < len(r) and str(r[icat]).strip()
    }


def legend_marker_html(cor):
    return (
        f"<span style='display:inline-flex; align-items:center; justify-content:center; "
        f"width:16px; height:16px; margin-right:5px; vertical-align:middle;'>"
        f"<svg width='16' height='16' viewBox='0 0 24 24' aria-hidden='true' focusable='false'>"
        f"<path fill='{html.escape(str(cor))}' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5"
        f"c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z'/></svg>"
        f"</span>"
    )


def mapa(dados, categorias=None, height=550):
    # Validação mínima dos dados de oficinas.
    if not dados or len(dados) < 2:
        return "<p>Sem dados de oficinas para mostrar no mapa.</p>"

    # Identificar colunas relevantes da tabela de oficinas.
    headers = dados[0]
    i_nome = findeIndex(headers, "Nome", "nome", "oficina")
    i_morada = findeIndex(headers, "Morada", "morada", "Endereço", "Endereco", "endereco")
    i_cat = findeIndex(headers, "Categoria", "categoria")
    i_horario = findeIndex(headers, "Horario", "horario", "Horário", "hórario")
    i_lon = findeIndex(headers, "Longitude", "longitude", "Lon")
    i_lat = findeIndex(headers, "Latitude", "latitude", "Lat")
    if i_lon is None or i_lat is None:
        return "<p>Os dados das oficinas não têm longitude/latitude.</p>"

    # Extrair e validar pontos geográficos.
    pontos = []
    for row in dados[1:]:
        lat = num(row[i_lat]) if i_lat < len(row) else None
        lon = num(row[i_lon]) if i_lon < len(row) else None
        if lat is None or lon is None:
            continue
        nome = row[i_nome] if i_nome is not None and i_nome < len(row) else "Oficina"
        morada = row[i_morada] if i_morada is not None and i_morada < len(row) else ""
        categoria = row[i_cat] if i_cat is not None and i_cat < len(row) else ""
        horario = row[i_horario] if i_horario is not None and i_horario < len(row) else ""
        pontos.append((nome, morada, categoria, horario, lat, lon))

    if not pontos:
        return "<p>Não foi possível gerar o mapa com os dados atuais.</p>"

    # Centro médio dos pontos para inicializar o mapa.
    centro = [mean(p[4] for p in pontos), mean(p[5] for p in pontos)]
    m = folium.Map(location=[41.22, -8.5795], zoom_start=12, width="100%", height=height)

    # Construir mapa categoria->cor a partir da tabela categoriasOficinas (se existir).
    cat_map = build_cat_map(categorias)

    # Adicionar marcadores: CircleMarker para cores hex, Marker para cores nomeadas.
    for nome, morada, categoria, horario, lat, lon in pontos:
        cor = color(categoria, cat_map)
        popup_html = (
            f"<b>{html.escape(str(nome))}</b><br>"
            f"Morada: {html.escape(str(morada or '—'))}<br>"
            f"Categoria: {html.escape(str(categoria or '—'))}<br>"
            f"Horário: {html.escape(str(horario or '—'))}"
        )
        if isinstance(cor, str) and cor.startswith("#"):
            folium.CircleMarker([lat, lon], radius=6, color=cor, fill=True, fillcolor=cor, popup=folium.Popup(popup_html, max_width=300), tooltip=nome).add_to(m)
        else:
            folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=300), tooltip=nome, icon=folium.Icon(color=cor)).add_to(m)

    # Gerar legenda de categorias no canto superior esquerdo.
    legenda_html = """
<div style="position: fixed; top: 10vh; left: 1vh; width: 180px; z-index:9999; font-size:14px; background-color:white; border:2px solid grey; padding: 10px;">
  <b>Legenda de Categorias</b><br>
"""
    if cat_map:
        for nome, cor in cat_map.items():
            legenda_html += f"{legend_marker_html(cor)} {html.escape(nome.capitalize())}<br>"
    else:
        seen = set()
        for _, categoria, _, _ in pontos:
            k = norm(categoria)
            if k in seen:
                continue
            seen.add(k)
            cor = color(categoria)
            legenda_html += f"{legend_marker_html(cor)} {html.escape(str(categoria).capitalize())}<br>"
    legenda_html += "</div>"
    m.get_root().html.add_child(Element(legenda_html))

    # Devolver HTML embebível mantendo altura fixa para evitar espaço extra no fim.
    mapa_html = m._repr_html_()
    return f"<div style='height:{height}px; overflow:hidden; margin:0; padding:0;'>{mapa_html}</div>"

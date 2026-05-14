from statistics import mean

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


def mapa(dados, categorias=None, height=550):
    # Validação mínima dos dados de oficinas.
    if not dados or len(dados) < 2:
        return "<p>Sem dados de oficinas para mostrar no mapa.</p>"

    # Identificar colunas relevantes da tabela de oficinas.
    headers = dados[0]
    i_nome = findeIndex(headers, "Nome", "nome", "oficina")
    i_cat = findeIndex(headers, "Categoria", "categoria")
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
        categoria = row[i_cat] if i_cat is not None and i_cat < len(row) else ""
        pontos.append((nome, categoria, lat, lon))

    if not pontos:
        return "<p>Não foi possível gerar o mapa com os dados atuais.</p>"

    # Centro médio dos pontos para inicializar o mapa.
    centro = [mean(p[2] for p in pontos), mean(p[3] for p in pontos)]
    m = folium.Map(location=[41.22, -8.5795], zoom_start=12, width="100%", height=height)

    # Construir mapa categoria->cor a partir da tabela categoriasOficinas (se existir).
    cat_map = None
    if categorias and len(categorias) > 1:
        h = categorias[0]
        ik = findeIndex(h, "nome", "Nome", "categoria")
        ic = findeIndex(h, "cor", "Cor", "color")
        if ik is not None and ic is not None:
            cat_map = { norm(r[ik]): r[ic] for r in categorias[1:] if ik < len(r) and ic < len(r) }

    # Adicionar marcadores: CircleMarker para cores hex, Marker para cores nomeadas.
    for nome, categoria, lat, lon in pontos:
        cor = color(categoria, cat_map)
        if isinstance(cor, str) and cor.startswith("#"):
            folium.CircleMarker([lat, lon], radius=6, color=cor, fill=True, fillcolor=cor, popup=nome, tooltip=nome).add_to(m)
        else:
            folium.Marker([lat, lon], popup=nome, tooltip=nome, icon=folium.Icon(color=cor)).add_to(m)

    # Gerar legenda de categorias no canto superior esquerdo.
    legenda_html = """
<div style="position: fixed; top: 10vh; left: 1vh; width: 180px; z-index:9999; font-size:14px; background-color:white; border:2px solid grey; padding: 10px;">
  <b>Legenda de Categorias</b><br>
"""
    if cat_map:
        for nome, cor in cat_map.items():
            legenda_html += f"<i style='background:{cor}; width:15px; height:15px; display:inline-block; margin-right:5px;'></i> {nome}<br>"
    else:
        seen = set()
        for _, categoria, _, _ in pontos:
            k = norm(categoria)
            if k in seen:
                continue
            seen.add(k)
            legenda_html += f"<i style='background:{color(categoria)}; width:15px; height:15px; display:inline-block; margin-right:5px;'></i> {categoria.capitalize()}<br>"
    legenda_html += "</div>"
    m.get_root().html.add_child(Element(legenda_html))

    # Devolver HTML embebível mantendo altura fixa para evitar espaço extra no fim.
    mapa_html = m._repr_html_()
    return f"<div style='height:{height}px; overflow:hidden; margin:0; padding:0;'>{mapa_html}</div>"

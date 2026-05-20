import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Procura coluna pelo nome (case-insensitive)
def achar_coluna(dados, *nomes):
	if not dados or len(dados) == 0:
		return None
	header = dados[0]
	for nome in nomes:
		for i, h in enumerate(header):
			if str(h).lower().strip() == str(nome).lower().strip():
				return i
	return None

# Converte texto para número (aceita vírgula como decimal)
def para_numero(valor):
	try:
		return float(str(valor).replace(",", "."))
	except:
		return None

# Converte texto para data (vários formatos)
def para_data(texto):
	if not texto:
		return None
	s = str(texto).strip()
	try:
		return datetime.fromisoformat(s).date()
	except:
		pass
	for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
		try:
			return datetime.strptime(s, fmt).date()
		except:
			continue
	return None

# Extrai dados de compras para DataFrame
def extrair_compras(compras):
	if not compras or len(compras) < 2:
		return pd.DataFrame()
	
	idx_nif_ofic = achar_coluna(compras, "nif oficina", "nif_oficina")
	idx_valor = achar_coluna(compras, "valor", "value")
	idx_data = achar_coluna(compras, "data", "date", "data compra")
	idx_tipo = achar_coluna(compras, "categoria", "type", "categoria_compra")
	
	linhas = []
	for row in compras[1:]:
		try:
			nif_ofic = row[idx_nif_ofic] if idx_nif_ofic is not None and idx_nif_ofic < len(row) else None
			valor = para_numero(row[idx_valor]) if idx_valor is not None and idx_valor < len(row) else None
			data = para_data(row[idx_data]) if idx_data is not None and idx_data < len(row) else None
			tipo = row[idx_tipo] if idx_tipo is not None and idx_tipo < len(row) else None
			
			if nif_ofic and valor and valor > 0:
				linhas.append({
					"nif_oficina": str(nif_ofic),
					"valor": valor,
					"data": data,
					"tipo": str(tipo).upper() if tipo else None
				})
		except:
			continue
	
	return pd.DataFrame(linhas)

# Extrai mapa de NIF -> Nome das oficinas
def extrair_oficinas(oficinas):
	if not oficinas or len(oficinas) < 2:
		return {}
	
	idx_nif = achar_coluna(oficinas, "nif", "numero fiscal", "número fiscal")
	idx_nome = achar_coluna(oficinas, "nome", "name")
	
	mapa = {}
	for row in oficinas[1:]:
		try:
			nif = row[idx_nif] if idx_nif is not None and idx_nif < len(row) else None
			nome = row[idx_nome] if idx_nome is not None and idx_nome < len(row) else None
			if nif:
				mapa[str(nif)] = nome if nome else nif
		except:
			continue
	
	return mapa

# Gera gráfico de quantidade de compras por oficina
def grafico_total(df, mapa_oficinas):
	if df.empty:
		return None
	
	compras = df.groupby("nif_oficina").size().sort_values(ascending=True)
	nomes = [mapa_oficinas.get(nif, nif) for nif in compras.index]
	
	fig = go.Figure(data=[go.Bar(y=nomes, x=compras.values, orientation='h', marker_color='steelblue')])
	fig.update_layout(title="Quantidade de Compras por Oficina", xaxis_title="Número de Compras", height=600, showlegend=False)
	
	return fig.to_html(include_plotlyjs='cdn', div_id="grafico_total")

# Gera gráfico de vendas por oficina
def grafico_oficinas(df, mapa_oficinas):
	if df.empty:
		return None
	
	vendas = df.groupby("nif_oficina")["valor"].sum().sort_values(ascending=True)
	nomes = [mapa_oficinas.get(nif, nif) for nif in vendas.index]
	
	fig = go.Figure(data=[go.Bar(y=nomes, x=vendas.values, orientation='h', marker_color='coral')])
	fig.update_layout(title="Volume de Vendas por Oficina", xaxis_title="Valor (€)", height=600, showlegend=False)
	
	return fig.to_html(include_plotlyjs='cdn', div_id="grafico_oficinas")

# Gera gráfico de vendas por tipo (Produto/Serviço)
def grafico_tipo(df):
	if df.empty:
		return None
	
	vendas = df.groupby("tipo")["valor"].sum()
	nomes = ["Produto" if x == "P" else "Serviço" if x == "S" else x for x in vendas.index]
	
	fig = go.Figure(data=[go.Pie(labels=nomes, values=vendas.values, textposition='inside', textinfo='label+percent')])
	fig.update_layout(title="Vendas por Tipo", height=600)
	
	return fig.to_html(include_plotlyjs='cdn', div_id="grafico_tipo")

# Gera gráfico de vendas ao longo do tempo
def grafico_tempo(df):
	if df.empty:
		return None
	
	df_valid = df[df["data"].notna()].copy()
	if df_valid.empty:
		return None
	
	vendas = df_valid.groupby("data")["valor"].sum().sort_index()
	
	fig = go.Figure(data=[go.Scatter(x=vendas.index, y=vendas.values, mode='lines+markers', fill='tozeroy', line=dict(color='green', width=2))])
	fig.update_layout(title="Volume de faturação ao Longo do Tempo", xaxis_title="Data", yaxis_title="Valor (€)", height=600)
	
	return fig.to_html(include_plotlyjs='cdn', div_id="grafico_tempo")

# Gera todos os gráficos do dashboard
def dashboard_data(dados):
	if not isinstance(dados, dict):
		return {}
	
	df_compras = extrair_compras(dados.get("compras", []))
	mapa_oficinas = extrair_oficinas(dados.get("oficinas", []))
	
	return {
		"total": grafico_total(df_compras, mapa_oficinas),
		"oficinas": grafico_oficinas(df_compras, mapa_oficinas),
		"tipo": grafico_tipo(df_compras),
		"tempo": grafico_tempo(df_compras),
	}

# Interface para templates - retorna HTML completo com layout customizável
def dashboard_html(dados):
	graficos = dashboard_data(dados)
	if not isinstance(graficos, dict) or not graficos:
		return "<p>Sem dados</p>"
	
	# CSS para layout responsivo
	css = """
	<style>
		.dashboard-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
		.dashboard-title { text-align: center; margin-bottom: 30px; }
		.graficos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
		.grafico-box { background: #f9f9f9; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
		.grafico-box:nth-child(1) { grid-column: 1 / -1; }
		@media (max-width: 1024px) { .graficos-grid { grid-template-columns: 1fr; } .grafico-box:nth-child(1) { grid-column: 1; } }
	</style>
	"""
	
	html = css
	html += '<div class="dashboard-container">'
	html += '<div class="graficos-grid">'
	
	# Adiciona cada gráfico numa box (tempo primeiro, ocupando 2 colunas)
	if graficos.get("tempo"):
		html += '<div class="grafico-box">' + graficos["tempo"] + '</div>'
	
	if graficos.get("total"):
		html += '<div class="grafico-box">' + graficos["total"] + '</div>'
	
	if graficos.get("tipo"):
		html += '<div class="grafico-box">' + graficos["tipo"] + '</div>'
	
	if graficos.get("oficinas"):
		html += '<div class="grafico-box">' + graficos["oficinas"] + '</div>'
	
	html += '</div></div>'
	
	return html


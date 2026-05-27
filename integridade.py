import re
from datetime import date, datetime

def relatorio_html(tabelas):
    # Recebe um dicionário {nome_tabela: dados} e retorna um relatório HTML de integridade dos dados.
	errors = []
	tables = tabelas or {}
	def normalize(value):
		#Normaliza texto: minúsculo, sem espaços.
		return str(value or "").strip().lower()

	def find_column_index(header, *candidates):
		# Procura coluna pelo nome (case-insensitive). Retorna índice ou None.
		index_map = {normalize(h): i for i, h in enumerate(header)}
		for c in candidates:
			if normalize(c) in index_map:
				return index_map[normalize(c)]
		return None

	def to_float(value):
		# Converte valor para float (aceita ',' como decimal). Retorna None se inválido.
		try:
			return float(str(value).replace(",", "."))
		except Exception:
			return None

	def parse_date(s):
		# Converte data em vários formatos. Retorna date ou None.
		if not s:
			return None
		s = str(s).strip()
		try:
			return datetime.fromisoformat(s).date()
		except Exception:
			pass
		for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
			try:
				return datetime.strptime(s, fmt).date()
			except Exception:
				continue
		return None

	def record_error(table_name, row_number, column_name, message, value=""):
		# Regista um erro encontrado.
		column_text = str(column_name).strip() if column_name else ""
		value_text = str(value).strip() if value not in (None, "") else ""
		message_text = str(message).strip()
		if column_text and message_text.lower().startswith(column_text.lower()):
			message_text = message_text[len(column_text):].lstrip(" :-")
		if column_text and value_text:
			error_text = f"{column_text} ({value_text}) {message_text}".strip()
		elif column_text:
			error_text = f"{column_text} {message_text}".strip()
		else:
			error_text = message_text
		errors.append({
			"Tabela": table_name,
			"Linha": "-" if row_number is None else str(row_number),
			"Coluna": column_name or "-",
			"Erro": error_text,
			"Valor": str(value),
		})

	def get_nif_set(table_name):
		# Extrai NIFs válidos de uma tabela. Retorna set de NIFs normalizados.
		nif_set = set()
		if tables.get(table_name) and len(tables[table_name]) > 1:
			header = tables[table_name][0]
			idx = find_column_index(header, "nif", "numero fiscal", "número fiscal", "numero", "nº nif")
			if idx is not None:
				for row in tables[table_name][1:]:
					if idx < len(row):
						nif = normalize(row[idx])
						if nif:
							nif_set.add(nif)
		return nif_set

	#  Validações genéricas (aplicáveis a qualquer tabela) 
	def validate_generic_table(table_name, data):
		# Verifica estrutura: tabela vazia, cabeçalho, colunas duplicadas, linhas inconsistentes
		if not data:
			record_error(table_name, None, None, "Tabela vazia")
			return
		header = data[0]
		if not header:
			record_error(table_name, 1, None, "Cabeçalho vazio")
			return
		
		# Detecta colunas duplicadas
		seen = set()
		for col in header:
			key = normalize(col)
			if key in seen:
				record_error(table_name, 1, col, "Coluna duplicada", col)
			seen.add(key)
		
		# Verifica consistência de número de colunas
		expected_cols = len(header)
		for i, row in enumerate(data[1:], start=2):
			if len(row) != expected_cols:
				record_error(table_name, i, None, "Número de colunas inconsistente", f"{len(row)} (esperado {expected_cols})")

	#  Validação: oficinas 
	def validate_oficinas_table(oficinas, categorias):
		# Verifica: nome não vazio, NIF duplicado, categoria existe, coordenadas válidas.
		if not oficinas or len(oficinas) < 2:
			return
		header = oficinas[0]
		idx_nome = find_column_index(header, "nome", "oficina")
		idx_nif = find_column_index(header, "nif", "numero fiscal", "número fiscal", "numero", "nº nif")
		idx_categoria = find_column_index(header, "categoria")
		idx_lat = find_column_index(header, "latitude", "lat")
		idx_lon = find_column_index(header, "longitude", "lon")

		# Extrai categorias permitidas
		allowed_cats = set()
		if categorias and len(categorias) > 1:
			cat_header = categorias[0]
			idx_cat_nome = find_column_index(cat_header, "nome", "categoria")
			if idx_cat_nome is not None:
				for r in categorias[1:]:
					if idx_cat_nome < len(r):
						allowed_cats.add(normalize(r[idx_cat_nome]))

		# Se categoria existe mas sem tabela de categorias, erro
		if idx_categoria is not None and not allowed_cats:
			record_error("oficinas", None, header[idx_categoria], "Tabela categoriasOficinas ausente ou vazia")

		seen_nifs = set()
		for i, row in enumerate(oficinas[1:], start=2):
			# Nome
			if idx_nome is not None and idx_nome < len(row):
				nome = normalize(row[idx_nome])
				if not nome:
					record_error("oficinas", i, header[idx_nome], "Nome vazio")

			# NIF
			if idx_nif is not None and idx_nif < len(row):
				nif = normalize(row[idx_nif])
				if not nif:
					record_error("oficinas", i, header[idx_nif], "NIF vazio")
				elif nif in seen_nifs:
					record_error("oficinas", i, header[idx_nif], "NIF duplicado", row[idx_nif])
				seen_nifs.add(nif)

			# Categoria
			if idx_categoria is not None and idx_categoria < len(row) and allowed_cats:
				cat = normalize(row[idx_categoria])
				if cat and cat not in allowed_cats:
					record_error("oficinas", i, header[idx_categoria], "Categoria inexistente em categoriasOficinas", row[idx_categoria])

			# Latitude
			if idx_lat is not None and idx_lat < len(row):
				lat = to_float(row[idx_lat])
				if lat is None or lat < -90 or lat > 90:
					record_error("oficinas", i, header[idx_lat], "Latitude inválida", row[idx_lat])

			# Longitude
			if idx_lon is not None and idx_lon < len(row):
				lon = to_float(row[idx_lon])
				if lon is None or lon < -180 or lon > 180:
					record_error("oficinas", i, header[idx_lon], "Longitude inválida", row[idx_lon])

			# Coordenadas fora da cidade da Maia (bounding box aproximada)
			# Bounding box derivado de: centro 41.2357, -8.6199 | área 82.99 km²
			# Norte: ~41.316 (Castêlo da Maia) | Sul: ~41.176 (Pedrouços)
			# Oeste: ~-8.695 (Gemunde)        | Este: ~-8.561 (Milheirós)
			# Fonte: OSM relation/3384812, Wikipedia freguesias da Maia
			if idx_lat is not None and idx_lon is not None and idx_lat < len(row) and idx_lon < len(row):
				lat = to_float(row[idx_lat])
				lon = to_float(row[idx_lon])
				if lat is not None and lon is not None:
					if not (41.18 <= lat <= 41.32 and -8.68 <= lon <= -8.54):
						record_error("oficinas", i, "Latitude/Longitude", "- Coordenadas fora da cidade da Maia", f"{row[idx_lat]}, {row[idx_lon]}")

		# Valida formato de horário: espera HH:MM-HH:MM (ex: 09:00-18:00)
		# Declarado fora do loop de linhas — o índice é fixo para toda a tabela
		idx_horario = find_column_index(header, "horario", "horário", "horarios", "horários", "schedule")
		if idx_horario is not None:
			# Regex: dois dígitos, ':', dois dígitos, '-', dois dígitos, ':', dois dígitos
			horario_re = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")
			for i, row in enumerate(oficinas[1:], start=2):
				if idx_horario < len(row):
					horario = str(row[idx_horario]).strip()
					# Só valida se a célula não estiver vazia
					if horario and not horario_re.match(horario):
						record_error("oficinas", i, header[idx_horario], "Horário mal formatado (esperado HH:MM-HH:MM)", row[idx_horario])
			
			

	# === Validação: utilizadores ===
	def validate_utilizadores_table(utilizadores):
		# Verifica: NIF duplicado, idade <100, género válido, data criação não futura.
		if not utilizadores or len(utilizadores) < 2:
			return
		head = utilizadores[0]
		idx_nif = find_column_index(head, "nif", "numero fiscal", "número fiscal", "numero", "nº nif")
		idx_dob = find_column_index(head, "data_nascimento", "nascimento", "data de nascimento", "dob")
		idx_genero = find_column_index(head, "genero", "género", "sexo", "gender")
		idx_created = find_column_index(head, "data_criacao", "created_at", "data de criação", "data_criação")

		seen_nifs = set()
		for i, row in enumerate(utilizadores[1:], start=2):
			# NIF
			if idx_nif is not None and idx_nif < len(row):
				nif = normalize(row[idx_nif])
				if not nif:
					record_error("utilizadores", i, head[idx_nif], "NIF vazio")
				elif nif in seen_nifs:
					record_error("utilizadores", i, head[idx_nif], "NIF duplicado", row[idx_nif])
				seen_nifs.add(nif)

			# Idade (nascimento)
			if idx_dob is not None and idx_dob < len(row):
				d = parse_date(row[idx_dob])
				if d is None:
					record_error("utilizadores", i, head[idx_dob], "Data de nascimento inválida", row[idx_dob])
				else:
					today = date.today()
					age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
					if age >= 100:
						record_error("utilizadores", i, head[idx_dob], "Idade >= 100 anos", f"{age} anos")

			# Género
			if idx_genero is not None and idx_genero < len(row):
				g = normalize(row[idx_genero])
				if g and g not in ("m", "f", "outro"):
					record_error("utilizadores", i, head[idx_genero], "Género inválido", row[idx_genero])

			# Data criação não futura
			if idx_created is not None and idx_created < len(row):
				dc = parse_date(row[idx_created])
				if dc is None:
					record_error("utilizadores", i, head[idx_created], "Data de criação inválida", row[idx_created])
				elif dc > date.today():
					record_error("utilizadores", i, head[idx_created], "Data de criação no futuro", row[idx_created])

	#  Validação: compras 
	def validate_compras_table(compras):
		# Verifica: NIF util/ofc existem, valor positivo, data não futura, categoria S ou P
		if not compras or len(compras) < 2:
			return
		head = compras[0]
		idx_nif_util = find_column_index(head, "nif_utilizador", "nifutilizador", "nif utilizador")
		idx_nif_ofc = find_column_index(head, "nif_oficina", "nifofficina", "nif oficina")
		idx_valor = find_column_index(head, "valor", "valor_compra", "valor compra", "price", "amount")
		idx_data = find_column_index(head, "data", "data_compra", "data compra", "data_criacao", "created_at")
		idx_categoria = find_column_index(head, "categoria_compra", "categoriascompra", "categoria compra", "tipo", "type")

		# Extrai NIFs válidos
		valid_nif_util = get_nif_set("utilizadores")
		valid_nif_ofc = get_nif_set("oficinas")

		for i, row in enumerate(compras[1:], start=2):
			# NIF utilizador
			if idx_nif_util is not None and idx_nif_util < len(row):
				nif = normalize(row[idx_nif_util])
				if not nif:
					record_error("compras", i, head[idx_nif_util], "NIF do utilizador vazio")
				elif nif not in valid_nif_util:
					record_error("compras", i, head[idx_nif_util], "NIF do utilizador não existe", row[idx_nif_util])

			# NIF oficina
			if idx_nif_ofc is not None and idx_nif_ofc < len(row):
				nif = normalize(row[idx_nif_ofc])
				if not nif:
					record_error("compras", i, head[idx_nif_ofc], "NIF da oficina vazio")
				elif nif not in valid_nif_ofc:
					record_error("compras", i, head[idx_nif_ofc], "NIF da oficina não existe", row[idx_nif_ofc])

			# Valor positivo
			if idx_valor is not None and idx_valor < len(row):
				val = to_float(row[idx_valor])
				if val is None:
					record_error("compras", i, head[idx_valor], "Valor inválido", row[idx_valor])
				elif val <= 0:
					record_error("compras", i, head[idx_valor], "Valor deve ser positivo", row[idx_valor])

			# Data não futura
			if idx_data is not None and idx_data < len(row):
				d = parse_date(row[idx_data])
				if d is None:
					record_error("compras", i, head[idx_data], "Data inválida", row[idx_data])
				elif d > date.today():
					record_error("compras", i, head[idx_data], "Data não pode ser futura", row[idx_data])

			# Categoria: S ou P
			if idx_categoria is not None and idx_categoria < len(row):
				cat = normalize(row[idx_categoria])
				if cat and cat not in ("s", "p"):
					record_error("compras", i, head[idx_categoria], "Categoria deve ser 'S' ou 'P'", row[idx_categoria])

	# Registar validadores por tabela
	validators = {
		"oficinas": lambda n, d: validate_oficinas_table(d, tables.get("categoriasOficinas")),
		"utilizadores": lambda n, d: validate_utilizadores_table(d),
		"compras": lambda n, d: validate_compras_table(d),
	}

	# Executar validações 
	for name, data in tables.items():
		if name in validators:
			validators[name](name, data)
		else:
			validate_generic_table(name, data)

	#  Construir HTML: resumo por tabela 
	table_names = sorted(tables.keys())
	html = "<h4>Relatório de Integridade dos Dados</h4>"
	items = []
	for n in (table_names or []):
		state = "erro" if any(e.get("Tabela") == n for e in errors) else "ok"
		color = "red" if state == "erro" else "green"
		items.append(f"<span style='color: {color}; font-weight: bold;'>{n}: {state}</span>")
	html += " | ".join(items)

	# Se não há erros, retorna apenas o resumo
	if not errors:
		return html

	#  Construir HTML: detalhes de erros 
	heads = ["Tabela", "Linha", "Coluna", "Erro"]
	html += "<br/><h3>Erros encontrados</h3>"
	html += "<table border='1' cellpadding='6' cellspacing='0'><tr>" + "".join(f"<th>{h}</th>" for h in heads) + "</tr>"
	for e in errors:
		html += "<tr>" + "".join(f"<td>{e.get(h, '')}</td>" for h in heads) + "</tr>"
	html += "</table>"
	return html

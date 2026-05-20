import datetime
import json
import os
from pathlib import Path
from flask import Flask, request
from dotenv import load_dotenv
import pygsheets
import templates

app = Flask(__name__)

load_dotenv()
is_production = os.getenv("isProduction", "false").lower() == "true"

if is_production:
    service_file_path = "/etc/secrets/mads-494811-aeff067e4247.json"
    chaves_file_path = "/etc/secrets/chave.json"
else:
    service_file_path = str(Path(__file__).resolve().parent / "secrets/mads-494811-aeff067e4247.json")
    chaves_file_path = str(Path(__file__).resolve().parent / "secrets/chave.json")

# Autorizar com ficheiro JSON de credenciais do Google
gc = pygsheets.authorize(service_file=service_file_path)
# Abrir a spreadsheet
sheet = gc.open("BaseDados_Projeto2_Grupo1")

agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Ler ficheiro chave.json (formato: {"chave": "tabela"})
# Cria um dicionário {chave: tabela}
with open(chaves_file_path) as f:
    KEYS = json.load(f)

# Função para buscar os dados de uma worksheet pelo nome da tabela
def get_data(nome):
    return sheet.worksheet_by_title(nome).get_all_values(include_tailing_empty=False)


def get_data_safe(nome):
    try:
        return get_data(nome)
    except Exception:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    # Tabela padrão (sem chave)
    tabela_atual = "oficinas"
    msg = ""
    
    # Se o utilizador enviou um formulário (POST)
    if request.method == "POST":
        chave = request.form.get("chave", "").strip()
        
        # Se a chave estiver vazia, não fazer nada
        if chave == "":
            pass
        # Verificar se a chave existe
        elif chave in KEYS:
            # Mudar para a tabela correspondente
            tabela_atual = KEYS[chave]
        else:
            # Mostrar erro se chave errada
            msg = "<p style='color:red;'><small>Chave errada!</small></p>"
    
    # Buscar dados da tabela atual (pular para a página de integridade, que não é tabela)
    if tabela_atual == "integridade" or tabela_atual == "dashboard":
        dados = {
            "oficinas": get_data_safe("oficinas"),
            "categoriasOficinas": get_data_safe("categoriasOficinas"),
            "utilizadores": get_data_safe("utilizadores"),
            "compras": get_data_safe("compras"),
        }
    elif tabela_atual == "oficinas":
        dados = get_data(tabela_atual)
        categorias = get_data("categoriasOficinas")
    else:
        dados = get_data(tabela_atual)
    # Obter função de template correspondente em templates.py
    tpl_func = getattr(templates, tabela_atual, templates.generic_table)
    content = tpl_func(dados, categorias) if tabela_atual == "oficinas" else tpl_func(dados)
    # Montar a página simples
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Grupo 1 - Projeto 2</title>
        <style>
            body{{font-family:Arial,sans-serif;margin:20px}}
            table{{border-collapse:collapse;width:100%}}
            th,td{{padding:6px 8px}}
            .header{{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:10px;margin-bottom:20px}}
            .header-text h1,.header-text h5{{margin:0}}
            .header-text h5{{margin-top:4px}}
            .header-image{{flex:0 0 auto}}
            .header-image img{{display:block;max-width:180px;height:auto}}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-text">
                <h1>Interface de análise de dados sobre oficinas</h1>
                <h5>Projeto 2 - Grupo 1 - Bernardo Pereira, Diogo Silva, Gabrielly Bresler | Metodologias Ágeis de Desenvolvimento de Software | Maio de 2026 | IPMAIA</h5>
            </div>
            <div class="header-image">
                <a href="https://www.ipmaia.pt/" target="_blank">
                    <img src="https://www.ipmaia.pt/SiteCollectionImages/logo_ipmaia_site_logo_ipmaia_small.png" alt="IPMAIA">
                </a>
                <p style="margin:12px; font-size:16px; color:green; text-align:justify; text-align: center;">{agora}</p>
            </div>
        </div>
        <p>Use a chave para acessar as diferentes tabelas:</p>
        <form method="POST">
            <input type="password" name="chave" placeholder="Chave">
            <input type="submit" value="Enviar">
        </form>
        {msg}
        <h2>{tabela_atual.capitalize()}</h2>
        {content}
    </body>
        <hr color=green><small><i></i></small>
    </html>
    """

if __name__ == '__main__':
    if is_production:
        # In production bind to all interfaces and use the PORT env var (Render, etc.)
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
    else:
        # In development bind to localhost and enable debug
        app.run(debug=True)

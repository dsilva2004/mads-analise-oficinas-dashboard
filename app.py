import datetime
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
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
    agora = datetime.datetime.now(ZoneInfo("Europe/Lisbon")).strftime("%Y-%m-%d %H:%M:%S")
    
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
            msg = '<div class="error-message">Chave de acesso inválida.</div>'
    
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
    # Montar a página com design moderno
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Grupo 1 - Projeto 2</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background-color: #f8f9fa;
                color: #2c3e50;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
            }}
            
            /* Header */
            .header {{
                background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
                border-bottom: 1px solid #e1e8ed;
                padding: 40px 0;
                margin-bottom: 40px;
            }}
            
            .header-content {{
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 40px;
                align-items: start;
            }}
            
            .header-text h1 {{
                font-size: 28px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 12px;
            }}
            
            .header-text .subtitle {{
                font-size: 13px;
                color: #666;
                line-height: 1.8;
                margin-bottom: 12px;
            }}
            
            .header-text .disclaimer {{
                font-size: 12px;
                color: #d63031;
                background-color: #fff5f5;
                padding: 10px 12px;
                border-radius: 4px;
                border-left: 3px solid #d63031;
            }}
            
            .header-image {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
            }}
            
            .header-image img {{
                max-width: 140px;
                height: auto;
                opacity: 0.9;
            }}
            
            .header-image a {{
                text-decoration: none;
            }}
            
            .timestamp {{
                font-size: 12px;
                color: #2c3e50;
                font-weight: 500;
            }}
            
            /* Navigation Section */
            .nav-section {{
                background: white;
                padding: 24px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                margin-bottom: 32px;
            }}
            
            .nav-section label {{
                display: block;
                font-size: 13px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .nav-form {{
                display: flex;
                gap: 8px;
            }}
            
            .nav-form input[type="password"] {{
                flex: 1;
                padding: 10px 14px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                transition: border-color 0.2s;
            }}
            
            .nav-form input[type="password"]:focus {{
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
            }}
            
            .nav-form input[type="submit"] {{
                padding: 10px 24px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s;
            }}
            
            .nav-form input[type="submit"]:hover {{
                background-color: #2980b9;
            }}
            
            /* Error Message */
            .error-message {{
                background-color: #fdeaea;
                color: #c0392b;
                padding: 12px 14px;
                border-radius: 4px;
                border-left: 3px solid #c0392b;
                margin-bottom: 20px;
                font-size: 13px;
            }}
            
            /* Content Title */
            .content-title {{
                font-size: 22px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 24px;
                padding-bottom: 12px;
                border-bottom: 2px solid #e1e8ed;
            }}
            
            /* Table Styles */
            .table-wrapper {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                overflow: hidden;
                margin-bottom: 32px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th {{
                background-color: #f5f7fa;
                color: #2c3e50;
                font-weight: 600;
                font-size: 13px;
                text-align: left;
                padding: 14px 16px;
                border-bottom: 2px solid #e1e8ed;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            
            td {{
                padding: 12px 16px;
                border-bottom: 1px solid #f0f0f0;
                font-size: 13px;
                color: #444;
            }}
            
            tr:hover {{
                background-color: #f9fbfc;
            }}
            
            tbody tr:last-child td {{
                border-bottom: none;
            }}
            
            /* Map Styles */
            .map-section {{
                background: transparent;
                border-radius: 0;
                box-shadow: none;
                overflow: visible;
                margin-bottom: 32px;
            }}
            
            .map-title {{
                font-size: 22px;
                font-weight: 600;
                color: #1a1a1a;
                padding: 20px 0;
                text-align: left;
                padding-left: 20px;
                margin-bottom: 12px;
                border-bottom: 2px solid #e1e8ed;
            }}
            
            .map-container {{
                width: 100%;
                height: 550px;
                overflow: hidden;
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            
            /* Footer */
            footer {{
                padding: 32px 0;
                text-align: center;
                border-top: 1px solid #e1e8ed;
                color: #7f8c8d;
                font-size: 12px;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .header-content {{
                    grid-template-columns: 1fr;
                    gap: 24px;
                }}
                
                .header-text h1 {{
                    font-size: 22px;
                }}
                
                .nav-form {{
                    flex-direction: column;
                }}
                
                .header-image {{
                    align-items: flex-start;
                }}
                
                th, td {{
                    padding: 10px 12px;
                    font-size: 12px;
                }}
            }}
            
            /* No data message */
            .no-data {{
                text-align: center;
                padding: 40px 20px;
                color: #7f8c8d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="container">
                <div class="header-content">
                    <div class="header-text">
                        <h1>Análise de Dados Sobre Oficinas</h1>
                        <div class="subtitle">
                            Projeto 2 - Grupo 1<br>
                            Bernardo Pereira, Diogo Silva, Gabrielly Bresler<br>
                            Metodologias Ágeis de Desenvolvimento de Software<br>
                            Maio de 2026 | IPMAIA
                        </div>
                        <div class="disclaimer">
                            Aviso: Os dados incluídos neste projeto são fictícios e utilizados exclusivamente em contexto educacional e de demonstração.
                        </div>
                    </div>
                    <div class="header-image">
                        <a href="https://www.ipmaia.pt/" target="_blank">
                            <img src="https://www.ipmaia.pt/SiteCollectionImages/logo_ipmaia_site_logo_ipmaia_small.png" alt="IPMAIA">
                        </a>
                        <div class="timestamp">{agora}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="nav-section">
                <label>Acesso às tabelas</label>
                <form method="POST" class="nav-form">
                    <input type="password" name="chave" placeholder="Insira a chave de acesso" autocomplete="off">
                    <input type="submit" value="Enviar">
                </form>
            </div>
            
            {msg}
            
            <h2 class="content-title">{("Categoria de Oficinas" if tabela_atual == "categoriasOficinas" else tabela_atual).capitalize()}</h2>
            {content}
            
            <footer>
                Interface de Análise de Dados | Projeto Académico
            </footer>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    if is_production:
        # In production bind to all interfaces and use the PORT env var (Render, etc.)
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
    else:
        # In development bind to localhost and enable debug
        app.run(debug=True)

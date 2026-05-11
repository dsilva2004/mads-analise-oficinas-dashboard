import datetime
from flask import Flask, request
import pygsheets

app = Flask(__name__)

# Autorizar com ficheiro JSON de credenciais do Google
gc = pygsheets.authorize(service_file="secrets/mads-494811-aeff067e4247.json")
# Abrir a spreadsheet
sheet = gc.open("BaseDados_Projeto2_Grupo1")


agora = str(datetime.datetime.now())[0:19]
bottomline = f"<hr color=green><small><i>{agora} - Projeto 2 - Grupo 1 - Desenvolvido por Diogo Silva, Gabrielly Bresler e Bernardo Pereira</i></small>"


# Ler ficheiro chave.txt (formato: chave:tabela)
# Cria um dicionário {chave: tabela}
with open("secrets/chave.txt") as f:
    KEYS = {line.strip().split(":")[0]: line.strip().split(":")[1] for line in f if ":" in line}

# Função para buscar os dados de uma worksheet pelo nome da tabela
def get_data(nome):
    return sheet.worksheet_by_title(nome).get_all_values(include_tailing_empty=False)

# Converte os dados em uma tabela HTML Simples
def tabela(dados):
    if not dados:
        return "<p>Sem dados</p>"
    
    # Criar cabeçalho
    html = "<table border='1' cellpadding='2' cellspacing='0'><tr>"
    for h in dados[0]:  # Primeira linha = headers
        html += f"<th>{h}</th>"
    html += "</tr>"

    # Adicionar linhas de dados
    for row in dados[1:]:  # Restantes linhas
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    
    return html + "</table>"

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
    
    # Buscar dados da tabela atual
    dados = get_data(tabela_atual)
    
    # Retornar HTML com a página
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Grupo 1 - Projeto 2 </title>
    </head>
    <body>
        <h1>Projeto 2</h1>
        
        <!-- Formulário de chave -->
        <form method="POST">
            <input type="password" name="chave" placeholder="Chave">
            <input type="submit" value="Enviar">
        </form>
        
        <!-- Mostrar mensagem de erro se houver -->
        {msg}
        
        <!-- Mostrar tabela -->
        <h2>{tabela_atual.capitalize()}</h2>
        {tabela(dados)}
    </body>
    {bottomline}
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)



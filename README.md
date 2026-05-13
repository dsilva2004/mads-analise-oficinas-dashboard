# Dashboard de Análise de Oficinas

Aplicação web em Flask que lê dados de um Google Sheets e os apresenta em tabelas HTML com controlo de acesso por chaves.

## Funcionalidades

- Leitura de dados do Google Sheets em tempo real
- Tabela `oficinas` visível por defeito
- Acesso a outras tabelas através de chaves configuráveis
- Validação de chaves com feedback ao utilizador

## Pré-requisitos

- Python 3.7+
- Conta Google com acesso ao Google Cloud Console
- Google Sheets criada e partilhada com o Service Account
- Ficheiro JSON com credenciais do Google

## Instalação

```bash
# 1. Entrar na pasta do projeto
cd mads-analise-oficinas-dashboard

# 2. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt
```

## Configuração

**1. Credenciais do Google**

No [Google Cloud Console](https://console.cloud.google.com):
- Criar um projeto e ativar a **Google Sheets API**
- Criar uma **Service Account** e descarregar o ficheiro JSON
- Guardar o ficheiro em `secrets/`
- Partilhar a spreadsheet com o email do Service Account

Atualizar `app.py` com os dados corretos:
```python
gc = pygsheets.authorize(service_file="secrets/seu-ficheiro.json")
sheet = gc.open("Nome da sua Spreadsheet")
```

**2. Ficheiro de chaves**

Criar `secrets/chave.txt` com o formato `chave:tabela`, uma por linha:
```
admin1234:utilizadores
grupo1:categoriasOficinas
teste123:compras
```

## Execução

```bash
python app.py
```

Aceder em: [http://localhost:5000](http://localhost:5000)

## Estrutura

```
├── app.py               # Aplicação principal
├── requirements.txt     # Dependências
├── VENV.md              # Guia de ambiente virtual
└── secrets/
    ├── *.json           # Credenciais Google  ⚠️ não commitar
    └── chave.txt        # Chaves de acesso    ⚠️ não commitar
```

## Segurança

A pasta `secrets/` está incluída no `.gitignore`. **Nunca** commitar credenciais nem o ficheiro de chaves.

```bash
git status  # Confirmar que secrets/ não aparece listado
```
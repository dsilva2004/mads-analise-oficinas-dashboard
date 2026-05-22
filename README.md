# Análise de Dados sobre Oficinas

Aplicação web em Flask que lê dados de um Google Sheets e apresenta tabelas, mapa interativo, dashboard e validação de dados, com controlo de acesso por chaves.

Relatório do projeto desenvolvido disponível em: https://docs.google.com/document/d/1MobcrBR_oaL5d95joBGpqeJOhM-1aHeL3ARiywxEzGY/edit?usp=sharing

> Projeto dispoível na plataforma Render.com [Link do Projeto](https://mads-analise-de-oficinas-dashboard.onrender.com/). As chaves de acesso aos dados privados estão disponíveis no relatório do projeto.

> ⚠️ Desenvolvido com apoio de [Claude.ai](https://claude.ai), [GitHub Copilot](https://github.com/features/copilot) e [ChatGPT](https://chatgpt.com).
---

## Funcionalidades

| Módulo | Descrição |
|---|---|
| **Tabelas** | Oficinas, utilizadores, compras e categorias |
| **Mapa** | Marcadores coloridos por categoria, gerados com `folium` |
| **Dashboard** | Gráficos de compras, vendas e faturação com `pandas` + `plotly` |
| **Integridade** | Validação automática dos dados com relatório de erros |
| **Acesso** | Controlo por chaves configuráveis em `secrets/chave.json` |

---

## Pré-requisitos

- Python 3.7+
- Conta Google com acesso ao [Google Cloud Console](https://console.cloud.google.com)
- Google Sheets partilhada com a conta de serviço
- Ficheiro JSON com as credenciais do Google

---

## Instalação

```bash
# 1. Entrar na pasta do projeto
cd Projeto2

# 2. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt
```

---

## Configuração

### 1. Credenciais do Google

No [Google Cloud Console](https://console.cloud.google.com):

1. Criar um projeto e ativar a **Google Sheets API**
2. Criar uma **conta de serviço** e descarregar o ficheiro JSON
3. Guardar o ficheiro em `secrets/`
4. Partilhar a folha de cálculo com o email da conta de serviço

Em `app.py`, ajustar conforme necessário:

```python
gc = pygsheets.authorize(service_file=service_file_path)
sheet = gc.open("BaseDados_Projeto2_Grupo1")
```

### 2. Chaves de acesso

Criar `secrets/chave.json` com o formato `{"chave": "tabela"}`:

```json
{
  "utilizadores": "utilizadores",
  "categorias": "categoriasOficinas",
  "compras": "compras",
  "integridade": "integridade",
  "dashboard": "dashboard"
}
```

### 3. Variáveis de ambiente

Criar um ficheiro `.env` na raiz do projeto:

```
isProduction=false
```

Em produção (ex.: Render), definir `isProduction=true`. A aplicação irá procurar as credenciais em `/etc/secrets/`.

---

## Execução

**Desenvolvimento:**

```bash
python app.py
# Disponível em http://127.0.0.1:5000
```

**Produção (Render):**

- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Variável de ambiente: `isProduction=true`
- Credenciais disponíveis em `/etc/secrets/`

---

## Estrutura do projeto

```
├── app.py                # Aplicação Flask principal
├── templates.py          # Gerador de HTML para cada página
├── integridade.py        # Validação de dados
├── mapa.py               # Mapa interativo (folium)
├── dashboard.py          # Gráficos (pandas + plotly)
├── requirements.txt      # Dependências
├── README.md             # Este ficheiro
└── secrets/
    ├── *.json            # Credenciais Google  ⚠️ não incluir no repositório
    └── chave.json        # Chaves de acesso    ⚠️ não incluir no repositório
```

---

## Validações de integridade

**Todas as tabelas**
- Tabela ou cabeçalho vazios, colunas duplicadas, número de colunas inconsistente

**Oficinas** — nome/NIF vazios ou duplicados, categoria inexistente, coordenadas fora do intervalo válido

**Utilizadores** — NIF vazio/duplicado, idade > 100 anos, género inválido (apenas M, F ou Outro), data de registo no futuro

**Compras** — NIFs vazios ou inexistentes, valor não positivo, data no futuro, categoria inválida (apenas S ou P)

---

## Autores

Bernardo Pereira, Diogo Silva, Gabrielly Bresler

**Unidade Curricular:** Metodologias Ágeis de Desenvolvimento de Software · Projeto 2  
**Data:** Maio de 2026 · **Instituição:** IPMAIA

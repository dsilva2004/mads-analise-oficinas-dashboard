# Análise de Dados sobre Oficinas

Aplicação web desenvolvida em Flask que lê dados de um Google Sheets e apresenta tabelas, mapas interativos e validação de dados, com controlo de acesso por chaves.

---

## Funcionalidades

- Tabelas com dados de oficinas, utilizadores, compras e categorias
- Mapa interativo com marcadores coloridos por categoria
- Validação automática de integridade dos dados
- Controlo de acesso com chaves configuráveis
- Dados carregados em tempo real a partir do Google Sheets

---

## Tabelas disponíveis

| Tabela | Descrição |
|---|---|
| `oficinas` | Nome, NIF, categoria e localização das oficinas |
| `utilizadores` | NIF, género, data de nascimento e data de registo |
| `compras` | NIF do utilizador, NIF da oficina, valor, data e categoria |
| `categoriasOficinas` | Categorias disponíveis (usado na validação e nas cores do mapa) |
| `integridade` | Relatório de erros e validação geral dos dados |

---

## Pré-requisitos

- Python 3.7 ou superior
- Conta Google com acesso ao Google Cloud Console
- Google Sheets partilhada com a conta de serviço
- Ficheiro JSON com as credenciais do Google

---

## Instalação

```bash
# 1. Entrar na pasta do projeto
cd Projeto2

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar as dependências
pip install -r requirements.txt
```

---

## Configuração

### Credenciais do Google

No [Google Cloud Console](https://console.cloud.google.com):

1. Criar um projeto e ativar a **Google Sheets API**
2. Criar uma **conta de serviço** e descarregar o ficheiro JSON
3. Guardar o ficheiro na pasta `secrets/`
4. Partilhar a folha de cálculo com o email da conta de serviço

O ficheiro e o nome da folha estão definidos em `app.py`:

```python
gc = pygsheets.authorize(service_file="secrets/mads-494811-aeff067e4247.json")
sheet = gc.open("BaseDados_Projeto2_Grupo1")
```

### Chaves de acesso

Criar o ficheiro `secrets/chave.json` com o formato `{"chave": "tabela"}`:

```json
{
  "admin1234": "utilizadores",
  "grupo1": "categoriasOficinas",
  "teste123": "compras",
  "integridade2026": "integridade"
}
```

---

## Execução

```bash
python app.py
```

Abrir no browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

- A página inicial mostra a tabela de oficinas com o mapa interativo.
- Para aceder a outras tabelas, usar o formulário com a chave correspondente.

---

## Estrutura do projeto

```
├── app.py                    # Aplicação Flask principal
├── templates.py              # Gerador de HTML para cada página
├── integridade.py            # Validação de dados
├── mapa.py                   # Gerador do mapa interativo (folium)
├── requirements.txt          # Dependências do projeto
├── README.md                 # Este ficheiro
└── secrets/
    ├── *.json                # Credenciais Google  ⚠️ não incluir no repositório
    └── chave.json            # Chaves de acesso    ⚠️ não incluir no repositório
```

---

## Validações de integridade

### Todas as tabelas
- Tabela ou cabeçalho vazios
- Colunas duplicadas
- Número de colunas inconsistente entre linhas

### Oficinas
- Nome ou NIF vazios
- NIFs duplicados
- Categoria inexistente em `categoriasOficinas`
- Latitude fora do intervalo [-90, 90]
- Longitude fora do intervalo [-180, 180]

### Utilizadores
- NIF vazio ou duplicado
- Idade superior a 100 anos
- Género inválido (apenas M, F ou Outro)
- Data de registo no futuro

### Compras
- NIF do utilizador ou da oficina vazios ou inexistentes
- Valor não positivo
- Data no futuro
- Categoria inválida (apenas S ou P)

---

## Segurança

A pasta `secrets/` está incluída no `.gitignore`. Os ficheiros seguintes **nunca devem ser enviados para o repositório**:

- Credenciais do Google (ficheiros JSON)
- Ficheiro de chaves de acesso

Para confirmar que estão excluídos:

```bash
git status
```

---

## Autores

Bernardo Pereira, Diogo Silva, Gabrielly Bresler

**Curso:** Metodologias Ágeis de Desenvolvimento de Software  
**Projeto:** 2 — Análise de Dados sobre Oficinas  
**Data:** Maio de 2026  
**Instituição:** IPMAIA

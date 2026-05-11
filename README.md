# Projeto 2 - Dashboard HTLM

Aplicação Flask que extrai dados de um Google Sheets e exibe em tabelas HTML. Cada tabela tem uma chave de acesso.

**Funcionalidades:**
- ✅ Lê dados do Google Sheets em tempo real
- ✅ Tabela "oficinas" visível por padrão
- ✅ Acesso a outras tabelas com chaves
- ✅ Chaves vazias não alteram nada
- ✅ Chaves erradas mostram erro

---

## 📋 Pré-requisitos

- Python 3.7+
- Conta Google ativa
- Google Sheets criada e partilhada
- Ficheiro JSON com credenciais do Google

---

## 🚀 Instalação Rápida

### Passo 1: Clonar/Descarregar

```bash
cd /caminho/para/Projeto2
```

### Passo 2: Criar e Ativar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Google Sheets

**A. Criar Service Account no Google Cloud:**

1. Aceder a [Google Cloud Console](https://console.cloud.google.com)
2. Criar novo projeto
3. Ativar "Google Sheets API"
4. Ir para "Credenciais" → "Service Account"
5. Descarregar ficheiro JSON
6. Guardar em pasta `secrets/`

**B. Atualizar app.py:**

Editar linha 8 do `app.py` com o nome do ficheiro JSON:

```python
gc = pygsheets.authorize(service_file="secrets/seu-ficheiro.json")
```

Editar linha 10 com o nome da spreadsheet:

```python
sheet = gc.open("Nome da sua Spreadsheet")
```

**C. Partilhar Spreadsheet:**

Na Google Sheets, clique em "Partilhar" e adicione o email do Service Account (que está no ficheiro JSON).

### Passo 5: Configurar Chaves

Editar `secrets/chave.txt` com o formato `chave:tabela`:

```
admin1234:utilizadores
grupo1:categoriasOficinas
teste123:compras
```

### Passo 6: Executar

```bash
python app.py
```

Abrir no navegador: **http://localhost:5000**

---

## 📁 Estrutura do Projeto

```
Projeto2/
├── app.py                              # Código principal (comentado)
├── requirements.txt                    # Dependências Python
├── README.md                           # Este ficheiro
├── VENV.md                             # Guia de ambiente virtual
├── .gitignore                          # Ficheiros ignorados no Git
└── secrets/
    ├── mads-494811-aeff067e4247.json   # Credenciais Google (NÃO COMMITAR)
    └── chave.txt                       # Chaves de acesso (NÃO COMMITAR)
```

---

## 🔑 Como Funciona

**Fluxo da Aplicação:**

1. **Página Inicial** → Mostra tabela "oficinas" automaticamente
2. **Utilizador Insere Chave** → Clica em "OK"
3. **Sistema Valida:**
   - ✅ Chave correta → Muda para a tabela correspondente
   - ⚠️ Chave vazia → Não faz nada (fica na tabela atual)
   - ❌ Chave errada → Mostra mensagem de erro em vermelho

---

## ⚙️ Configuração

### Mudar a Spreadsheet

Editar em `app.py` (linhas 10-11):

```python
gc.open("BaseDados_Projeto2_Grupo1")  # Nome da spreadsheet
sheet.worksheet_by_title(nome)         # Nome da aba/worksheet
```

### Mudar o Ficheiro de Credenciais

Editar em `app.py` (linha 8):

```python
gc = pygsheets.authorize(service_file="caminho/para/novo/ficheiro.json")
```

---

## 📝 Formato do Ficheiro Chaves

Ficheiro: `secrets/chave.txt`

Formato: **uma chave por linha**

```
chave1:oficinas
chave2:utilizadores
chave3:categoriasOficinas
chave4:compras
```

**Exemplo prático:**

```
admin1234:utilizadores
grupo1:categoriasOficinas
teste123:compras
password456:compras
```

**Notas:**
- Sem espaços antes/depois dos `:` (são removidos automaticamente)
- Uma chave pode aceder a múltiplas tabelas (exemplo: password456 → compras)
- Chave vazia não funciona

---

## 🔒 Segurança

**⚠️ IMPORTANTE:**

- ❌ **Nunca** commitar `secrets/` para o Git
- ❌ **Nunca** partilhar ficheiro JSON com credenciais
- ✅ Ficheiro `.gitignore` já protege a pasta `secrets/`
- ✅ Manter credenciais só no seu computador

**Verificar se está seguro:**

```bash
git status  # Não deve mostrar secrets/
```

---

## 🛑 Desativar Ambiente Virtual

Quando terminar de trabalhar:

```bash
deactivate
```

---

## 📊 Troubleshooting

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: pygsheets` | Ativar venv e instalar: `pip install -r requirements.txt` |
| `FileNotFoundError: secrets/chave.txt` | Criar ficheiro `secrets/chave.txt` com chaves |
| `Error 403: Permission denied` | Partilhar spreadsheet com email do Service Account |
| Tabela não aparece | Verificar nome exato da worksheet |

---

## 📚 Ficheiros Adicionais

- **VENV.md** → Guia completo sobre ambientes virtuais
- **app.py** → Código comentado linha por linha
- **.gitignore** → Lista de ficheiros ignorados

---

## 🎉 Pronto!

Projeto configurado e pronto para usar. Para mais informações, consulte `VENV.md`.

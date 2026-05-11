# 🐍 Ambiente Virtual - Guia Rápido

## O Que É?

Pasta isolada que tem seu próprio Python e packages. Não afeta o sistema.

---

## ✅ Criar

```bash
python3 -m venv venv
```

Isto cria pasta `venv/` no projeto.

---

## ✅ Ativar

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

Depois de ativar, o terminal mostra `(venv)` no início.

---

## ✅ Instalar Packages

```bash
pip install -r requirements.txt
```

Isto instala Flask, pygsheets, etc. **só neste projeto**.

---

## ✅ Desativar

```bash
deactivate
```

Volta ao Python normal do sistema.

---

## 💡 Dicas

- `pip list` - Ver packages instalados
- `pip freeze > requirements.txt` - Atualizar requirements
- Sempre ativar antes de trabalhar
- Sempre desativar quando terminar

---

## 🗑️ Limpar

Para remover tudo:
```bash
rm -rf venv
```

E criar novo depois se precisar.

---

**Pronto! 🚀**

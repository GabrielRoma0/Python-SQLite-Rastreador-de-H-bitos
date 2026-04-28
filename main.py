import sqlite3
from datetime import date, timedelta


# ─────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────

def conectar() -> sqlite3.Connection:
    """Cria/conecta ao banco e retorna a conexão."""
    conn = sqlite3.connect("habitos.db")
    criar_tabelas(conn)
    return conn

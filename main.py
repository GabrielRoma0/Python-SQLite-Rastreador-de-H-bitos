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


def criar_tabelas(conn: sqlite3.Connection) -> None:
    """Cria as tabelas se ainda não existirem e aplica migrations necessárias."""
    conn.executescript("""
                       CREATE TABLE IF NOT EXISTS habitos
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           nome
                           TEXT
                           NOT
                           NULL
                           UNIQUE,
                           criado_em
                           TEXT
                       );

                       CREATE TABLE IF NOT EXISTS registros
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           habito_id
                           INTEGER
                           NOT
                           NULL,
                           data
                           TEXT
                           NOT
                           NULL,
                           FOREIGN
                           KEY
                       (
                           habito_id
                       ) REFERENCES habitos
                       (
                           id
                       ),
                           UNIQUE
                       (
                           habito_id,
                           data
                       )
                           );
                       """)

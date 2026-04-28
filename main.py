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
        CREATE TABLE IF NOT EXISTS habitos (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT NOT NULL UNIQUE,
            criado_em TEXT
        );


                               CREATE TABLE IF NOT EXISTS registros (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            habito_id INTEGER NOT NULL,
            data      TEXT NOT NULL,
            FOREIGN KEY (habito_id) REFERENCES habitos(id),
            UNIQUE (habito_id, data)
        );
    """)


 # Migration: atualiza bancos antigos que não possuem a coluna criado_em
    colunas = [row[1] for row in conn.execute("PRAGMA table_info(habitos)")]
    if "criado_em" not in colunas:
        conn.execute("ALTER TABLE habitos ADD COLUMN criado_em TEXT")
        conn.execute("UPDATE habitos SET criado_em = ? WHERE criado_em IS NULL", (str(date.today()),))

    conn.commit()

# ─────────────────────────────────────────
#  VALIDAÇÃO
# ─────────────────────────────────────────

def validar_nome(nome: str) -> bool:
    """Valida se o nome do hábito é aceitável."""
    return bool(nome) and len(nome) <= 50


def validar_data(data: str) -> bool:
    """Valida se a string está no formato YYYY-MM-DD."""
    try:
        date.fromisoformat(data)
        return True
    except ValueError:
        return False

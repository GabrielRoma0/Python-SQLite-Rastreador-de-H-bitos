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

# ─────────────────────────────────────────
#  HÁBITOS
# ─────────────────────────────────────────

def adicionar_habito(conn: sqlite3.Connection, nome: str) -> None:
    try:
        conn.execute("INSERT INTO habitos (nome) VALUES (?)", (nome,))
        conn.commit()
        print(f"  ✓ Hábito '{nome}' adicionado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"  ✗ O hábito '{nome}' já existe.")


def remover_habito(conn: sqlite3.Connection, nome: str) -> None:
    cursor = conn.execute("SELECT id FROM habitos WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if not row:
        print(f"  ✗ Hábito '{nome}' não encontrado.")
        return

    confirmar = input(f"  Tem certeza que deseja remover '{nome}'? (s/N): ").strip().lower()
    if confirmar != "s":
        print("  Operação cancelada.")
        return

    habito_id = row[0]
    conn.execute("DELETE FROM registros WHERE habito_id = ?", (habito_id,))
    conn.execute("DELETE FROM habitos WHERE id = ?", (habito_id,))
    conn.commit()
    print(f"  ✓ Hábito '{nome}' e seus registros foram removidos.")

def listar_habitos(conn: sqlite3.Connection) -> None:
    cursor = conn.execute("SELECT id, nome FROM habitos ORDER BY nome")
    habitos = cursor.fetchall()
    if not habitos:
        print("  Nenhum hábito cadastrado ainda.")
    else:
        print("\n  Hábitos cadastrados:")
        for i, (habito_id, nome) in enumerate(habitos, 1):
            streak = calcular_streak(conn, habito_id)
            streak_txt = f" {streak} dia(s)" if streak > 0 else ""
            print(f"    {i}. {nome}{streak_txt}")


# ─────────────────────────────────────────
#  REGISTROS
# ─────────────────────────────────────────

def marcar_habito(conn: sqlite3.Connection, nome: str, data: str | None = None) -> None:
    if data is None:
        data = str(date.today())

    if not validar_data(data):
        print(f"  ✗ Data inválida: '{data}'. Use o formato YYYY-MM-DD.")
        return

    cursor = conn.execute("SELECT id FROM habitos WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if not row:
        print(f"  ✗ Hábito '{nome}' não encontrado.")
        return

    try:
        conn.execute(
            "INSERT INTO registros (habito_id, data) VALUES (?, ?)",
            (row[0], data)
        )
        conn.commit()
        print(f"  ✓ '{nome}' marcado como feito em {data}!")
    except sqlite3.IntegrityError:
        print(f"  ✗ '{nome}' já foi marcado em {data}.")


def desmarcar_habito(conn: sqlite3.Connection, nome: str, data: str | None = None) -> None:
    if data is None:
        data = str(date.today())

    if not validar_data(data):
        print(f"  ✗ Data inválida: '{data}'. Use o formato YYYY-MM-DD.")
        return

    cursor = conn.execute("SELECT id FROM habitos WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if not row:
        print(f"  ✗ Hábito '{nome}' não encontrado.")
        return

    conn.execute(
        "DELETE FROM registros WHERE habito_id = ? AND data = ?",
        (row[0], data)
    )
    conn.commit()
    print(f"  ✓ Marcação de '{nome}' em {data} removida.")


# ─────────────────────────────────────────
#  STREAK
# ─────────────────────────────────────────

def calcular_streak(conn: sqlite3.Connection, habito_id: int) -> int:
    """Retorna quantos dias consecutivos (até hoje) o hábito foi cumprido."""
    cursor = conn.execute(
        "SELECT data FROM registros WHERE habito_id = ? ORDER BY data DESC",
        (habito_id,)
    )
    datas = {date.fromisoformat(r[0]) for r in cursor.fetchall()}
    streak, dia = 0, date.today()
    while dia in datas:
        streak += 1
        dia -= timedelta(days=1)
    return streak


# ─────────────────────────────────────────
#  RELATÓRIOS
# ─────────────────────────────────────────

def relatorio_semanal(conn: sqlite3.Connection) -> None:
    hoje = date.today()
    dias = [(hoje - timedelta(days=i)) for i in range(6, -1, -1)]
    datas = [str(d) for d in dias]

    cursor = conn.execute("SELECT id, nome FROM habitos ORDER BY nome")
    habitos = cursor.fetchall()

    if not habitos:
        print("  Nenhum hábito para exibir.")
        return

    placeholders = ",".join("?" * 7)
    cursor = conn.execute(
        f"SELECT habito_id, data FROM registros WHERE data IN ({placeholders})",
        datas
    )
    feitos = {(r[0], r[1]) for r in cursor.fetchall()}

    print()
    print("  RELATÓRIO SEMANAL")
    print("  " + "─" * 60)

    cabecalho = "  {:<20}".format("Hábito")
    for d in dias:
        cabecalho += " {:^5}".format(d.strftime("%d/%m"))
    cabecalho += "  {:>6}".format("Taxa")
    print(cabecalho)
    print("  " + "─" * 60)

    for habito_id, nome in habitos:
        linha = "  {:<20}".format(nome[:20])
        total = 0
        for data in datas:
            if (habito_id, data) in feitos:
                linha += "  {:^5}".format("✓")
                total += 1
            else:
                linha += "  {:^5}".format("·")
        taxa = int((total / 7) * 100)
        linha += "  {:>5}%".format(taxa)
        print(linha)

    print("  " + "─" * 60)

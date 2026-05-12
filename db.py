"""
db.py - Capa de base de datos SQLite para Prode Mundial 2026

Tablas:
- users: jugadores y admin (login por email)
- password_reset_tokens: codigos de recuperacion de contraseña
- group_matches: fixtures de fase de grupos (72 partidos)
- official_results: resultados oficiales (solo admin)
- predictions: pronosticos de cada jugador por partido
- final_predictions: campeon, finalista, semis, goleadores
- playoff_matches: partidos de eliminacion directa
- playoff_results: resultados oficiales de playoffs
- playoff_predictions: pronosticos de playoffs
- group_standings_official: posiciones finales oficiales por grupo
- scorer_standings: tabla de goleadores oficial
"""

import sqlite3
import hashlib
import os
import secrets
import string
from datetime import datetime, timedelta
from contextlib import contextmanager
from data import GROUP_MATCHES, ALL_TEAMS

DB_PATH = os.environ.get("PRODE_DB_PATH", "prode_mundial.db")


@contextmanager
def get_db():
    """Context manager para conexiones a la DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _get_admin_credentials() -> tuple[str, str]:
    """Lee credenciales del admin desde secrets de Streamlit, con fallback."""
    try:
        import streamlit as st
        email = st.secrets["admin"]["email"]
        password = st.secrets["admin"]["password"]
        return email, password
    except Exception:
        return "admin@prode.local", "admin2026"


# ============================================================
# INICIALIZACION Y MIGRACION
# ============================================================
def init_db():
    """Crea todas las tablas si no existen, migra schema si es necesario, carga fixtures."""
    with get_db() as conn:

        # --- Migracion: renombrar columna username → email si es necesario ---
        cols_info = conn.execute("PRAGMA table_info(users)").fetchall()
        if cols_info:
            col_names = [row[1] for row in cols_info]
            if "email" not in col_names and "username" in col_names:
                conn.executescript("""
                    CREATE TABLE users_migrated (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        display_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_admin INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    INSERT INTO users_migrated (id, email, display_name, password_hash, is_admin, created_at)
                        SELECT id, username, display_name, password_hash, is_admin, created_at FROM users;
                    DROP TABLE users;
                    ALTER TABLE users_migrated RENAME TO users;
                """)

        # --- Crear tablas ---
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS group_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                match_order INTEGER NOT NULL,
                team_home TEXT NOT NULL,
                team_away TEXT NOT NULL,
                UNIQUE(group_name, match_order)
            );

            CREATE TABLE IF NOT EXISTS official_results (
                match_id INTEGER PRIMARY KEY REFERENCES group_matches(id),
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                match_id INTEGER NOT NULL REFERENCES group_matches(id),
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, match_id)
            );

            CREATE TABLE IF NOT EXISTS final_predictions (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                champion TEXT,
                finalist TEXT,
                semi1 TEXT,
                semi2 TEXT,
                scorer1 TEXT,
                scorer2 TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playoff_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_name TEXT NOT NULL,
                position INTEGER NOT NULL,
                team_home TEXT,
                team_away TEXT,
                bracket_side TEXT DEFAULT 'L',
                UNIQUE(round_name, position, bracket_side)
            );

            CREATE TABLE IF NOT EXISTS playoff_results (
                match_id INTEGER PRIMARY KEY REFERENCES playoff_matches(id),
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                advancing_team TEXT NOT NULL,
                mvp_player TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playoff_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                match_id INTEGER NOT NULL REFERENCES playoff_matches(id),
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                advancing_team TEXT NOT NULL,
                mvp_player TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, match_id)
            );

            CREATE TABLE IF NOT EXISTS scorer_standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                goals INTEGER NOT NULL DEFAULT 0,
                rank INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                red_cards INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                UNIQUE(group_name, team_name)
            );

            CREATE TABLE IF NOT EXISTS tournament_info (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS group_classification_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                group_name TEXT NOT NULL,
                first_place TEXT NOT NULL,
                second_place TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, group_name)
            );

            CREATE TABLE IF NOT EXISTS best_third_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                group_name TEXT NOT NULL,
                team_name TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, group_name)
            );

            CREATE TABLE IF NOT EXISTS official_group_classification (
                group_name TEXT PRIMARY KEY,
                first_place TEXT NOT NULL,
                second_place TEXT NOT NULL,
                third_place TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS official_best_thirds (
                group_name TEXT PRIMARY KEY,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS match_schedule (
                group_name TEXT NOT NULL,
                match_order INTEGER NOT NULL,
                match_date TEXT NOT NULL,
                match_time TEXT NOT NULL,
                stadium TEXT NOT NULL,
                city TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_name, match_order)
            );
        """)

        # Insertar fixtures si la tabla esta vacia
        existing = conn.execute("SELECT COUNT(*) FROM group_matches").fetchone()[0]
        if existing == 0:
            for group, order, home, away in GROUP_MATCHES:
                conn.execute(
                    "INSERT INTO group_matches (group_name, match_order, team_home, team_away) VALUES (?, ?, ?, ?)",
                    (group, order, home, away)
                )

        # Crear admin si no existe
        admin = conn.execute("SELECT id FROM users WHERE is_admin = 1").fetchone()
        if not admin:
            admin_email, admin_pass = _get_admin_credentials()
            conn.execute(
                "INSERT INTO users (email, display_name, password_hash, is_admin) VALUES (?, ?, ?, ?)",
                (admin_email.lower().strip(), "Administrador", hash_password(admin_pass), 1)
            )


# ============================================================
# HORARIOS DE PARTIDOS
# ============================================================
def get_match_schedule(group_name: str = None) -> list[dict]:
    """Retorna todos los horarios, o solo los de un grupo."""
    with get_db() as conn:
        if group_name:
            rows = conn.execute(
                "SELECT * FROM match_schedule WHERE group_name = ? ORDER BY match_order",
                (group_name,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM match_schedule ORDER BY group_name, match_order"
            ).fetchall()
        return [dict(r) for r in rows]


def set_match_schedule(group_name: str, match_order: int,
                       match_date: str, match_time: str,
                       stadium: str, city: str) -> None:
    """Inserta o actualiza el horario de un partido."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO match_schedule (group_name, match_order, match_date, match_time, stadium, city)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(group_name, match_order) DO UPDATE SET
                match_date = excluded.match_date,
                match_time = excluded.match_time,
                stadium = excluded.stadium,
                city = excluded.city,
                updated_at = CURRENT_TIMESTAMP
        """, (group_name, match_order, match_date, match_time, stadium, city))


def get_schedule_as_dict() -> dict:
    """Retorna el horario como dict {(group, order): (date, time, stadium, city)}."""
    rows = get_match_schedule()
    return {
        (r["group_name"], r["match_order"]): (
            r["match_date"], r["match_time"], r["stadium"], r["city"]
        )
        for r in rows
    }


# ============================================================
# USUARIOS
# ============================================================
def create_user(email: str, display_name: str, password: str) -> int:
    """Crea un usuario. Retorna el ID."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, display_name, password_hash) VALUES (?, ?, ?)",
            (email.lower().strip(), display_name.strip(), hash_password(password))
        )
        return cursor.lastrowid


def authenticate_user(email: str, password: str) -> dict | None:
    """Autentica un usuario por email y contraseña. Retorna dict con datos o None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, display_name, is_admin FROM users WHERE email = ? AND password_hash = ?",
            (email.lower().strip(), hash_password(password))
        ).fetchone()
        if row:
            return dict(row)
        return None


def user_exists(email: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return row is not None


def get_all_users() -> list[dict]:
    """Retorna todos los usuarios no-admin."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, email, display_name FROM users WHERE is_admin = 0 ORDER BY display_name"
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_users_detailed() -> list[dict]:
    """Retorna todos los usuarios no-admin con info detallada."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT u.id, u.email, u.display_name, u.created_at,
                   COUNT(DISTINCT p.match_id) as predictions_count
            FROM users u
            LEFT JOIN predictions p ON u.id = p.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY u.display_name
        """).fetchall()
        return [dict(r) for r in rows]


def delete_user(user_id: int):
    """Elimina un usuario y todos sus datos asociados."""
    with get_db() as conn:
        conn.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM final_predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM playoff_predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM group_classification_predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM best_third_predictions WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ? AND is_admin = 0", (user_id,))


def reset_user_password(user_id: int, new_password: str):
    """Resetea la contraseña de un usuario (solo no-admin)."""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ? AND is_admin = 0",
            (hash_password(new_password), user_id)
        )


# ============================================================
# RECUPERACION DE CONTRASEÑA
# ============================================================
def create_reset_token(email: str) -> str | None:
    """
    Genera un codigo de 6 digitos para recuperacion de contraseña.
    Retorna el codigo si el email existe, None si no existe.
    El codigo expira en 15 minutos.
    """
    with get_db() as conn:
        user = conn.execute(
            "SELECT id FROM users WHERE email = ? AND is_admin = 0",
            (email.lower().strip(),)
        ).fetchone()

        if not user:
            return None

        # Eliminar tokens previos de este email
        conn.execute(
            "DELETE FROM password_reset_tokens WHERE email = ?",
            (email.lower().strip(),)
        )

        # Generar codigo de 6 digitos
        code = "".join(secrets.choice(string.digits) for _ in range(6))
        expires_at = (datetime.now() + timedelta(minutes=15)).isoformat()

        conn.execute(
            "INSERT INTO password_reset_tokens (email, code, expires_at) VALUES (?, ?, ?)",
            (email.lower().strip(), code, expires_at)
        )
        return code


def consume_reset_token(email: str, code: str, new_password: str) -> bool:
    """
    Verifica el codigo de recuperacion y, si es valido, resetea la contraseña.
    Retorna True si exitoso, False si el codigo es incorrecto o expiró.
    """
    with get_db() as conn:
        token = conn.execute(
            """SELECT id FROM password_reset_tokens
               WHERE email = ? AND code = ? AND expires_at > ?""",
            (email.lower().strip(), code, datetime.now().isoformat())
        ).fetchone()

        if not token:
            return False

        conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ? AND is_admin = 0",
            (hash_password(new_password), email.lower().strip())
        )
        conn.execute(
            "DELETE FROM password_reset_tokens WHERE email = ?",
            (email.lower().strip(),)
        )
        return True


def get_display_name_by_email(email: str) -> str:
    """Retorna el nombre de un usuario por email, o cadena vacia si no existe."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT display_name FROM users WHERE email = ?",
            (email.lower().strip(),)
        ).fetchone()
        return row["display_name"] if row else ""


# ============================================================
# RESULTADOS OFICIALES (ADMIN)
# ============================================================
def set_official_result(match_id: int, home_goals: int, away_goals: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO official_results (match_id, home_goals, away_goals, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(match_id) DO UPDATE SET
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals,
                updated_at = CURRENT_TIMESTAMP
        """, (match_id, home_goals, away_goals))


def delete_official_result(match_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM official_results WHERE match_id = ?", (match_id,))


def get_official_results(group: str = None) -> list[dict]:
    with get_db() as conn:
        if group:
            rows = conn.execute("""
                SELECT gm.id, gm.group_name, gm.match_order, gm.team_home, gm.team_away,
                       orr.home_goals, orr.away_goals
                FROM group_matches gm
                LEFT JOIN official_results orr ON gm.id = orr.match_id
                WHERE gm.group_name = ?
                ORDER BY gm.match_order
            """, (group,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT gm.id, gm.group_name, gm.match_order, gm.team_home, gm.team_away,
                       orr.home_goals, orr.away_goals
                FROM group_matches gm
                LEFT JOIN official_results orr ON gm.id = orr.match_id
                ORDER BY gm.group_name, gm.match_order
            """).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# PRONOSTICOS DE JUGADORES
# ============================================================
def set_prediction(user_id: int, match_id: int, home_goals: int, away_goals: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO predictions (user_id, match_id, home_goals, away_goals, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, match_id) DO UPDATE SET
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, match_id, home_goals, away_goals))


def get_predictions(user_id: int, group: str = None) -> list[dict]:
    with get_db() as conn:
        if group:
            rows = conn.execute("""
                SELECT gm.id as match_id, gm.group_name, gm.match_order,
                       gm.team_home, gm.team_away,
                       p.home_goals, p.away_goals
                FROM group_matches gm
                LEFT JOIN predictions p ON gm.id = p.match_id AND p.user_id = ?
                WHERE gm.group_name = ?
                ORDER BY gm.match_order
            """, (user_id, group)).fetchall()
        else:
            rows = conn.execute("""
                SELECT gm.id as match_id, gm.group_name, gm.match_order,
                       gm.team_home, gm.team_away,
                       p.home_goals, p.away_goals
                FROM group_matches gm
                LEFT JOIN predictions p ON gm.id = p.match_id AND p.user_id = ?
                ORDER BY gm.group_name, gm.match_order
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


def set_final_predictions(user_id: int, champion: str, finalist: str,
                          semi1: str, semi2: str, scorer1: str, scorer2: str):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO final_predictions (user_id, champion, finalist, semi1, semi2, scorer1, scorer2, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                champion = excluded.champion,
                finalist = excluded.finalist,
                semi1 = excluded.semi1,
                semi2 = excluded.semi2,
                scorer1 = excluded.scorer1,
                scorer2 = excluded.scorer2,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, champion, finalist, semi1, semi2, scorer1, scorer2))


def get_final_predictions(user_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM final_predictions WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_predictions_for_match(match_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT u.display_name, p.home_goals, p.away_goals
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            WHERE p.match_id = ?
            ORDER BY u.display_name
        """, (match_id,)).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# CLASIFICADOS DE GRUPO (predicciones de jugadores)
# ============================================================
def set_group_classification_prediction(user_id: int, group_name: str,
                                        first_place: str, second_place: str):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO group_classification_predictions
                (user_id, group_name, first_place, second_place, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, group_name) DO UPDATE SET
                first_place = excluded.first_place,
                second_place = excluded.second_place,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, group_name, first_place.upper().strip(), second_place.upper().strip()))


def get_group_classification_predictions(user_id: int, group_name: str = None) -> list[dict]:
    with get_db() as conn:
        if group_name:
            rows = conn.execute(
                "SELECT * FROM group_classification_predictions WHERE user_id = ? AND group_name = ?",
                (user_id, group_name)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM group_classification_predictions WHERE user_id = ? ORDER BY group_name",
                (user_id,)
            ).fetchall()
        return [dict(r) for r in rows]


def set_best_third_prediction(user_id: int, thirds: dict):
    with get_db() as conn:
        conn.execute("DELETE FROM best_third_predictions WHERE user_id = ?", (user_id,))
        for group, team in thirds.items():
            conn.execute(
                "INSERT INTO best_third_predictions (user_id, group_name, team_name, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (user_id, group.upper().strip(), team.upper().strip())
            )


def get_best_third_predictions(user_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT group_name, team_name FROM best_third_predictions WHERE user_id = ? ORDER BY group_name",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# CLASIFICADOS OFICIALES (admin)
# ============================================================
def set_official_group_classification(group_name: str, first_place: str,
                                      second_place: str, third_place: str = None):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO official_group_classification (group_name, first_place, second_place, third_place, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(group_name) DO UPDATE SET
                first_place = excluded.first_place,
                second_place = excluded.second_place,
                third_place = excluded.third_place,
                updated_at = CURRENT_TIMESTAMP
        """, (group_name, first_place.upper().strip(), second_place.upper().strip(),
              third_place.upper().strip() if third_place else None))


def get_official_group_classifications() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM official_group_classification ORDER BY group_name"
        ).fetchall()
        return [dict(r) for r in rows]


def set_official_best_thirds(groups: list[str]):
    with get_db() as conn:
        conn.execute("DELETE FROM official_best_thirds")
        for g in groups:
            conn.execute(
                "INSERT INTO official_best_thirds (group_name, updated_at) VALUES (?, CURRENT_TIMESTAMP)",
                (g.upper().strip(),)
            )


def get_official_best_thirds() -> list[str]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT group_name FROM official_best_thirds ORDER BY group_name"
        ).fetchall()
        return [r["group_name"] for r in rows]


# ============================================================
# PLAYOFFS
# ============================================================
def create_playoff_match(round_name: str, position: int, team_home: str,
                         team_away: str, bracket_side: str = "L") -> int:
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO playoff_matches (round_name, position, team_home, team_away, bracket_side)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(round_name, position, bracket_side) DO UPDATE SET
                team_home = excluded.team_home,
                team_away = excluded.team_away
        """, (round_name, position, team_home, team_away, bracket_side))
        return cursor.lastrowid


def set_playoff_result(match_id: int, home_goals: int, away_goals: int,
                       advancing_team: str, mvp_player: str = None):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO playoff_results (match_id, home_goals, away_goals, advancing_team, mvp_player, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(match_id) DO UPDATE SET
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals,
                advancing_team = excluded.advancing_team,
                mvp_player = excluded.mvp_player,
                updated_at = CURRENT_TIMESTAMP
        """, (match_id, home_goals, away_goals, advancing_team, mvp_player))


def delete_playoff_result(match_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM playoff_results WHERE match_id = ?", (match_id,))


def get_playoff_matches(round_name: str = None) -> list[dict]:
    with get_db() as conn:
        if round_name:
            rows = conn.execute("""
                SELECT pm.*, pr.home_goals as result_home, pr.away_goals as result_away,
                       pr.advancing_team, pr.mvp_player
                FROM playoff_matches pm
                LEFT JOIN playoff_results pr ON pm.id = pr.match_id
                WHERE pm.round_name = ?
                ORDER BY pm.bracket_side, pm.position
            """, (round_name,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT pm.*, pr.home_goals as result_home, pr.away_goals as result_away,
                       pr.advancing_team, pr.mvp_player
                FROM playoff_matches pm
                LEFT JOIN playoff_results pr ON pm.id = pr.match_id
                ORDER BY pm.round_name, pm.bracket_side, pm.position
            """).fetchall()
        return [dict(r) for r in rows]


def set_playoff_prediction(user_id: int, match_id: int, home_goals: int,
                           away_goals: int, advancing_team: str, mvp_player: str = None):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO playoff_predictions (user_id, match_id, home_goals, away_goals, advancing_team, mvp_player, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, match_id) DO UPDATE SET
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals,
                advancing_team = excluded.advancing_team,
                mvp_player = excluded.mvp_player,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, match_id, home_goals, away_goals, advancing_team, mvp_player))


def get_playoff_predictions(user_id: int, round_name: str = None) -> list[dict]:
    with get_db() as conn:
        if round_name:
            rows = conn.execute("""
                SELECT pm.id as match_id, pm.round_name, pm.position, pm.team_home, pm.team_away,
                       pp.home_goals, pp.away_goals, pp.advancing_team, pp.mvp_player
                FROM playoff_matches pm
                LEFT JOIN playoff_predictions pp ON pm.id = pp.match_id AND pp.user_id = ?
                WHERE pm.round_name = ?
                ORDER BY pm.bracket_side, pm.position
            """, (user_id, round_name)).fetchall()
        else:
            rows = conn.execute("""
                SELECT pm.id as match_id, pm.round_name, pm.position, pm.team_home, pm.team_away,
                       pp.home_goals, pp.away_goals, pp.advancing_team, pp.mvp_player
                FROM playoff_matches pm
                LEFT JOIN playoff_predictions pp ON pm.id = pp.match_id AND pp.user_id = ?
                ORDER BY pm.round_name, pm.bracket_side, pm.position
            """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# GOLEADORES OFICIALES
# ============================================================
def set_scorer_standing(player_name: str, goals: int, rank: int):
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM scorer_standings WHERE player_name = ?", (player_name,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE scorer_standings SET goals = ?, rank = ?, updated_at = CURRENT_TIMESTAMP WHERE player_name = ?",
                (goals, rank, player_name)
            )
        else:
            conn.execute(
                "INSERT INTO scorer_standings (player_name, goals, rank) VALUES (?, ?, ?)",
                (player_name, goals, rank)
            )


def get_scorer_standings() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM scorer_standings ORDER BY goals DESC, player_name"
        ).fetchall()
        return [dict(r) for r in rows]


# ============================================================
# TARJETAS
# ============================================================
def set_cards(group_name: str, team_name: str, red_cards: int, yellow_cards: int):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO cards (group_name, team_name, red_cards, yellow_cards)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(group_name, team_name) DO UPDATE SET
                red_cards = excluded.red_cards,
                yellow_cards = excluded.yellow_cards
        """, (group_name, team_name, red_cards, yellow_cards))


def get_cards(group_name: str = None) -> list[dict]:
    with get_db() as conn:
        if group_name:
            rows = conn.execute(
                "SELECT * FROM cards WHERE group_name = ? ORDER BY team_name", (group_name,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM cards ORDER BY group_name, team_name").fetchall()
        return [dict(r) for r in rows]


# ============================================================
# INFO DEL TORNEO
# ============================================================
def set_tournament_info(key: str, value: str):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO tournament_info (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))


def get_tournament_info(key: str) -> str | None:
    with get_db() as conn:
        row = conn.execute("SELECT value FROM tournament_info WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None


# ============================================================
# LEADERBOARD
# ============================================================
def get_leaderboard_data() -> list[dict]:
    """Calcula el leaderboard completo con puntaje desglosado."""
    from scoring import (
        score_group_match, score_group_classification,
        score_long_term_predictions, score_scorers,
        score_playoff_match, calculate_group_standings
    )
    from data import GROUPS

    users = get_all_users()
    official = get_official_results()
    scorer_standings = get_scorer_standings()
    official_lookup = {r["id"]: r for r in official}

    real_champion = get_tournament_info("champion")
    real_finalist = get_tournament_info("finalist")
    real_semi1 = get_tournament_info("semi1")
    real_semi2 = get_tournament_info("semi2")

    official_cls = get_official_group_classifications()
    official_cls_map = {c["group_name"]: c for c in official_cls}
    official_thirds = set(get_official_best_thirds())

    leaderboard = []

    for user in users:
        uid = user["id"]
        breakdown = {
            "grupos_partidos": 0,
            "grupos_clasificados": 0,
            "largo_plazo": 0,
            "goleadores": 0,
            "playoffs": 0,
        }

        # Puntos por partidos de grupo
        predictions = get_predictions(uid)
        for pred in predictions:
            off = official_lookup.get(pred["match_id"])
            if off and off["home_goals"] is not None and pred["home_goals"] is not None:
                result = score_group_match(
                    pred["home_goals"], pred["away_goals"],
                    off["home_goals"], off["away_goals"]
                )
                breakdown["grupos_partidos"] += result["points"]

        # Puntos por clasificados
        final_preds = get_final_predictions(uid)
        user_cls_preds = get_group_classification_predictions(uid)
        user_cls_map = {c["group_name"]: c for c in user_cls_preds}
        user_thirds = get_best_third_predictions(uid)
        user_thirds_map = {t["group_name"]: t["team_name"] for t in user_thirds}

        for group_name, off_cls in official_cls_map.items():
            user_cls = user_cls_map.get(group_name)
            if user_cls:
                cls_result = score_group_classification(
                    user_cls["first_place"], user_cls["second_place"],
                    off_cls["first_place"], off_cls["second_place"],
                    pred_3rd=user_thirds_map.get(group_name),
                    real_3rd=off_cls.get("third_place"),
                    real_third_qualifies=group_name in official_thirds,
                )
                breakdown["grupos_clasificados"] += cls_result["points"]

        # Largo plazo
        if final_preds and real_champion:
            lt_result = score_long_term_predictions(
                final_preds.get("champion", ""),
                final_preds.get("finalist", ""),
                final_preds.get("semi1", ""),
                final_preds.get("semi2", ""),
                real_champion, real_finalist, real_semi1, real_semi2
            )
            breakdown["largo_plazo"] = lt_result["points"]

        # Goleadores
        if final_preds and scorer_standings:
            sc_result = score_scorers(
                final_preds.get("scorer1", ""),
                final_preds.get("scorer2", ""),
                scorer_standings
            )
            breakdown["goleadores"] = sc_result["points"]

        # Playoffs
        playoff_preds = get_playoff_predictions(uid)
        playoff_matches_data = get_playoff_matches()
        playoff_lookup = {m["id"]: m for m in playoff_matches_data}

        for pp in playoff_preds:
            pm = playoff_lookup.get(pp["match_id"])
            if pm and pm.get("result_home") is not None and pp["home_goals"] is not None:
                is_final = pm["round_name"] == "final"
                po_result = score_playoff_match(
                    pp["home_goals"], pp["away_goals"], pp.get("advancing_team"),
                    pm["result_home"], pm["result_away"], pm.get("advancing_team"),
                    is_final=is_final
                )
                breakdown["playoffs"] += po_result["points"]

        total_points = sum(breakdown.values())
        leaderboard.append({
            "position": 0,
            "display_name": user["display_name"],
            "user_id": uid,
            "total": total_points,
            **breakdown,
            "champion": final_preds.get("champion", "-") if final_preds else "-",
            "scorers": f"{final_preds.get('scorer1', '-')} / {final_preds.get('scorer2', '-')}" if final_preds else "- / -",
        })

    leaderboard.sort(key=lambda x: x["total"], reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["position"] = i + 1

    return leaderboard

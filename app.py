"""
app.py - Prode Mundial 2026
Aplicacion web con Streamlit para el juego de predicciones del Mundial.
"""

import re
import streamlit as st
import pandas as pd
import db
import email_utils
import streamlit.components.v1 as components
from colors import team_chip_html, match_card_html, get_team_color
from data import GROUPS, GROUP_MATCHES, ALL_TEAMS, PLAYOFF_ROUNDS, REGISTERED_PLAYERS, \
    TOURNAMENT_PHASES, VENUES, WORLD_CUP_START_UTC, WORLD_CUP_START_LABEL, MATCH_SCHEDULE
from scoring import (
    score_group_match, score_group_classification,
    score_long_term_predictions, score_scorers,
    score_playoff_match, score_final_mvp,
    calculate_group_standings
)

# ============================================================
# CONFIGURACION
# ============================================================
st.set_page_config(
    page_title="Prode Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
    /* Header */
    .main-header {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 2rem;
        background: linear-gradient(90deg, #f1c40f, #e74c3c, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Cards de stats */
    .stat-card {
        background: #1c2333;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2c3e50;
    }
    .stat-card .number {
        font-size: 2rem;
        font-weight: bold;
        color: #f1c40f;
    }
    .stat-card .label {
        font-size: 0.85rem;
        color: #95a5a6;
    }

    /* Tabla leaderboard */
    .leaderboard-row {
        display: flex;
        align-items: center;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        background: #1c2333;
    }
    .leaderboard-row.top1 { border-left: 4px solid #f1c40f; }
    .leaderboard-row.top2 { border-left: 4px solid #95a5a6; }
    .leaderboard-row.top3 { border-left: 4px solid #cd7f32; }

    /* Partido card */
    .match-card {
        background: #1c2333;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #2c3e50;
    }

    /* Resultado tag */
    .result-pleno { color: #2ecc71; font-weight: bold; }
    .result-partial { color: #f1c40f; font-weight: bold; }
    .result-wrong { color: #e74c3c; }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.5rem; }
        .stat-card .number { font-size: 1.5rem; }
    }

    /* Ocultar hamburger y footer en deploy */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar mejorado */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar DB
db.init_db()


# ============================================================
# SESION / AUTH
# ============================================================
def _is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def init_session():
    defaults = {
        "user": None,
        "page": "login",
        "reset_email": "",
        "reset_step": "email",  # "email" | "code"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


def do_login(email, password):
    user = db.authenticate_user(email, password)
    if user:
        st.session_state.user = user
        st.session_state.page = "leaderboard"
        return True
    return False


def do_logout():
    st.session_state.user = None
    st.session_state.page = "login"
    st.session_state.reset_step = "email"
    st.session_state.reset_email = ""


def do_register(email, display_name, password):
    if not _is_valid_email(email):
        return False, "El email no tiene un formato valido"
    if db.user_exists(email):
        return False, "Ya existe una cuenta con ese email"
    try:
        db.create_user(email, display_name, password)
        return True, "Cuenta creada! Ya podes iniciar sesion."
    except Exception as e:
        return False, str(e)


# ============================================================
# PAGINA: LOGIN
# ============================================================
def page_login():
    st.markdown('<div class="main-header"><h1>⚽ Prode Mundial 2026</h1></div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["Iniciar Sesion", "Registrarse"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                if submit:
                    if not email or not password:
                        st.error("Completa todos los campos")
                    elif do_login(email, password):
                        st.rerun()
                    else:
                        st.error("Email o contraseña incorrectos")

            st.markdown("")
            if st.button("¿Olvidaste tu contraseña?", use_container_width=True, type="secondary"):
                st.session_state.page = "forgot_password"
                st.session_state.reset_step = "email"
                st.session_state.reset_email = ""
                st.rerun()

        with tab_register:
            with st.form("register_form"):
                new_email = st.text_input("Tu email")
                new_name = st.text_input("Nombre completo (como aparecera en el ranking)")
                new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
                new_pass2 = st.text_input("Repetir contraseña", type="password")
                register = st.form_submit_button("Crear cuenta", use_container_width=True)
                if register:
                    if not new_email or not new_name or not new_pass:
                        st.error("Completa todos los campos")
                    elif not _is_valid_email(new_email):
                        st.error("El email no tiene un formato valido")
                    elif new_pass != new_pass2:
                        st.error("Las contraseñas no coinciden")
                    elif len(new_pass) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres")
                    else:
                        ok, msg = do_register(new_email, new_name, new_pass)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)


# ============================================================
# PAGINA: RECUPERAR CONTRASEÑA
# ============================================================
def page_forgot_password():
    st.markdown('<div class="main-header"><h1>🔑 Recuperar Contraseña</h1></div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        if st.session_state.reset_step == "email":
            st.markdown("### Paso 1: Ingresa tu email")
            st.markdown("Te vamos a enviar un codigo de 6 digitos para crear una nueva contraseña.")
            st.markdown("")

            with st.form("forgot_form"):
                email_input = st.text_input("Tu email registrado")
                send = st.form_submit_button("Enviar codigo", use_container_width=True)

                if send:
                    if not email_input:
                        st.error("Ingresa tu email")
                    elif not _is_valid_email(email_input):
                        st.error("El email no tiene un formato valido")
                    else:
                        display_name = db.get_display_name_by_email(email_input)
                        code = db.create_reset_token(email_input)

                        if code is None:
                            # Por seguridad no revelamos si el email existe o no
                            st.success(
                                "Si ese email esta registrado, vas a recibir un codigo en unos segundos. "
                                "Revisa tu casilla (y la carpeta de spam)."
                            )
                        else:
                            ok, err = email_utils.send_reset_email(
                                email_input, code, display_name or "Usuario"
                            )
                            if ok:
                                st.session_state.reset_email = email_input.lower().strip()
                                st.session_state.reset_step = "code"
                                st.success("Codigo enviado! Revisa tu email.")
                                st.rerun()
                            else:
                                st.error(f"No se pudo enviar el email. {err}")

            st.markdown("")
            if st.button("← Volver al login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

        elif st.session_state.reset_step == "code":
            st.markdown("### Paso 2: Ingresa el codigo y tu nueva contraseña")
            email_display = st.session_state.reset_email
            st.info(f"Codigo enviado a **{email_display}**. Expira en 15 minutos.")
            st.markdown("")

            with st.form("reset_form"):
                code_input = st.text_input("Codigo de 6 digitos", max_chars=6,
                                           placeholder="123456")
                new_pass = st.text_input("Nueva contraseña", type="password")
                new_pass2 = st.text_input("Repetir nueva contraseña", type="password")
                reset = st.form_submit_button("Cambiar contraseña", use_container_width=True)

                if reset:
                    if not code_input or not new_pass or not new_pass2:
                        st.error("Completa todos los campos")
                    elif len(new_pass) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres")
                    elif new_pass != new_pass2:
                        st.error("Las contraseñas no coinciden")
                    else:
                        ok = db.consume_reset_token(email_display, code_input.strip(), new_pass)
                        if ok:
                            st.success("Contraseña cambiada con exito! Ya podes iniciar sesion.")
                            st.session_state.reset_step = "email"
                            st.session_state.reset_email = ""
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error("Codigo incorrecto o expirado. Intenta pedir un nuevo codigo.")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Cambiar email", use_container_width=True):
                    st.session_state.reset_step = "email"
                    st.rerun()
            with col_b:
                if st.button("← Volver al login", use_container_width=True):
                    st.session_state.page = "login"
                    st.session_state.reset_step = "email"
                    st.rerun()


# ============================================================
# PAGINA: PROXIMOS PARTIDOS + COUNTDOWN
# ============================================================
def page_upcoming_matches():
    st.markdown(
        '<div class="main-header"><h1>📅 Próximos Partidos</h1></div>',
        unsafe_allow_html=True,
    )

    # ── Countdown en vivo (iframe con JavaScript real) ──────
    countdown_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin:0; padding:0;
    background:linear-gradient(135deg,#0D1B2A 0%,#1A2744 100%);
    font-family:'Segoe UI',Arial,sans-serif;
    border-radius:16px;
    overflow:hidden;
  }}
  .wrap {{
    padding:1.4rem 1rem 1.2rem;
    text-align:center;
  }}
  .label {{
    font-size:0.7rem; color:#8899AA;
    letter-spacing:4px; text-transform:uppercase;
    margin-bottom:1rem;
  }}
  .units {{
    display:flex; justify-content:center;
    align-items:flex-start; gap:4px; flex-wrap:wrap;
  }}
  .unit {{ text-align:center; min-width:64px; }}
  .num {{
    font-size:3rem; font-weight:900; line-height:1;
    font-variant-numeric:tabular-nums;
  }}
  .sep {{
    font-size:2.6rem; font-weight:900;
    color:#334; padding-top:1px; user-select:none;
  }}
  .unit-label {{
    font-size:0.55rem; color:#556677;
    letter-spacing:3px; margin-top:4px;
  }}
  .sub {{
    margin-top:1rem;
    font-size:0.7rem; color:#445566;
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="label">⚽ &nbsp; Mundial 2026 arranca en</div>
  <div class="units">
    <div class="unit">
      <div class="num" id="d" style="color:#F1C40F">000</div>
      <div class="unit-label">DÍAS</div>
    </div>
    <div class="sep">:</div>
    <div class="unit">
      <div class="num" id="h" style="color:#E74C3C">00</div>
      <div class="unit-label">HORAS</div>
    </div>
    <div class="sep">:</div>
    <div class="unit">
      <div class="num" id="m" style="color:#3498DB">00</div>
      <div class="unit-label">MIN</div>
    </div>
    <div class="sep">:</div>
    <div class="unit">
      <div class="num" id="s" style="color:#2ECC71">00</div>
      <div class="unit-label">SEG</div>
    </div>
  </div>
  <div class="sub">📅 &nbsp; {WORLD_CUP_START_LABEL}</div>
</div>
<script>
  var t = new Date('{WORLD_CUP_START_UTC}');
  function p(n,w){{return String(n).padStart(w||2,'0');}}
  function tick(){{
    var diff = t - new Date();
    if(diff<=0){{diff=0;}}
    document.getElementById('d').textContent=p(Math.floor(diff/86400000),3);
    document.getElementById('h').textContent=p(Math.floor((diff%86400000)/3600000));
    document.getElementById('m').textContent=p(Math.floor((diff%3600000)/60000));
    document.getElementById('s').textContent=p(Math.floor((diff%60000)/1000));
  }}
  setInterval(tick,1000); tick();
</script>
</body>
</html>
"""
    components.html(countdown_html, height=195)

    st.markdown("---")

    # ── Tabs: Calendario | Partidos | Sedes ─────────────────
    tab_cal, tab_matches, tab_venues = st.tabs(
        ["🗓️ Calendario", "⚽ Partidos por grupo", "🏟️ Sedes"]
    )

    # ── TAB 1: Fases del torneo ──────────────────────────────
    with tab_cal:
        st.markdown("#### Fases del torneo")
        for p in TOURNAMENT_PHASES:
            is_final = p["phase"] == "GRAN FINAL"
            date_range = (
                p["start"] if p["start"] == p["end"]
                else f"{p['start']} – {p['end']}"
            )
            col_name, col_date = st.columns([3, 1])
            with col_name:
                weight = "**" if is_final else ""
                st.markdown(
                    f"{p['emoji']} &nbsp; {weight}{p['phase']}{weight}"
                )
            with col_date:
                st.markdown(
                    f"<span style='color:{p['color']};font-weight:700;'>"
                    f"{date_range} 2026</span>",
                    unsafe_allow_html=True,
                )

    # ── TAB 2: Partidos por grupo con horario ARG ────────────
    with tab_matches:
        st.markdown("#### Horarios en hora Argentina (UTC-3)")
        group_sel = st.selectbox(
            "Seleccionar grupo",
            sorted(GROUPS.keys()),
            format_func=lambda g: f"Grupo {g} — {', '.join(GROUPS[g])}",
            key="upcoming_group_sel",
        )

        teams = GROUPS[group_sel]
        # Mostrar el banner de equipos del grupo con colores
        chips = " &nbsp; ".join(team_chip_html(t, size="small") for t in teams)
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("")

        from data import GROUP_MATCHES as GM
        group_matches_list = [(g, o, h, a) for g, o, h, a in GM if g == group_sel]

        db_schedule = db.get_schedule_as_dict()

        for g, order, home, away in group_matches_list:
            sched = db_schedule.get((g, order)) or MATCH_SCHEDULE.get((g, order), None)
            if isinstance(sched, tuple) and len(sched) == 4:
                date_s, time_s, stadium_s, city_s = sched
            else:
                date_s, time_s, stadium_s, city_s = "Por confirmar", "", "", ""

            official = db.get_official_results(g)
            result = next((r for r in official if r["match_order"] == order), None)
            sh = result["home_goals"] if result and result["home_goals"] is not None else None
            sa = result["away_goals"] if result and result["home_goals"] is not None else None

            st.markdown(
                match_card_html(
                    home, away,
                    date_str=date_s,
                    time_str=time_s,
                    venue=stadium_s,
                    city=city_s,
                    score_home=sh,
                    score_away=sa,
                ),
                unsafe_allow_html=True,
            )

    # ── TAB 3: Sedes con imagenes ────────────────────────────
    with tab_venues:
        country_colors = {"México": "#006847", "Canadá": "#D80621", "USA": "#002868"}
        by_country = {}
        for v in VENUES:
            by_country.setdefault(v["country"], []).append(v)

        for country, vlist in by_country.items():
            color = country_colors.get(country, "#555")
            st.markdown(
                f"<span style='color:{color};font-weight:800;font-size:1rem;'>"
                f"{vlist[0]['flag']} {country}</span>",
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            for i, v in enumerate(vlist):
                with cols[i % 3]:
                    try:
                        st.image(v["img"], use_container_width=True)
                    except Exception:
                        st.markdown("🏟️")
                    cap = f"{v['capacity']:,}".replace(",", ".")
                    st.markdown(
                        f"**{v['name']}**  \n"
                        f"📍 {v['city']}  \n"
                        f"👥 {cap} esp.",
                        unsafe_allow_html=False,
                    )
            st.markdown("---")


# ============================================================
# SIDEBAR (navegacion)
# ============================================================
def render_sidebar():
    user = st.session_state.user
    is_admin = user.get("is_admin")
    with st.sidebar:
        st.markdown(f"### Hola, {user['display_name']}!")
        st.markdown("---")

        if st.button("📊 Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()

        if st.button("📅 Próximos Partidos", use_container_width=True):
            st.session_state.page = "upcoming"
            st.rerun()

        if st.button("📋 Resultados Oficiales", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()

        if st.button("🥊 Playoffs", use_container_width=True):
            st.session_state.page = "playoffs"
            st.rerun()

        # Solo jugadores pueden cargar pronosticos
        if not is_admin:
            st.markdown("---")
            st.markdown("### Mis Pronosticos")

            if st.button("⚽ Fase de Grupos", use_container_width=True):
                st.session_state.page = "predictions"
                st.rerun()

            if st.button("🏆 Predicciones Finales", use_container_width=True):
                st.session_state.page = "final_predictions"
                st.rerun()

        # Solo admin ve las paginas de admin
        if is_admin:
            st.markdown("---")
            st.markdown("### Admin")
            if st.button("⚙️ Cargar Resultados", use_container_width=True):
                st.session_state.page = "admin_results"
                st.rerun()
            if st.button("🏟️ Armar Playoffs", use_container_width=True):
                st.session_state.page = "admin_playoffs"
                st.rerun()
            if st.button("👟 Goleadores", use_container_width=True):
                st.session_state.page = "admin_scorers"
                st.rerun()
            if st.button("🕐 Horarios", use_container_width=True):
                st.session_state.page = "admin_schedule"
                st.rerun()
            if st.button("🏆 Info Torneo", use_container_width=True):
                st.session_state.page = "admin_tournament"
                st.rerun()
            if st.button("📊 Clasificados Oficiales", use_container_width=True):
                st.session_state.page = "admin_classification"
                st.rerun()
            if st.button("👥 Gestionar Jugadores", use_container_width=True):
                st.session_state.page = "admin_users"
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar Sesion", use_container_width=True):
            do_logout()
            st.rerun()


# ============================================================
# PAGINA: LEADERBOARD
# ============================================================
def page_leaderboard():
    st.markdown('<div class="main-header"><h1>📊 Leaderboard</h1></div>', unsafe_allow_html=True)

    leaderboard = db.get_leaderboard_data()

    if not leaderboard:
        st.info("No hay datos todavia. Esperando que los jugadores carguen pronosticos.")
        return

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <div class="number">{len(leaderboard)}</div>
            <div class="label">Jugadores</div>
        </div>""", unsafe_allow_html=True)

    official_results = db.get_official_results()
    played = sum(1 for r in official_results if r["home_goals"] is not None)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <div class="number">{played}/72</div>
            <div class="label">Partidos jugados</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        leader = leaderboard[0] if leaderboard else {"display_name": "-", "total": 0}
        st.markdown(f"""<div class="stat-card">
            <div class="number">{leader["total"]}</div>
            <div class="label">Lider: {leader["display_name"]}</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        avg = sum(e["total"] for e in leaderboard) / len(leaderboard) if leaderboard else 0
        st.markdown(f"""<div class="stat-card">
            <div class="number">{avg:.1f}</div>
            <div class="label">Promedio</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Tabla principal
    df = pd.DataFrame(leaderboard)
    display_cols = {
        "position": "#",
        "display_name": "Jugador",
        "total": "Total",
        "grupos_partidos": "Partidos",
        "grupos_clasificados": "Clasificados",
        "playoffs": "Playoffs",
        "largo_plazo": "Largo Plazo",
        "goleadores": "Goleadores",
        "champion": "Campeon",
    }
    df_display = df[list(display_cols.keys())].rename(columns=display_cols)

    st.dataframe(
        df_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "#": st.column_config.NumberColumn(width="small"),
            "Total": st.column_config.NumberColumn(width="small"),
            "Partidos": st.column_config.NumberColumn(width="small"),
            "Clasificados": st.column_config.NumberColumn(width="small"),
            "Playoffs": st.column_config.NumberColumn(width="small"),
            "Largo Plazo": st.column_config.NumberColumn(width="small"),
            "Goleadores": st.column_config.NumberColumn(width="small"),
        }
    )


# ============================================================
# PAGINA: MIS PRONOSTICOS (Fase de Grupos + Clasificados)
# ============================================================
def page_predictions():
    st.markdown('<div class="main-header"><h1>⚽ Mis Pronosticos - Fase de Grupos</h1></div>', unsafe_allow_html=True)

    user = st.session_state.user
    group_names = sorted(GROUPS.keys())
    selected_group = st.selectbox("Seleccionar grupo", group_names, format_func=lambda g: f"Grupo {g}")

    teams = GROUPS[selected_group]
    st.markdown(f"### Grupo {selected_group}: {', '.join(teams)}")

    # Cargar datos existentes
    predictions = db.get_predictions(user["id"], selected_group)
    official = db.get_official_results(selected_group)
    official_map = {r["id"]: r for r in official}

    existing_cls_list = db.get_group_classification_predictions(user["id"])
    cls_map = {c["group_name"]: c for c in existing_cls_list}
    existing_cls = cls_map.get(selected_group, {})

    existing_thirds_list = db.get_best_third_predictions(user["id"])
    existing_thirds_map = {t["group_name"]: t["team_name"] for t in existing_thirds_list}

    teams_list = [""] + teams

    with st.form(f"pred_group_{selected_group}"):
        # --- SECCION 1: Pronosticos de partidos ---
        st.markdown("#### Resultados de partidos")
        for pred in predictions:
            match_id = pred["match_id"]
            off = official_map.get(match_id)
            has_result = off and off["home_goals"] is not None

            col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])

            with col1:
                st.markdown(
                    team_chip_html(pred["team_home"], size="normal"),
                    unsafe_allow_html=True,
                )
            with col2:
                home_key = f"home_{match_id}"
                home_val = pred["home_goals"] if pred["home_goals"] is not None else 0
                st.number_input("", min_value=0, max_value=20, value=home_val,
                                key=home_key, label_visibility="collapsed")
            with col3:
                st.markdown("<div style='text-align:center; padding-top:0.5rem;'>vs</div>",
                            unsafe_allow_html=True)
            with col4:
                away_key = f"away_{match_id}"
                away_val = pred["away_goals"] if pred["away_goals"] is not None else 0
                st.number_input("", min_value=0, max_value=20, value=away_val,
                                key=away_key, label_visibility="collapsed")
            with col5:
                st.markdown(
                    team_chip_html(pred["team_away"], size="normal"),
                    unsafe_allow_html=True,
                )

            # Mostrar resultado oficial si existe
            if has_result:
                result = score_group_match(
                    st.session_state.get(f"home_{match_id}", 0),
                    st.session_state.get(f"away_{match_id}", 0),
                    off["home_goals"], off["away_goals"]
                )
                result_text = f"Oficial: {off['home_goals']}-{off['away_goals']}"
                pts = result["points"]
                if pts == 2:
                    st.markdown(f'<span class="result-pleno">{result_text} | Pleno! +2pts</span>',
                                unsafe_allow_html=True)
                elif pts == 1:
                    st.markdown(f'<span class="result-partial">{result_text} | Resultado +1pt</span>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="result-wrong">{result_text} | 0pts</span>',
                                unsafe_allow_html=True)

        st.markdown("---")

        # --- SECCION 2: Clasificados del grupo ---
        st.markdown("#### Clasificados del grupo")
        st.markdown(
            "*1ro y 2do exactos = 4pts | Invertidos = 3pts | "
            "Un correcto = 2pts | Uno en top 2 = 1pt*"
        )

        col1, col2 = st.columns(2)
        with col1:
            first_idx = teams_list.index(existing_cls.get("first_place", "")) if existing_cls.get("first_place") in teams_list else 0
            st.selectbox("1ro del grupo", teams_list, index=first_idx,
                         key=f"cls_1_{selected_group}",
                         format_func=lambda x: f"1ro: {x}" if x else "Elegir 1ro...")
        with col2:
            second_idx = teams_list.index(existing_cls.get("second_place", "")) if existing_cls.get("second_place") in teams_list else 0
            st.selectbox("2do del grupo", teams_list, index=second_idx,
                         key=f"cls_2_{selected_group}",
                         format_func=lambda x: f"2do: {x}" if x else "Elegir 2do...")

        # Mejor 3ro de este grupo
        st.markdown("---")
        st.markdown("#### Mejor tercero")
        st.markdown("*+1pt si acertás el equipo que sale 3ro y ese 3ro clasifica*")

        has_third = selected_group in existing_thirds_map
        st.checkbox(
            f"Creo que el 3ro del Grupo {selected_group} clasifica",
            value=has_third,
            key=f"third_{selected_group}"
        )
        third_team = existing_thirds_map.get(selected_group, "")
        t_idx = teams_list.index(third_team) if third_team in teams_list else 0
        st.selectbox("Equipo que sale 3ro", teams_list, index=t_idx,
                     key=f"third_team_{selected_group}",
                     format_func=lambda x: f"3ro: {x}" if x else "Elegir 3ro...")

        st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar Todo", use_container_width=True)
        if submitted:
            errors = []

            # Validar clasificados
            first = st.session_state.get(f"cls_1_{selected_group}", "")
            second = st.session_state.get(f"cls_2_{selected_group}", "")

            if first and second and first == second:
                errors.append("1ro y 2do no pueden ser el mismo equipo")
            if first and not second:
                errors.append("Elegiste 1ro pero falta el 2do")
            if second and not first:
                errors.append("Elegiste 2do pero falta el 1ro")

            # Validar 3ro
            is_third_checked = st.session_state.get(f"third_{selected_group}")
            third_team_val = st.session_state.get(f"third_team_{selected_group}", "")

            if is_third_checked:
                if not third_team_val:
                    errors.append("Marcaste mejor tercero pero no elegiste el equipo")
                elif third_team_val == first or third_team_val == second:
                    errors.append("El 3ro no puede ser el mismo que el 1ro o 2do")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Guardar pronosticos de partidos
                for pred in predictions:
                    mid = pred["match_id"]
                    h = st.session_state.get(f"home_{mid}", 0)
                    a = st.session_state.get(f"away_{mid}", 0)
                    db.set_prediction(user["id"], mid, h, a)

                # Guardar clasificados
                if first and second:
                    db.set_group_classification_prediction(user["id"], selected_group, first, second)

                # Guardar/actualizar mejor 3ro
                # Leer los terceros actuales y actualizar solo este grupo
                current_thirds = {t["group_name"]: t["team_name"] for t in db.get_best_third_predictions(user["id"])}
                if is_third_checked and third_team_val:
                    current_thirds[selected_group] = third_team_val
                elif selected_group in current_thirds:
                    del current_thirds[selected_group]

                if current_thirds:
                    db.set_best_third_prediction(user["id"], current_thirds)
                else:
                    # Borrar todos si no queda ninguno
                    db.set_best_third_prediction(user["id"], {})

                st.success("Pronosticos guardados!")
                st.rerun()

    # Mostrar resumen de mejores terceros seleccionados (fuera del form)
    all_thirds = db.get_best_third_predictions(user["id"])
    if all_thirds:
        st.markdown("---")
        st.markdown("#### Resumen: Mejores terceros seleccionados")
        thirds_text = ", ".join([f"**Grupo {t['group_name']}**: {t['team_name']}" for t in all_thirds])
        st.markdown(f"{thirds_text} ({len(all_thirds)}/8)")
        if len(all_thirds) != 8:
            st.warning(f"Necesitas exactamente 8 mejores terceros. Tenés {len(all_thirds)}. Recorré los otros grupos para completar.")


# ============================================================
# PAGINA: PREDICCIONES FINALES
# ============================================================
def page_final_predictions():
    st.markdown('<div class="main-header"><h1>🏆 Predicciones Finales</h1></div>', unsafe_allow_html=True)

    user = st.session_state.user
    current = db.get_final_predictions(user["id"])

    teams_list = [""] + ALL_TEAMS

    with st.form("final_preds"):
        st.markdown("### Podio")
        col1, col2 = st.columns(2)
        with col1:
            champ_idx = teams_list.index(current["champion"].upper()) if current and current.get("champion") and current["champion"].upper() in teams_list else 0
            champion = st.selectbox("Campeon", teams_list, index=champ_idx)
        with col2:
            fin_idx = teams_list.index(current["finalist"].upper()) if current and current.get("finalist") and current["finalist"].upper() in teams_list else 0
            finalist = st.selectbox("Finalista (subcampeon)", teams_list, index=fin_idx)

        col3, col4 = st.columns(2)
        with col3:
            s1_idx = teams_list.index(current["semi1"].upper()) if current and current.get("semi1") and current["semi1"].upper() in teams_list else 0
            semi1 = st.selectbox("Semifinalista 1", teams_list, index=s1_idx)
        with col4:
            s2_idx = teams_list.index(current["semi2"].upper()) if current and current.get("semi2") and current["semi2"].upper() in teams_list else 0
            semi2 = st.selectbox("Semifinalista 2", teams_list, index=s2_idx)

        st.markdown("### Goleadores")
        scorer1 = st.text_input("Goleador 1 (nombre del jugador)",
                                value=current.get("scorer1", "") if current else "")
        scorer2 = st.text_input("Goleador 2 (nombre del jugador)",
                                value=current.get("scorer2", "") if current else "")

        st.markdown("---")
        st.markdown("""
        **Sistema de puntos:**
        - Semifinalista correcto: 3pts
        - Finalista correcto: +5pts (acumulable)
        - Campeon correcto: +7pts (acumulable = 15pts total)
        - Goleador 1ro: 10pts | 2do: 5pts (max 15pts)
        """)

        submitted = st.form_submit_button("💾 Guardar Predicciones", use_container_width=True)
        if submitted:
            db.set_final_predictions(
                user["id"],
                champion or "", finalist or "",
                semi1 or "", semi2 or "",
                scorer1.strip(), scorer2.strip()
            )
            st.success("Predicciones guardadas!")
            st.rerun()


# ============================================================
# PAGINA: RESULTADOS OFICIALES (vista publica)
# ============================================================
def page_results():
    st.markdown('<div class="main-header"><h1>📋 Resultados Oficiales</h1></div>', unsafe_allow_html=True)

    group_names = sorted(GROUPS.keys())
    selected_group = st.selectbox("Grupo", group_names, format_func=lambda g: f"Grupo {g}", key="res_group")

    results = db.get_official_results(selected_group)
    st.markdown(f"### Grupo {selected_group}: {', '.join(GROUPS[selected_group])}")

    # Tabla de posiciones
    played_matches = [r for r in results if r["home_goals"] is not None]
    if played_matches:
        matches_for_standings = [
            {"team_home": r["team_home"], "team_away": r["team_away"],
             "home_goals": r["home_goals"], "away_goals": r["away_goals"]}
            for r in played_matches
        ]
        standings = calculate_group_standings(matches_for_standings)

        st.markdown("#### Tabla de Posiciones")
        df_standings = pd.DataFrame(standings)
        # Reordenar columnas: Equipo, PJ, Pts, GF, GC, DG
        df_standings = df_standings[["team", "played", "pts", "gf", "gc", "gd"]]
        df_standings.index = range(1, len(df_standings) + 1)
        df_standings.columns = ["Equipo", "PJ", "Pts", "GF", "GC", "DG"]
        st.dataframe(
            df_standings,
            use_container_width=True,
            column_config={
                "Pts": st.column_config.NumberColumn(width="small"),
                "PJ": st.column_config.NumberColumn(width="small"),
                "GF": st.column_config.NumberColumn(width="small"),
                "GC": st.column_config.NumberColumn(width="small"),
                "DG": st.column_config.NumberColumn(width="small"),
            }
        )

    st.markdown("---")

    # Cada partido con pronosticos integrados
    for r in results:
        if r["home_goals"] is not None:
            # Partido jugado - tarjeta con colores + resultado
            st.markdown(
                match_card_html(
                    r["team_home"], r["team_away"],
                    score_home=r["home_goals"], score_away=r["away_goals"],
                ),
                unsafe_allow_html=True,
            )

            all_preds = db.get_all_predictions_for_match(r["id"])
            if all_preds:
                # Ordenar: pleno primero, luego resultado, luego fallo
                scored_preds = []
                for p in all_preds:
                    result = score_group_match(
                        p["home_goals"], p["away_goals"],
                        r["home_goals"], r["away_goals"]
                    )
                    scored_preds.append({**p, "score_result": result})

                scored_preds.sort(key=lambda x: x["score_result"]["points"], reverse=True)

                cols_per_row = 3
                for i in range(0, len(scored_preds), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(scored_preds):
                            p = scored_preds[i + j]
                            pts = p["score_result"]["points"]
                            if pts == 2:
                                color = "#2ecc71"
                                icon = "🟢"
                            elif pts == 1:
                                color = "#f1c40f"
                                icon = "🟡"
                            else:
                                color = "#e74c3c"
                                icon = "🔴"

                            with col:
                                st.markdown(
                                    f'<div style="background:#1c2333;border-left:3px solid {color};'
                                    f'padding:0.5rem;border-radius:5px;margin:0.2rem 0;">'
                                    f'{icon} <b>{p["display_name"]}</b><br>'
                                    f'{p["home_goals"]} - {p["away_goals"]} '
                                    f'<span style="color:{color};font-size:0.85rem">(+{pts}pts)</span>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
            else:
                st.caption("Sin pronosticos cargados")

            st.markdown("---")
        else:
            # Partido pendiente - tarjeta sin resultado
            st.markdown(
                match_card_html(r["team_home"], r["team_away"]),
                unsafe_allow_html=True,
            )


# ============================================================
# PAGINA: PLAYOFFS (vista y predicciones)
# ============================================================
def _render_bracket_html(all_matches: list[dict]) -> str:
    """Genera HTML del bracket de playoffs."""
    rounds_order = ["16avos", "octavos", "cuartos", "semifinal", "final"]
    round_labels = {
        "16avos": "16avos", "octavos": "Octavos",
        "cuartos": "Cuartos", "semifinal": "Semis", "final": "Final"
    }

    matches_by_round = {}
    for m in all_matches:
        rn = m["round_name"]
        if rn not in matches_by_round:
            matches_by_round[rn] = []
        matches_by_round[rn].append(m)

    html = '<div style="overflow-x:auto;padding:1rem 0;">'

    for rnd in rounds_order:
        matches = matches_by_round.get(rnd, [])
        if not matches:
            continue

        html += f'<h4 style="color:#f1c40f;margin:1.5rem 0 0.5rem 0;">{round_labels.get(rnd, rnd)}</h4>'
        html += '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;">'

        for m in matches:
            th = m.get("team_home") or "?"
            ta = m.get("team_away") or "?"
            has_result = m.get("result_home") is not None

            if has_result:
                rh = m["result_home"]
                ra = m["result_away"]
                adv = m.get("advancing_team", "")
                border_color = "#2ecc71"
                th_bold = "font-weight:bold;" if th == adv else "opacity:0.5;"
                ta_bold = "font-weight:bold;" if ta == adv else "opacity:0.5;"
                score_html = f'<span style="color:#95a5a6;font-size:0.8rem;">({rh}-{ra})</span>'
            else:
                border_color = "#2c3e50"
                th_bold = ""
                ta_bold = ""
                score_html = ""

            side = m.get("bracket_side", "L")
            side_tag = f'<span style="font-size:0.65rem;color:#555;">{side}</span> '

            ch = get_team_color(th)
            ca = get_team_color(ta)
            th_chip = (
                f'<span style="background:{ch["primary"]};color:{ch["text"]};'
                f'padding:2px 8px;border-radius:5px;font-weight:800;font-size:0.78rem;'
                f'{th_bold}">{th}</span>'
            )
            ta_chip = (
                f'<span style="background:{ca["primary"]};color:{ca["text"]};'
                f'padding:2px 8px;border-radius:5px;font-weight:800;font-size:0.78rem;'
                f'{ta_bold}">{ta}</span>'
            )

            html += (
                f'<div style="background:#1c2333;border:1px solid {border_color};'
                f'border-radius:8px;padding:0.4rem 0.7rem;min-width:200px;">'
                f'{side_tag}{th_chip} <span style="color:#556677;font-size:0.75rem;">vs</span> {ta_chip} {score_html}'
                f'</div>'
            )

        html += '</div>'

    html += '</div>'
    return html


def page_playoffs():
    st.markdown('<div class="main-header"><h1>🥊 Playoffs</h1></div>', unsafe_allow_html=True)

    user = st.session_state.user

    # Mostrar bracket general
    all_matches = db.get_playoff_matches()
    if all_matches:
        st.markdown("### Cuadro de Llaves")
        bracket_html = _render_bracket_html(all_matches)
        st.markdown(bracket_html, unsafe_allow_html=True)
        st.markdown("---")
    else:
        st.info("El admin todavia no cargo los partidos de playoffs. Cuando se definan los cruces, van a aparecer aca.")

    is_admin = st.session_state.user.get("is_admin")
    if is_admin:
        return  # Admin no carga pronosticos de playoffs

    st.markdown("### Cargar Pronosticos")

    rounds = ["16avos", "octavos", "cuartos", "semifinal", "final"]
    round_labels = {
        "16avos": "16avos de Final",
        "octavos": "Octavos de Final",
        "cuartos": "Cuartos de Final",
        "semifinal": "Semifinales",
        "final": "Final",
    }

    selected_round = st.selectbox("Ronda", rounds,
                                  format_func=lambda r: round_labels.get(r, r))

    matches = db.get_playoff_matches(selected_round)

    if not matches:
        st.info("No hay partidos cargados para esta ronda todavia.")
        return

    predictions = db.get_playoff_predictions(user["id"], selected_round)
    pred_map = {p["match_id"]: p for p in predictions}

    with st.form(f"playoff_{selected_round}"):
        for m in matches:
            if not m["team_home"] or not m["team_away"]:
                st.markdown(f"*Partido pendiente (posicion {m.get('position', '?')})*")
                st.markdown("---")
                continue

            home_chip = team_chip_html(m["team_home"], size="normal")
            away_chip = team_chip_html(m["team_away"], size="normal")
            st.markdown(
                f'<div style="margin:0.5rem 0 0.3rem 0;">'
                f'{home_chip} <span style="color:#556677;font-weight:700;padding:0 0.4rem;">vs</span> {away_chip}'
                f'</div>',
                unsafe_allow_html=True,
            )

            pred = pred_map.get(m["id"], {})
            has_result = m.get("result_home") is not None

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                h_val = pred.get("home_goals", 0) or 0
                st.number_input(m["team_home"], min_value=0, max_value=20,
                                value=h_val, key=f"po_h_{m['id']}")
            with col2:
                a_val = pred.get("away_goals", 0) or 0
                st.number_input(m["team_away"], min_value=0, max_value=20,
                                value=a_val, key=f"po_a_{m['id']}")
            with col3:
                teams_in_match = [m["team_home"], m["team_away"]]
                adv_idx = teams_in_match.index(pred["advancing_team"]) if pred.get("advancing_team") in teams_in_match else 0
                st.selectbox("Avanza", teams_in_match, index=adv_idx,
                             key=f"po_adv_{m['id']}")

            if selected_round == "final":
                mvp_val = pred.get("mvp_player", "") or ""
                st.text_input("MVP de la Final", value=mvp_val, key=f"po_mvp_{m['id']}")

            if has_result:
                adv_team = m.get('advancing_team', '?')
                st.markdown(
                    f'<div style="background:#1a3a1a;border-radius:5px;padding:0.5rem;margin:0.3rem 0;">'
                    f'✅ <b>Resultado:</b> {m["result_home"]}-{m["result_away"]} | '
                    f'Avanza: <b>{adv_team}</b></div>',
                    unsafe_allow_html=True
                )

            st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar Pronosticos", use_container_width=True)
        if submitted:
            for m in matches:
                if not m["team_home"] or not m["team_away"]:
                    continue
                mid = m["id"]
                h = st.session_state.get(f"po_h_{mid}", 0)
                a = st.session_state.get(f"po_a_{mid}", 0)
                adv = st.session_state.get(f"po_adv_{mid}", "")
                mvp = st.session_state.get(f"po_mvp_{mid}", "") if selected_round == "final" else None
                db.set_playoff_prediction(user["id"], mid, h, a, adv, mvp)
            st.success("Pronosticos de playoffs guardados!")
            st.rerun()


# ============================================================
# ADMIN: CARGAR RESULTADOS DE GRUPOS
# ============================================================
def page_admin_results():
    st.markdown('<div class="main-header"><h1>⚙️ Cargar Resultados Oficiales</h1></div>', unsafe_allow_html=True)

    group_names = sorted(GROUPS.keys())
    selected_group = st.selectbox("Grupo", group_names, format_func=lambda g: f"Grupo {g}", key="admin_group")

    results = db.get_official_results(selected_group)

    with st.form(f"admin_results_{selected_group}"):
        for r in results:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])

            with col1:
                st.markdown(f"**{r['team_home']}**")
            with col2:
                h_val = r["home_goals"] if r["home_goals"] is not None else 0
                st.number_input("", min_value=0, max_value=20, value=h_val,
                                key=f"ar_h_{r['id']}", label_visibility="collapsed")
            with col3:
                st.markdown("<div style='text-align:center;padding-top:0.5rem'>-</div>",
                            unsafe_allow_html=True)
            with col4:
                a_val = r["away_goals"] if r["away_goals"] is not None else 0
                st.number_input("", min_value=0, max_value=20, value=a_val,
                                key=f"ar_a_{r['id']}", label_visibility="collapsed")
            with col5:
                st.markdown(f"**{r['team_away']}**")

            # Checkbox para marcar como jugado
            played = r["home_goals"] is not None
            st.checkbox("Partido jugado", value=played, key=f"ar_played_{r['id']}")
            st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar Resultados", use_container_width=True)
        if submitted:
            changes = 0
            for r in results:
                rid = r["id"]
                is_played = st.session_state.get(f"ar_played_{rid}")
                was_played = r["home_goals"] is not None

                if is_played:
                    h = st.session_state.get(f"ar_h_{rid}", 0)
                    a = st.session_state.get(f"ar_a_{rid}", 0)
                    db.set_official_result(rid, h, a)
                    changes += 1
                elif was_played and not is_played:
                    # Admin desmarco el partido - borrar resultado
                    db.delete_official_result(rid)
                    changes += 1

            st.success(f"Resultados actualizados! ({changes} cambios)")
            st.rerun()


# ============================================================
# ADMIN: ARMAR PLAYOFFS
# ============================================================
def page_admin_playoffs():
    st.markdown('<div class="main-header"><h1>🏟️ Armar Partidos de Playoffs</h1></div>', unsafe_allow_html=True)

    rounds = ["16avos", "octavos", "cuartos", "semifinal", "final", "tercer_puesto"]
    round_labels_admin = {
        "16avos": "16avos de Final (16 partidos)",
        "octavos": "Octavos de Final (8 partidos)",
        "cuartos": "Cuartos de Final (4 partidos)",
        "semifinal": "Semifinales (2 partidos)",
        "final": "Final (1 partido)",
        "tercer_puesto": "Tercer Puesto (1 partido)",
    }
    selected_round = st.selectbox("Ronda", rounds,
                                  format_func=lambda r: round_labels_admin.get(r, r))

    existing = db.get_playoff_matches(selected_round)

    st.markdown(f"### {selected_round.upper()}")
    st.info("Ingresá los equipos para cada partido. Para cargar resultado, primero guardá los equipos y luego expandí el resultado.")

    teams_list = [""] + ALL_TEAMS

    match_counts = {
        "16avos": 16, "octavos": 8, "cuartos": 4,
        "semifinal": 2, "final": 1, "tercer_puesto": 1
    }
    n_matches = match_counts.get(selected_round, 4)

    with st.form(f"admin_po_{selected_round}"):
        for i in range(1, n_matches + 1):
            side = "L" if i <= n_matches // 2 or n_matches <= 2 else "R"
            pos = i if i <= n_matches // 2 or n_matches <= 2 else i - n_matches // 2

            existing_match = next(
                (m for m in existing if m["position"] == pos and m["bracket_side"] == side),
                {}
            )

            side_label = "Izq" if side == "L" else "Der"
            label = f"Partido {i}" if n_matches <= 2 else f"Partido {i} ({side_label} #{pos})"
            st.markdown(f"**{label}**")

            col1, col2, col3 = st.columns([2, 0.5, 2])
            with col1:
                h_idx = teams_list.index(existing_match.get("team_home", "")) if existing_match.get("team_home") in teams_list else 0
                st.selectbox(f"Local", teams_list, index=h_idx, key=f"apo_h_{i}",
                             label_visibility="collapsed",
                             format_func=lambda x: f"Local: {x}" if x else "Seleccionar local...")
            with col2:
                st.markdown("<div style='text-align:center;padding-top:0.5rem'>vs</div>",
                            unsafe_allow_html=True)
            with col3:
                a_idx = teams_list.index(existing_match.get("team_away", "")) if existing_match.get("team_away") in teams_list else 0
                st.selectbox(f"Visitante", teams_list, index=a_idx, key=f"apo_a_{i}",
                             label_visibility="collapsed",
                             format_func=lambda x: f"Visitante: {x}" if x else "Seleccionar visitante...")

            # Resultado - siempre visible si los equipos ya existen
            if existing_match.get("id"):
                rh = existing_match.get("result_home", 0) or 0
                ra = existing_match.get("result_away", 0) or 0
                has_res = existing_match.get("result_home") is not None

                st.checkbox("Resultado cargado", value=has_res, key=f"apo_has_result_{i}")

                col_r1, col_r2, col_r3 = st.columns([1, 1, 2])
                with col_r1:
                    st.number_input(f"Goles {existing_match.get('team_home', 'Local')[:10]}",
                                    min_value=0, value=rh, key=f"apo_rh_{i}")
                with col_r2:
                    st.number_input(f"Goles {existing_match.get('team_away', 'Visit')[:10]}",
                                    min_value=0, value=ra, key=f"apo_ra_{i}")
                with col_r3:
                    match_teams = [existing_match.get("team_home", ""), existing_match.get("team_away", "")]
                    adv_val = existing_match.get("advancing_team", "")
                    adv_idx = match_teams.index(adv_val) if adv_val in match_teams else 0
                    st.selectbox("Equipo que avanza", match_teams, index=adv_idx,
                                 key=f"apo_adv_{i}")

                if selected_round == "final":
                    mvp_val = existing_match.get("mvp_player", "") or ""
                    st.text_input("MVP", value=mvp_val, key=f"apo_mvp_{i}")

            st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar Playoffs", use_container_width=True)
        if submitted:
            saved = 0
            for i in range(1, n_matches + 1):
                side = "L" if i <= n_matches // 2 or n_matches <= 2 else "R"
                pos = i if i <= n_matches // 2 or n_matches <= 2 else i - n_matches // 2

                th = st.session_state.get(f"apo_h_{i}", "")
                ta = st.session_state.get(f"apo_a_{i}", "")

                if th and ta:
                    db.create_playoff_match(selected_round, pos, th, ta, side)
                    saved += 1

                    # Guardar o borrar resultado
                    existing_match = next(
                        (m for m in existing if m["position"] == pos and m["bracket_side"] == side),
                        {}
                    )
                    if existing_match.get("id"):
                        if st.session_state.get(f"apo_has_result_{i}"):
                            rh = st.session_state.get(f"apo_rh_{i}", 0)
                            ra = st.session_state.get(f"apo_ra_{i}", 0)
                            adv = st.session_state.get(f"apo_adv_{i}", th)
                            mvp = st.session_state.get(f"apo_mvp_{i}", "") if selected_round == "final" else None
                            db.set_playoff_result(existing_match["id"], rh, ra, adv, mvp)
                        elif existing_match.get("result_home") is not None:
                            # Desmarcar resultado
                            db.delete_playoff_result(existing_match["id"])

            st.success(f"Playoffs guardados! ({saved} partidos)")
            st.rerun()


# ============================================================
# ADMIN: GOLEADORES
# ============================================================
def page_admin_scorers():
    st.markdown('<div class="main-header"><h1>👟 Tabla de Goleadores</h1></div>', unsafe_allow_html=True)

    current = db.get_scorer_standings()

    st.markdown("### Goleadores actuales")
    if current:
        for s in current:
            st.markdown(f"**{s.get('rank', '-')}.** {s['player_name']} - {s['goals']} goles")

    st.markdown("---")
    st.markdown("### Agregar/Actualizar goleador")

    with st.form("scorer_form"):
        name = st.text_input("Nombre del jugador")
        col1, col2 = st.columns(2)
        with col1:
            goals = st.number_input("Goles", min_value=0, max_value=30, value=0)
        with col2:
            rank = st.number_input("Posicion", min_value=1, max_value=50, value=1)

        submitted = st.form_submit_button("💾 Guardar", use_container_width=True)
        if submitted and name:
            db.set_scorer_standing(name.strip(), goals, rank)
            st.success(f"Goleador {name} actualizado!")
            st.rerun()


# ============================================================
# ADMIN: HORARIOS DE PARTIDOS
# ============================================================
def page_admin_schedule():
    st.markdown('<div class="main-header"><h1>🕐 Horarios de Partidos</h1></div>', unsafe_allow_html=True)
    st.markdown("Ingresá los horarios en **hora Argentina (UTC-3)**. Estos reemplazan los horarios provisorios.")

    group_names = sorted(GROUPS.keys())
    selected_group = st.selectbox("Grupo", group_names, format_func=lambda g: f"Grupo {g}", key="sched_group")

    from data import GROUP_MATCHES as GM
    group_matches_list = [(g, o, h, a) for g, o, h, a in GM if g == selected_group]

    existing = {r["match_order"]: r for r in db.get_match_schedule(selected_group)}

    venues_list = [""] + [v["name"] for v in VENUES]
    cities_list = [""] + [v["city"] for v in VENUES]

    with st.form(f"schedule_{selected_group}"):
        for g, order, home, away in group_matches_list:
            ex = existing.get(order, {})
            home_chip = team_chip_html(home, size="small")
            away_chip = team_chip_html(away, size="small")
            st.markdown(
                f'**Partido {order}** &nbsp; {home_chip} vs {away_chip}',
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.text_input(
                    "Fecha (ej: 12 Jun)", value=ex.get("match_date", ""),
                    key=f"sched_date_{order}",
                )
            with col2:
                st.text_input(
                    "Hora ARG (ej: 14:00)", value=ex.get("match_time", ""),
                    key=f"sched_time_{order}",
                )

            col3, col4 = st.columns(2)
            with col3:
                st.text_input(
                    "Estadio", value=ex.get("stadium", ""),
                    key=f"sched_stad_{order}",
                )
            with col4:
                st.text_input(
                    "Ciudad", value=ex.get("city", ""),
                    key=f"sched_city_{order}",
                )
            st.markdown("---")

        submitted = st.form_submit_button("💾 Guardar Horarios", use_container_width=True)
        if submitted:
            saved = 0
            for g, order, home, away in group_matches_list:
                date_v = st.session_state.get(f"sched_date_{order}", "").strip()
                time_v = st.session_state.get(f"sched_time_{order}", "").strip()
                stad_v = st.session_state.get(f"sched_stad_{order}", "").strip()
                city_v = st.session_state.get(f"sched_city_{order}", "").strip()
                if date_v or time_v or stad_v:
                    db.set_match_schedule(selected_group, order, date_v, time_v, stad_v, city_v)
                    saved += 1
            st.success(f"Horarios guardados! ({saved} partidos)")
            st.rerun()


# ============================================================
# ADMIN: INFO TORNEO (campeon, finalista, etc)
# ============================================================
def page_admin_tournament():
    st.markdown('<div class="main-header"><h1>🏆 Informacion del Torneo</h1></div>', unsafe_allow_html=True)

    teams_list = [""] + ALL_TEAMS

    current_champ = db.get_tournament_info("champion") or ""
    current_fin = db.get_tournament_info("finalist") or ""
    current_s1 = db.get_tournament_info("semi1") or ""
    current_s2 = db.get_tournament_info("semi2") or ""

    with st.form("tournament_info"):
        st.markdown("### Resultados finales del torneo")
        st.markdown("Cargar estos datos cuando se conozcan los resultados reales.")

        col1, col2 = st.columns(2)
        with col1:
            c_idx = teams_list.index(current_champ.upper()) if current_champ.upper() in teams_list else 0
            champ = st.selectbox("Campeon", teams_list, index=c_idx)
        with col2:
            f_idx = teams_list.index(current_fin.upper()) if current_fin.upper() in teams_list else 0
            fin = st.selectbox("Finalista", teams_list, index=f_idx)

        col3, col4 = st.columns(2)
        with col3:
            s1_idx = teams_list.index(current_s1.upper()) if current_s1.upper() in teams_list else 0
            s1 = st.selectbox("Semifinalista 1", teams_list, index=s1_idx)
        with col4:
            s2_idx = teams_list.index(current_s2.upper()) if current_s2.upper() in teams_list else 0
            s2 = st.selectbox("Semifinalista 2", teams_list, index=s2_idx)

        submitted = st.form_submit_button("💾 Guardar Info", use_container_width=True)
        if submitted:
            if champ:
                db.set_tournament_info("champion", champ)
            if fin:
                db.set_tournament_info("finalist", fin)
            if s1:
                db.set_tournament_info("semi1", s1)
            if s2:
                db.set_tournament_info("semi2", s2)
            st.success("Info del torneo actualizada!")
            st.rerun()


# ============================================================
# ADMIN: CLASIFICADOS OFICIALES
# ============================================================
def page_admin_classification():
    st.markdown('<div class="main-header"><h1>📊 Clasificados Oficiales</h1></div>', unsafe_allow_html=True)

    st.markdown("Cargá los clasificados oficiales de cada grupo una vez que termine la fase de grupos.")

    existing = db.get_official_group_classifications()
    cls_map = {c["group_name"]: c for c in existing}
    existing_thirds = set(db.get_official_best_thirds())

    group_names = sorted(GROUPS.keys())

    with st.form("admin_classification"):
        for group in group_names:
            teams = GROUPS[group]
            teams_list = [""] + teams

            current = cls_map.get(group, {})

            st.markdown(f"**Grupo {group}**: {', '.join(teams)}")
            col1, col2, col3 = st.columns(3)
            with col1:
                f_idx = teams_list.index(current.get("first_place", "")) if current.get("first_place") in teams_list else 0
                st.selectbox(f"1ro Grupo {group}", teams_list, index=f_idx, key=f"off_cls_1_{group}")
            with col2:
                s_idx = teams_list.index(current.get("second_place", "")) if current.get("second_place") in teams_list else 0
                st.selectbox(f"2do Grupo {group}", teams_list, index=s_idx, key=f"off_cls_2_{group}")
            with col3:
                t_idx = teams_list.index(current.get("third_place", "")) if current.get("third_place") in teams_list else 0
                st.selectbox(f"3ro Grupo {group}", teams_list, index=t_idx, key=f"off_cls_3_{group}")

        st.markdown("---")
        st.markdown("### Mejores terceros que clasifican (8 de 12)")
        cols = st.columns(4)
        for i, group in enumerate(group_names):
            with cols[i % 4]:
                st.checkbox(f"Grupo {group}", value=group in existing_thirds, key=f"off_third_{group}")

        submitted = st.form_submit_button("💾 Guardar Clasificados Oficiales", use_container_width=True)
        if submitted:
            for group in group_names:
                first = st.session_state.get(f"off_cls_1_{group}", "")
                second = st.session_state.get(f"off_cls_2_{group}", "")
                third = st.session_state.get(f"off_cls_3_{group}", "")
                if first and second:
                    db.set_official_group_classification(group, first, second, third or None)

            sel_thirds = [g for g in group_names if st.session_state.get(f"off_third_{g}")]
            if sel_thirds:
                db.set_official_best_thirds(sel_thirds)

            st.success("Clasificados oficiales guardados!")
            st.rerun()


# ============================================================
# ADMIN: GESTION DE JUGADORES
# ============================================================
def page_admin_users():
    st.markdown('<div class="main-header"><h1>👥 Gestionar Jugadores</h1></div>', unsafe_allow_html=True)

    users = db.get_all_users_detailed()

    st.markdown(f"### Jugadores registrados: {len(users)}")
    st.markdown("---")

    if not users:
        st.info("No hay jugadores registrados todavia.")
        return

    for u in users:
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
        with col1:
            st.markdown(f"**{u['display_name']}**")
        with col2:
            st.markdown(f"`{u['email']}`")
        with col3:
            st.markdown(f"Pronosticos: {u['predictions_count']}/72")
        with col4:
            if st.button("🔑", key=f"reset_pw_{u['id']}", help="Resetear contraseña"):
                st.session_state[f"show_reset_{u['id']}"] = True
        with col5:
            if st.button("🗑️", key=f"del_user_{u['id']}", help="Eliminar jugador"):
                st.session_state[f"confirm_del_{u['id']}"] = True

        # Resetear contraseña
        if st.session_state.get(f"show_reset_{u['id']}"):
            with st.form(f"reset_form_{u['id']}"):
                new_pw = st.text_input(f"Nueva contraseña para {u['display_name']}", type="password",
                                       key=f"new_pw_{u['id']}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("Guardar"):
                        if new_pw and len(new_pw) >= 4:
                            db.reset_user_password(u['id'], new_pw)
                            st.session_state.pop(f"show_reset_{u['id']}", None)
                            st.success(f"Contraseña de {u['display_name']} actualizada!")
                            st.rerun()
                        else:
                            st.error("La contraseña debe tener al menos 4 caracteres")
                with col_cancel:
                    if st.form_submit_button("Cancelar"):
                        st.session_state.pop(f"show_reset_{u['id']}", None)
                        st.rerun()

        # Confirmacion de eliminacion
        if st.session_state.get(f"confirm_del_{u['id']}"):
            st.warning(f"Estas seguro de eliminar a **{u['display_name']}**? Se borran todos sus pronosticos.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Si, eliminar", key=f"yes_del_{u['id']}", type="primary"):
                    db.delete_user(u['id'])
                    st.session_state.pop(f"confirm_del_{u['id']}", None)
                    st.success(f"{u['display_name']} eliminado")
                    st.rerun()
            with col_no:
                if st.button("Cancelar", key=f"no_del_{u['id']}"):
                    st.session_state.pop(f"confirm_del_{u['id']}", None)
                    st.rerun()

        st.markdown("---")

    # Crear usuario manualmente
    st.markdown("### Agregar jugador manualmente")
    with st.form("add_user_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_email = st.text_input("Email del jugador")
        with col2:
            new_name = st.text_input("Nombre completo")
        with col3:
            new_pass = st.text_input("Contraseña temporal", type="password")

        submitted = st.form_submit_button("Agregar jugador", use_container_width=True)
        if submitted:
            if not new_email or not new_name or not new_pass:
                st.error("Completa todos los campos")
            elif not _is_valid_email(new_email):
                st.error("El email no tiene un formato valido")
            elif db.user_exists(new_email):
                st.error("Ya existe una cuenta con ese email")
            else:
                db.create_user(new_email, new_name, new_pass)
                st.success(f"Jugador {new_name} agregado! Puede usar el email {new_email} para ingresar.")
                st.rerun()


# ============================================================
# ROUTER PRINCIPAL
# ============================================================
def main():
    user = st.session_state.user

    if not user:
        if st.session_state.page == "forgot_password":
            page_forgot_password()
        else:
            page_login()
        return

    render_sidebar()

    page = st.session_state.page

    pages = {
        "leaderboard": page_leaderboard,
        "upcoming": page_upcoming_matches,
        "predictions": page_predictions,
        "final_predictions": page_final_predictions,
        "results": page_results,
        "playoffs": page_playoffs,
        # Admin pages
        "admin_results": page_admin_results,
        "admin_playoffs": page_admin_playoffs,
        "admin_scorers": page_admin_scorers,
        "admin_schedule": page_admin_schedule,
        "admin_users": page_admin_users,
        "admin_tournament": page_admin_tournament,
        "admin_classification": page_admin_classification,
    }

    # Verificar permisos admin
    admin_pages = {"admin_results", "admin_playoffs", "admin_scorers", "admin_schedule", "admin_tournament", "admin_users", "admin_classification"}
    if page in admin_pages and not user.get("is_admin"):
        st.error("No tenes permisos de administrador")
        st.session_state.page = "leaderboard"
        st.rerun()
        return

    # Admin no puede cargar pronosticos
    player_only_pages = {"predictions", "final_predictions"}
    if page in player_only_pages and user.get("is_admin"):
        st.warning("El admin no puede cargar pronosticos. Usa las paginas de administracion.")
        st.session_state.page = "leaderboard"
        st.rerun()
        return

    page_fn = pages.get(page, page_leaderboard)
    page_fn()


if __name__ == "__main__":
    main()

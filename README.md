# Prode Mundial 2026

Aplicacion web para el juego de predicciones del Mundial FIFA 2026.

## Estructura

```
prode_mundial_2026/
├── .streamlit/config.toml   # Tema oscuro y config de Streamlit
├── app.py                   # UI principal (Streamlit)
├── data.py                  # Fixtures, grupos, equipos, jugadores
├── db.py                    # Capa de base de datos SQLite
├── scoring.py               # Motor de puntuacion
├── requirements.txt         # Dependencias
└── README.md
```

## Instalacion local

```bash
cd prode_mundial_2026
pip install -r requirements.txt
streamlit run app.py
```

## Deploy en Streamlit Cloud

1. Subir el proyecto a un repositorio de GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar el repo y seleccionar `app.py` como archivo principal
4. Deploy

**Nota importante:** Streamlit Cloud tiene filesystem efimero. La base SQLite se reinicia con cada deploy/restart. Para produccion persistente, migrar a una base externa (Supabase, PlanetScale, Turso, etc.) o usar Streamlit con un volumen persistente.

## Credenciales

- **Admin:** usuario `admin`, contraseña `admin2026`
- Los jugadores se registran desde la pantalla de login

## Sistema de puntos

**Fase de Grupos (por partido):**
- Resultado correcto (W/D/L): 1pt
- Pleno (resultado exacto): +1pt

**Clasificados (por grupo):**
- 1ro y 2do exactos: 4pts
- Ambos correctos, invertidos: 3pts
- Un clasificado en posicion correcta: 2pts
- Un clasificado entre top 2: 1pt

**Largo plazo:**
- Semifinalista correcto: 3pts
- Finalista correcto: +5pts (acumulable)
- Campeon correcto: +7pts (acumulable = 15pts max por seleccion)

**Goleadores:**
- 1er goleador: 10pts
- 2do goleador: 5pts
- Max 15pts entre ambos

**Playoffs (por partido):**
- Resultado 90min correcto: 1pt
- Pleno 90min: +2pts
- Equipo que avanza: 1pt (2pts en la final)
- MVP de la final: 1pt

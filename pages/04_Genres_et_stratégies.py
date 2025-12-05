import re
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Genres & stratégies — Steam",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# TITRE
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <h1 style="color:#9b7dff;">Genres & stratégies</h1>
    <h3 style="color:#ecf0f1;">Quels genres représentent les meilleures opportunités sur Steam ?</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# =========================================================
# CHARGEMENT DU FICHIER LOCAL
# =========================================================

PATH_GAMES_CLEAN = "data/games_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(PATH_GAMES_CLEAN)

    # Sécurité
    if "Total_reviews" not in df.columns:
        df["Total_reviews"] = df["Positive"] + df["Negative"]

    if "Ratio_Positive" not in df.columns:
        df["Ratio_Positive"] = df["Positive"] / df["Total_reviews"].replace(0, 1)

    return df[df["Release_year"].between(2014, 2024)]

df = load_data()
# =========================================================
# 2. PRÉPARATION DES GENRES
# =========================================================
def safe_parse_genres(x):
    if isinstance(x, list):
        return x
    if not isinstance(x, str) or x.strip() == "":
        return []
    s = x.strip()

    if s.startswith("[") and s.endswith("]"):
        items = re.findall(r"'(.*?)'|\"(.*?)\"", s)
        cleaned = [a or b for (a, b) in items if (a or b)]
        if cleaned:
            return cleaned

    tokens = re.split(r"[,;/|]", s)
    return [t.strip() for t in tokens if t.strip()]

def normalize_genre(g):
    if not isinstance(g, str):
        return None
    s = g.strip()
    if s == "":
        return None

    low = s.lower()

    if "free to play" in low or "free-to-play" in low or "f2p" in low:
        return "free to play"

    if low in {"rpg", "mmorpg"}:
        return low.upper()

    return s.title()

@st.cache_data
def compute_genre_table(min_nb_jeux_for_display: int = 1):
    df_g = df.copy()

    df_g["Genres_list"] = df_g["Genres"].apply(safe_parse_genres)
    df_g = df_g.explode("Genres_list")
    df_g["Genres_list"] = df_g["Genres_list"].apply(normalize_genre)

    df_g = df_g[df_g["Genres_list"].notna() & (df_g["Genres_list"] != "")]

    genre_stats = df_g.groupby("Genres_list").agg(
        nb_jeux=("AppID", "count"),
        total_reviews=("Total_reviews", "sum"),
        total_pos=("Positive", "sum"),
        total_neg=("Negative", "sum"),
        ratio_moyen=("Ratio_Positive", "mean"),
    ).reset_index()

    genre_year = df_g.groupby(
        ["Release_year", "Genres_list"]
    ).size().reset_index(name="count")

    genre_year = genre_year[
        genre_year["Release_year"].between(2014, 2024)
    ]

    pivot_growth = genre_year.pivot(
        index="Genres_list", columns="Release_year", values="count"
    ).fillna(0)

    for y in [2014, 2024]:
        if y not in pivot_growth.columns:
            pivot_growth[y] = 0

    pivot_growth["croissance"] = pivot_growth[2024] - pivot_growth[2014]

    genre_final = genre_stats.merge(
        pivot_growth[["croissance"]],
        left_on="Genres_list",
        right_index=True,
        how="left"
    ).fillna(0)

    max_reviews = genre_final["total_reviews"].max() or 1
    genre_final["taille"] = (
        genre_final["total_reviews"] / max_reviews * 3000 + 200
    )

    genre_filtered = genre_final[
        genre_final["nb_jeux"] >= min_nb_jeux_for_display
    ].copy()

    return genre_final, genre_filtered


# =========================================================
# 3. PARAMÈTRE UTILISATEUR
# =========================================================

st.subheader("Paramètre d’analyse")

min_nb_jeux = st.slider(
    "Nombre minimum de jeux pour considérer un genre",
    min_value=200,
    max_value=10000,
    value=500,
    step=100,
)

genre_final, genre_filtered = compute_genre_table(min_nb_jeux)

if genre_filtered.empty:
    st.error("Aucun genre ne respecte ce seuil.")
    st.stop()

genre_filtered["ratio_moyen_pct"] = (genre_filtered["ratio_moyen"] * 100).round(1)
st.caption(f"Filtre appliqué : minimum {min_nb_jeux} jeux par genre.")

st.markdown("---")


# =========================================================
# 4. METRICS RAPIDES
# =========================================================

col_a, col_b, col_c = st.columns(3)

g_pop = genre_filtered.sort_values("total_reviews", ascending=False).iloc[0]

g_quality_df = genre_filtered[genre_filtered["total_reviews"] >= 1_000_000]
g_quality = (
    g_quality_df.sort_values("ratio_moyen", ascending=False).iloc[0]
    if not g_quality_df.empty
    else genre_filtered.sort_values("ratio_moyen", ascending=False).iloc[0]
)

g_growth = genre_filtered.sort_values("croissance", ascending=False).iloc[0]

with col_a:
    st.metric("Genre le plus populaire", g_pop["Genres_list"],
              f"{int(g_pop['total_reviews']):,} avis".replace(",", " "))

with col_b:
    st.metric("Meilleure qualité moyenne", g_quality["Genres_list"],
              f"{g_quality['ratio_moyen']*100:.1f} % d’avis positifs")

with col_c:
    st.metric("Croissance la plus forte", g_growth["Genres_list"],
              f"{int(g_growth['croissance']):,} jeux".replace(",", " "))

st.markdown("---")


# =========================================================
# 5. VISUALISATIONS STRATÉGIQUES — TABS 2D / 3D
# =========================================================

st.header("Analyses stratégiques des genres")

tab2d, tab3d = st.tabs(["Vue 2D", "Vue 3D"])

med_croissance = genre_filtered["croissance"].median()
med_ratio = genre_filtered["ratio_moyen"].median()

def categorize(row):
    if row["croissance"] >= med_croissance and row["ratio_moyen"] >= med_ratio:
        return "Winner"
    elif row["croissance"] >= med_croissance:
        return "Émergent"
    elif row["ratio_moyen"] >= med_ratio:
        return "Stable & fiable"
    return "Risque"

genre_filtered["categorie"] = genre_filtered.apply(categorize, axis=1)

color_map = {
    "Winner": "#2ecc71",
    "Émergent": "#f1c40f",
    "Stable & fiable": "#3498db",
    "Risque": "#e74c3c"
}

with tab2d:
    st.subheader("Matrice stratégique — Croissance × Qualité")

    fig_scatter = px.scatter(
        genre_filtered,
        x="croissance",
        y="ratio_moyen",
        size="total_reviews",
        color="categorie",
        color_discrete_map=color_map,
        hover_name="Genres_list",
        hover_data={
            "nb_jeux": True,
            "total_reviews": True,
            "ratio_moyen_pct": True,
        },
        size_max=60,
        template="plotly_dark",
    )

    fig_scatter.add_vline(x=med_croissance, line_dash="dash", line_color="white")
    fig_scatter.add_hline(y=med_ratio, line_dash="dash", line_color="white")

    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3d:
    st.subheader("Vue 3D — Croissance × Qualité × Nombre de jeux")

    fig3d = px.scatter_3d(
        genre_filtered,
        x="croissance",
        y="ratio_moyen",
        z="nb_jeux",
        color="categorie",
        color_discrete_map=color_map,
        hover_name="Genres_list",
        size="total_reviews",
        size_max=50,
        template="plotly_dark",
    )

    st.plotly_chart(fig3d, use_container_width=True)

st.markdown("---")


# =========================================================
# 6. ANALYSES CROISÉES AVANCÉES
# =========================================================

st.header("Analyses croisées avancées par genre")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 — Genres les plus populaires")
    top_pop = genre_filtered.sort_values("total_reviews", ascending=False).head(10)

    fig_pop = px.bar(
        top_pop[::-1],
        x="total_reviews",
        y="Genres_list",
        orientation="h",
        template="plotly_dark",
        color="total_reviews",
        color_continuous_scale="Tealgrn",
    )

    st.plotly_chart(fig_pop, use_container_width=True)

with col2:
    st.subheader("Top 10 — Genres les mieux notés (volume suffisant)")

    high_vol = genre_filtered[genre_filtered["total_reviews"] >= 1_000_000]
    top_quality = high_vol.sort_values("ratio_moyen", ascending=False).head(10)

    fig_quality = px.bar(
        top_quality[::-1],
        x="ratio_moyen",
        y="Genres_list",
        orientation="h",
        template="plotly_dark",
        color="ratio_moyen",
        color_continuous_scale="Viridis",
    )

    st.plotly_chart(fig_quality, use_container_width=True)

st.markdown("---")

st.subheader("Genres à plus forte croissance")

top_growth = genre_filtered.sort_values("croissance", ascending=False).head(10)

fig_growth = px.bar(
    top_growth,
    x="Genres_list",
    y="croissance",
    template="plotly_dark",
    color="croissance",
    color_continuous_scale="Turbo",
)

st.plotly_chart(fig_growth, use_container_width=True)

st.markdown("---")


# =========================================================
# 7. SYNTHÈSE STRATÉGIQUE
# =========================================================
from textwrap import dedent

html_block = dedent("""
<div style="
    background-color:#000;
    border:2px solid #9b7dff;
    border-radius:12px;
    padding:20px 25px;
    margin:25px 0;
    color:white;
    font-size:16px;
    line-height:1.7;
">
<div style="font-size:22px; font-weight:600; margin-bottom:10px;">
    Synthèse stratégique
</div>

<p>Les analyses montrent des différences marquées entre les genres :</p>

<ul style="margin-left:20px; list-style-position:outside;">
    <li>Certains genres, comme Action ou Adventure, combinent popularité élevée et bonne qualité.</li>
    <li>D'autres genres affichent une forte croissance mais une qualité plus variable : ils représentent des opportunités, mais demandent un positionnement précis.</li>
    <li>Les genres très bien notés mais en croissance modérée peuvent constituer un terrain sûr pour un projet avec moins de risque.</li>
    <li>Les genres cumulant faible qualité et absence de dynamique doivent être considérés avec prudence.</li>
</ul>

<p style="margin-top:10px;">
Ces résultats permettent d’orienter le choix d’un genre pour un futur jeu en fonction du positionnement stratégique recherché.
</p>

</div>
""")

st.markdown(html_block, unsafe_allow_html=True)


st.markdown("---")

# =========================================================
# NAVIGATION
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/03_Jeux_populaires.py", label="◀ Retour : Jeux Populaires")

with col2:
    st.page_link("pages/05_Synthèse_&_Conclusions.py", label="Page suivante : Synthèse & Conclusions ▶")

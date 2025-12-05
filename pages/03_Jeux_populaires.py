# =========================================================
# 02 — JEUX POPULAIRES (VERSION FINALE PRO & CORRIGÉE)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Jeux populaires", page_icon="🔥", layout="wide")

# style visuel harmonisé
st.markdown("""
<style>
h1 {
    color: #E74C3C;
    font-weight: 700;
}
.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-top: 35px;
    color: #333;
}
.block {
    background: #f7f7f7;
    padding: 18px 22px;
    border-radius: 8px;
    border: 1px solid #ddd;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITRE
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 10px 0 15px 0;">
    <h1 style="color:#9b7dff;">Jeux populaires</h1>
    <h3 style="color:white;">Analyse des jeux les plus influents sur Steam (2014–2024)</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

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

# ---------------------------------------------------------
# FIX DES DOUBLONS RAINBOW / GTA / ETC.
# ---------------------------------------------------------

df_unique = (
    df.sort_values("Total_reviews", ascending=False)
      .drop_duplicates(subset=["Name"], keep="first")
)

df_filtered = df_unique[df_unique["Total_reviews"] >= 20000]

# ---------------------------------------------------------
# TOP 20 — JEU POPULAIRES
# ---------------------------------------------------------
st.markdown("<div class='section-title' style='color:#ffffff;'>Top 20 – Jeux les plus populaires</div>", unsafe_allow_html=True)

top20 = df_unique.sort_values("Total_reviews", ascending=False).head(20)

fig1 = px.bar(
    top20[::-1],
    x="Total_reviews",
    y="Name",
    orientation="h",
    text="Total_reviews",
    color="Total_reviews",
    color_continuous_scale="Agsunset",
    height=700
)

fig1.update_traces(texttemplate='%{text:,}', textposition="outside")
fig1.update_layout(
    xaxis_title="Nombre total d'avis",
    yaxis_title="",
    coloraxis_showscale=False,
    template="plotly_white",
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(fig1, use_container_width=True)

best_game = top20.iloc[0]["Name"]
best_reviews = int(top20.iloc[0]["Total_reviews"])

st.info(f"Jeu le plus populaire : **{best_game}** avec **{best_reviews:,} avis**.")

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION INTERACTIVE : 2D & 3D
# ---------------------------------------------------------
st.markdown(
    "<div class='section-title' style='color:#ffffff;'>Popularité × Qualité — Analyses interactives</div>",
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["Vue 2D", "Vue 3D"])

# -------- 2D SCATTER --------
with tab1:
    st.markdown("### Scatter 2D — Popularité vs Qualité")

    fig2d = px.scatter(
        df_filtered,
        x="Total_reviews",
        y="Ratio_Positive",
        color="Release_year",
        size="Total_reviews",
        hover_name="Name",
        log_x=True,
        size_max=40,
        color_continuous_scale="Viridis",
        opacity=0.75,
        height=600,
    )

    fig2d.update_layout(
        xaxis_title="Nombre total d'avis (log)",
        yaxis_title="Ratio d'avis positifs",
        template="plotly_white",
    )

    st.plotly_chart(fig2d, use_container_width=True)

# -------- 3D SCATTER --------
with tab2:
    st.markdown("### Scatter 3D — Popularité × Qualité × Année")

    fig3d = px.scatter_3d(
        df_filtered,
        x="Total_reviews",
        y="Ratio_Positive",
        z="Release_year",
        color="Release_year",
        hover_name="Name",
        size="Total_reviews",
        size_max=35,
        opacity=0.75,
        color_continuous_scale="Plasma",
        height=650,
    )

    fig3d.update_layout(
        scene=dict(
            xaxis_title="Popularité (reviews)",
            yaxis_title="Qualité (ratio positif)",
            zaxis_title="Année",
        ),
        template="plotly_dark",
    )

    st.plotly_chart(fig3d, use_container_width=True)

# ---------------------------------------------------------
# SYNTHÈSE
# ---------------------------------------------------------
st.markdown("""
<style>
pre, code {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div style="
        background-color:#000;
        border:2px solid #9b7dff;
        border-radius:12px;
        padding:20px 25px;
        margin:20px 0;
        color:white;
        font-size:16px;
        line-height:1.7;
    ">

    <div style="font-size:22px; font-weight:600; margin-bottom:10px;">
        Synthèse
    </div>

    <ul style="margin-left:20px; list-style-position:outside;">
        <li>Les jeux les plus populaires sont dominés par les grands AAA (PUBG, GTA V).</li>
        <li>Plusieurs jeux massivement joués obtiennent pourtant des scores de qualité moyens.</li>
        <li>Certains jeux plus modestes affichent d’excellentes évaluations malgré une faible visibilité.</li>
        <li>L’analyse croisée 2D/3D met en lumière des comportements différents selon les générations de sortie.</li>
        <li>Cette page constitue un lien direct avec l’étude stratégique des genres.</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)



st.markdown("---")

# =========================================================
# NAVIGATION
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/02_Marché_global.py", label="◀ Retour : Marché global")

with col2:
    st.page_link("pages/04_Genres_et_stratégies.py", label="Page suivante : Genres & Stratégies ▶")

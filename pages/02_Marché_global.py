import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(page_title="Marché global — Steam 2014–2024", page_icon="📈", layout="wide")

# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------
st.markdown("""
<style>
h1 {
    color: #4A90E2;
    font-weight: 700;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #E0E0E0;
    margin-top: 40px;
}
.card {
    padding: 20px;
    border-radius: 10px;
    background: #1E1E1E;
    border: 1px solid #333;
    text-align: center;
}
.card h3 {
    margin: 0;
    font-size: 30px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔗 URL GitHub Release du dataset propre
# =========================================================
URL_GAMES_CLEAN = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games_clean.csv"


# =========================================================
# Fonction de chargement ROBUSTE (lecture binaire complète)
# =========================================================
@st.cache_data
def load_full_clean_dataset():
    """
    Charge TOUT le fichier games_clean.csv depuis GitHub Release.
    Le fichier fait ~300 Mo, donc on utilise la lecture binaire.
    """
    try:
        response = requests.get(URL_GAMES_CLEAN, stream=True)
        response.raise_for_status()

        content = response.content  # récupération binaire
        df = pd.read_csv(BytesIO(content))

        # Sécurité si certaines colonnes manquent
        if "Total_reviews" not in df.columns:
            df["Total_reviews"] = df["Positive"] + df["Negative"]

        if "Ratio_Positive" not in df.columns:
            df["Ratio_Positive"] = df["Positive"] / df["Total_reviews"].replace(0, 1)

        # Filtre sur 2014–2024
        return df[df["Release_year"].between(2014, 2024)]

    except Exception as e:
        st.error(f"Erreur lors du chargement du dataset : {e}")
        return pd.DataFrame()

df = load_full_clean_dataset()


# =========================================================
# TITRE
# =========================================================
st.markdown("""
<div style="text-align:center; padding: 10px 0 25px 0;">
    <h1>Marché global (2014–2024)</h1>
    <p style="color:#bbbbbb; font-size:16px;">Comprendre l’évolution du marché Steam sur dix ans</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# STATISTIQUES PRINCIPALES
# =========================================================
st.markdown("<div class='section-title'>Statistiques principales du marché</div>", unsafe_allow_html=True)

total_games = df.shape[0]
total_reviews = df["Total_reviews"].sum()
free_pct = (df["Price"] == 0).mean() * 100

colA, colB, colC = st.columns(3)

with colA:
    st.markdown(f"""
        <div class="card">
            <h3 style="color:#4A90E2;">{total_games:,}</h3>
            <p>Jeux publiés (2014–2024)</p>
        </div>
    """, unsafe_allow_html=True)

with colB:
    st.markdown(f"""
        <div class="card">
            <h3 style="color:#F5A623;">{total_reviews:,}</h3>
            <p>Avis analysés</p>
        </div>
    """, unsafe_allow_html=True)

with colC:
    st.markdown(f"""
        <div class="card">
            <h3 style="color:#2ECC71;">{free_pct:.1f}%</h3>
            <p>Jeux gratuits</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# ÉVOLUTION DES SORTIES
# =========================================================
st.markdown("<div class='section-title'>Évolution des sorties annuelles</div>", unsafe_allow_html=True)

count_year = df.groupby("Release_year")["AppID"].count().reset_index()

fig1 = px.line(
    count_year,
    x="Release_year",
    y="AppID",
    markers=True,
    template="plotly_dark",
    color_discrete_sequence=["#4A90E2"],
)

fig1.update_layout(
    yaxis_title="Nombre de jeux publiés",
    xaxis_title="Année",
    height=450,
)

st.plotly_chart(fig1, use_container_width=True)

delta = count_year["AppID"].iloc[-1] - count_year["AppID"].iloc[0]
pct = (delta / count_year["AppID"].iloc[0]) * 100

st.info(
    f"Entre 2014 et 2024, le nombre de sorties augmente de **{pct:.1f}%**, "
    f"passant de **{count_year['AppID'].iloc[0]:,}** à **{count_year['AppID'].iloc[-1]:,}** jeux."
)

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# DISTRIBUTION DES PRIX
# =========================================================
st.markdown("<div class='section-title'>Distribution des prix</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    fig2 = px.histogram(
        df,
        x="Price",
        nbins=60,
        template="plotly_dark",
        color_discrete_sequence=["#4A90E2"],
    )
    fig2.update_layout(
        height=450,
        xaxis_title="Prix (€)",
        yaxis_title="Nombre de jeux",
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Statistiques")
    st.write(df["Price"].describe().to_frame("Valeur"))

st.warning(f"Les jeux gratuits représentent **{free_pct:.1f}%** du marché.")

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# PRIX MÉDIAN PAR ANNÉE
# =========================================================
st.markdown("<div class='section-title'>Évolution du prix médian</div>", unsafe_allow_html=True)

median_price = df.groupby("Release_year")["Price"].median().reset_index()

fig3 = px.line(
    median_price,
    x="Release_year",
    y="Price",
    markers=True,
    template="plotly_dark",
    color_discrete_sequence=["#F5A623"],
)

fig3.update_layout(
    height=450,
    yaxis_title="Prix médian (€)",
    xaxis_title="Année",
)

st.plotly_chart(fig3, use_container_width=True)

st.info(f"Le prix médian moyen entre 2014 et 2024 est de **{median_price['Price'].mean():.2f}€**.")

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# SYNTHÈSE
# =========================================================
st.markdown("<div class='section-title'>Synthèse du marché Steam</div>", unsafe_allow_html=True)

st.markdown("""
- Forte explosion du nombre de sorties → concurrence accrue.  
- Prix globalement bas → domination de l’indie + free-to-play.  
- Marché très volatil → visibilité plus difficile à obtenir pour les petits studios.  
""")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/01_Page_d'accueil.py", label="Retour : Page d'accueil")

with col2:
    st.page_link("pages/03_Jeux_populaires.py", label="Page suivante : Jeux populaires")

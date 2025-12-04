import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --------------------------------------
# Configuration générale
# --------------------------------------
st.set_page_config(
    page_title="Analyse Steam – 2014 à 2024",
    page_icon="🎮",
    layout="wide"
)

# --------------------------------------
# CSS : style épuré et pro
# --------------------------------------
st.markdown("""
<style>
h1 {
    color: #9B59B6;
    font-weight: 700;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #E0E0E0;
    margin-top: 45px;
}
.block {
    background: #1E1E1E;
    padding: 18px 25px;
    border-radius: 8px;
    border: 1px solid #333;
    margin-bottom: 28px;
}
.small-note {
    color: #BFBFBF;
    font-size: 14px;
}
.link {
    color: #A974FF;
    text-decoration: none;
}
.footer {
    text-align:center;
    font-size:13px;
    color:gray;
    margin-top:60px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 🔗 URLs GitHub Release des datasets
# =========================================================

URL_GAMES_RAW   = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games.csv"
URL_GAMES_FIXED = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games_fixed.csv"
URL_GAMES_CLEAN = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games_clean.csv"


# =========================================================
# Fonction optimisée : lecture BINAIRE & PARTIELLE
# =========================================================
def load_partial_csv_github(url, nrows=20):
    """
    Lecture partielle (3 Mo max) d’un CSV volumineux à partir d’un fichier GitHub Release.
    Compatible Streamlit Cloud.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # lecture binaire (3 Mo max)
        chunk = response.raw.read(3_000_000)

        return pd.read_csv(BytesIO(chunk), nrows=nrows)

    except Exception as e:
        raise RuntimeError(f"Erreur de chargement binaire GitHub : {e}")


@st.cache_data
def preview_dataset(url):
    return load_partial_csv_github(url, nrows=20)


# --------------------------------------
# TITRE
# --------------------------------------
st.title("Analyse du marché Steam (2014–2024)")
st.markdown(
    "<p class='small-note'>Étude interactive du marché vidéoludique sur dix années d’évolution.</p>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# Problématique
# =========================================================
st.markdown("<div class='section-title'>Problématique</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">
Quels sont les facteurs qui déterminent le succès d’un jeu sur Steam,
et comment ces éléments permettent-ils d’identifier les genres les plus prometteurs entre 2014 et 2024 ?
</div>
""", unsafe_allow_html=True)


# =========================================================
# Présentation des datasets
# =========================================================
st.markdown("<div class='section-title'>Datasets utilisés</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">
L’application repose sur les données du dataset Kaggle :  
<a class='link' href="https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data">
Steam Games Dataset
</a>

<br><br>
Les étapes de transformation expliquent le passage :
<ul>
<li>du dataset brut (<code>games.csv</code>)</li>
<li>au dataset corrigé (<code>games_fixed.csv</code>)</li>
<li>au dataset final utilisé (<code>games_clean.csv</code>)</li>
</ul>
</div>
""", unsafe_allow_html=True)


# =========================================================
# Aperçu interactif des datasets (lecture légère)
# =========================================================
def display_preview(url, title):
    try:
        df = preview_dataset(url)
        st.write(f"### {title}")
        st.dataframe(df, use_container_width=True)
        st.caption("Aperçu limité aux premières lignes (lecture partielle du fichier).")
    except Exception as e:
        st.error(f"Erreur : {e}")


col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Dataset brut"):
        display_preview(URL_GAMES_RAW, "Dataset brut")

with col2:
    if st.button("Dataset corrigé"):
        display_preview(URL_GAMES_FIXED, "Dataset corrigé")

with col3:
    if st.button("Dataset nettoyé"):
        display_preview(URL_GAMES_CLEAN, "Dataset nettoyé")


st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# Structure du dataset final
# =========================================================
st.markdown("<div class='section-title'>Structure du dataset final</div>", unsafe_allow_html=True)

# 👉 Lecture ultra légère pour récupérer uniquement les colonnes
cols = preview_dataset(URL_GAMES_CLEAN).columns.tolist()

with st.expander("Liste des colonnes"):
    st.write(cols)

with st.expander("Description des colonnes"):
    descriptions = {
        "AppID": "Identifiant unique du jeu.",
        "Name": "Nom du jeu.",
        "Release_date": "Date de sortie.",
        "Release_year": "Année de sortie.",
        "Developer": "Développeur.",
        "Publisher": "Éditeur.",
        "Positive": "Avis positifs.",
        "Negative": "Avis négatifs.",
        "Total_reviews": "Total des avis.",
        "Ratio_Positive": "Pourcentage d’avis positifs.",
        "Genres": "Genres bruts.",
        "Genres_list": "Genres nettoyés.",
        "Tags": "Tags Steam.",
        "Price": "Prix initial.",
        "Discount": "Réduction.",
        "DLC_count": "Nombre de DLC.",
        "Windows": "Compatibilité Windows.",
        "Mac": "Compatibilité Mac.",
        "Linux": "Compatibilité Linux."
    }
    st.write(pd.DataFrame.from_dict(descriptions, orient="index", columns=["Description"]))


st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# Navigation interne
# =========================================================
st.markdown("<div class='section-title'>Contenu de l'application</div>", unsafe_allow_html=True)

colA, colB = st.columns(2)

with colA:
    st.markdown("""
<div class='block'>
<strong>Marché global</strong><br>
Analyse des sorties annuelles et dynamique globale du marché.
</div>

<div class='block'>
<strong>Jeux populaires</strong><br>
Identification des leaders du marché selon les avis.
</div>
""", unsafe_allow_html=True)

with colB:
    st.markdown("""
<div class='block'>
<strong>Genres & stratégie</strong><br>
Analyse croisée (qualité × popularité × croissance).
</div>

<div class='block'>
<strong>Recommandations finales</strong><br>
Synthèse stratégique complète.
</div>
""", unsafe_allow_html=True)


# --------------------------------------
# Footer
# --------------------------------------
st.markdown("<div class='footer'>Analyse du marché Steam (2014–2024)</div>", unsafe_allow_html=True)

st.page_link("pages/02_Marché_global.py", label="➡️ Page suivante : Marché global")

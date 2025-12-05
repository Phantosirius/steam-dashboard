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
# CSS
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
# DATA SOURCES
# =========================================================

# GitHub Release (gros fichiers bruts corrigés)
URL_GAMES_RAW   = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games.csv"
URL_GAMES_FIXED = "https://github.com/Phantosirius/steam-dashboard/releases/download/v1.0/games_fixed.csv"

# Fichier propre & léger, stocké dans le repo
PATH_GAMES_CLEAN = "data/games_clean.csv"


# =========================================================
# FONCTIONS DE CHARGEMENT
# =========================================================

def load_partial_csv_github(url, nrows=20):
    """
    Lecture légère depuis GitHub Release (limite 3 Mo).
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        chunk = response.raw.read(3_000_000)  # max 3 Mo
        return pd.read_csv(BytesIO(chunk), nrows=nrows)
    except Exception as e:
        raise RuntimeError(f"Erreur GitHub : {e}")


def preview_local_csv(path, nrows=20):
    """Lecture rapide d’un CSV local."""
    return pd.read_csv(path, nrows=nrows)


@st.cache_data
def preview_dataset_github(url):
    return load_partial_csv_github(url)


# =========================================================
# TITRE
# =========================================================
st.markdown("""
<div style="text-align:center;">
    <h1 style="color:#9b7dff;">Analyse du marché Steam (2014–2024)</h1>
</div>
""", unsafe_allow_html=True)
st.markdown(
    "<p class='small-note' style='color:white; text-align:center;'>Étude interactive du marché vidéoludique sur dix années d’évolution.</p>",
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
L’application repose sur le dataset Kaggle suivant :  
<a class='link' href="https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data">
Steam Games Dataset
</a>

<br><br>

Ce projet utilise trois versions successives du fichier, correspondant aux étapes du pipeline de préparation :

### 1. <code>games.csv</code> — Dataset brut  
Données initiales, contenant :  
• beaucoup de valeurs manquantes  
• des champs mal formés (dates, listes, booléens…)  
• des doublons et des jeux NSFW  
• des colonnes inutiles pour l'analyse (assets, descriptions HTML, screenshots…)

### 2. <code>games_fixed.csv</code> — Dataset corrigé  
Première normalisation :  
• conversion des dates et extraction de l’année  
• harmonisation des champs textuels  
• conversion numérique des variables (Price, Positive, Negative…)  
• suppression des doublons  
• correction partielle de la colonne Genres

### 3. <code>games_clean.csv</code> — Dataset final optimisé  
Préparation pour l’analyse :  
• suppression définitive de toutes les colonnes inutiles pour la DataViz  
• parsing propre des genres → création de <code>Genres_list</code>  
• ajout de variables dérivées :  
  – <code>Total_reviews</code>  
  – <code>Ratio_Positive</code>  
• filtrage strict :  
  – exclusion des jeux NSFW  
  – exclusion des jeux avec < 50 avis  
  – exclusion des titres trop rares ou avec genres aberrants  
• réduction du poids → fichier final léger et adapté à Streamlit  

Ce dernier fichier est celui utilisé dans toute l'application.
</div>
""", unsafe_allow_html=True)



# =========================================================
# Aperçu interactif des datasets
# =========================================================
def display_preview_from_github(url, title):
    try:
        df = preview_dataset_github(url)
        st.write(f"### {title}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")


def display_preview_local(path, title):
    try:
        df = preview_local_csv(path)
        st.write(f"### {title}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur : {e}")


col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Dataset brut"):
        display_preview_from_github(URL_GAMES_RAW, "Dataset brut (GitHub Release)")

with col2:
    if st.button("Dataset corrigé"):
        display_preview_from_github(URL_GAMES_FIXED, "Dataset corrigé (GitHub Release)")

with col3:
    if st.button("Dataset nettoyé"):
        display_preview_local(PATH_GAMES_CLEAN, "Dataset nettoyé (local)")


st.markdown("<hr>", unsafe_allow_html=True)


# =========================================================
# Structure du dataset final
# =========================================================
st.markdown("<div class='section-title'>Structure du dataset final</div>", unsafe_allow_html=True)

cols = preview_local_csv(PATH_GAMES_CLEAN).columns.tolist()

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
        "Genres_list": "Genres nettoyés.",
        "Price": "Prix du jeu.",
        "DLC_count": "Nombre de DLC.",
    }
    st.write(pd.DataFrame.from_dict(descriptions, orient="index", columns=["Description"]))


st.markdown("<hr>", unsafe_allow_html=True)



# =========================================================
# Navigation interne
# =========================================================
st.markdown("<div class='section-title'>Contenu de l'application</div>", unsafe_allow_html=True)

# CSS pour les cartes interactives
st.markdown("""
<style>
.nav-card {
    background: linear-gradient(135deg, #1a1a24, #11111a);
    border: 1px solid #3b3486;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 18px;
    transition: 0.25s;
    cursor: pointer;
}
.nav-card:hover {
    background: linear-gradient(135deg, #2d2659, #1c1c29);
    border-color: #7b6dff;
    transform: translateY(-4px);
}
.nav-title {
    font-size: 20px;
    font-weight: 700;
    color: #9b7dff;
}
.nav-desc {
    font-size: 14px;
    color: #cccccc;
}
</style>
""", unsafe_allow_html=True)


colA, colB = st.columns(2)

with colA:
    # Marché global
    if st.container().markdown(
        "<div class='nav-card' id='nav1'>"
        "<div class='nav-title'>Marché global</div>"
        "<div class='nav-desc'>Analyse des sorties annuelles et dynamique du marché.</div>"
        "</div>",
        unsafe_allow_html=True
    ):
        pass

    if st.button("Aller à la page Marché global", key="go_global"):
        st.switch_page("pages/02_Marché_global.py")

    # Jeux populaires
    if st.container().markdown(
        "<div class='nav-card'>"
        "<div class='nav-title'>Jeux populaires</div>"
        "<div class='nav-desc'>Identification des leaders du marché selon les avis.</div>"
        "</div>",
        unsafe_allow_html=True
    ):
        pass

    if st.button("Aller à la page Jeux populaires", key="go_pop"):
        st.switch_page("pages/03_Jeux_populaires.py")


with colB:
    # Genres & stratégie
    if st.container().markdown(
        "<div class='nav-card'>"
        "<div class='nav-title'>Genres & stratégie</div>"
        "<div class='nav-desc'>Analyse croisée : qualité × popularité × croissance.</div>"
        "</div>",
        unsafe_allow_html=True
    ):
        pass

    if st.button("Aller à la page Genres & Stratégies", key="go_gen"):
        st.switch_page("pages/04_Genres_et_stratégies.py")

    # Recommandations
    if st.container().markdown(
        "<div class='nav-card'>"
        "<div class='nav-title'>Recommandations finales</div>"
        "<div class='nav-desc'>Synthèse stratégique + moteur de recommandations.</div>"
        "</div>",
        unsafe_allow_html=True
    ):
        pass

    if st.button("Aller à la page Recommandations", key="go_rec"):
        st.switch_page("pages/06_Recommandations.py")

# --------------------------------------
# Footer
# --------------------------------------
st.markdown("<div class='footer'>Analyse du marché Steam (2014–2024)</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# NAVIGATION
# =========================================================

st.page_link("pages/02_Marché_global.py", label="Page suivante : Marché global  ▶")

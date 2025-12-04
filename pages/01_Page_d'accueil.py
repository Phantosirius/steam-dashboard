import streamlit as st
import pandas as pd
import requests
from io import StringIO

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
# 🚀 FONCTION STREAMING : LIRE SEULEMENT LES PREMIÈRES LIGNES
# =========================================================
def load_preview_csv(url, preview_rows=15):
    """
    Télécharge uniquement les premières lignes d’un CSV massif via un stream.
    Cela évite de charger 300 Mo en mémoire (limitations Streamlit Cloud).
    """
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()

            lines = []
            for i, line in enumerate(r.iter_lines(decode_unicode=True)):
                if i > preview_rows:  # on arrête tôt = rapide
                    break
                lines.append(line)

        csv_data = "\n".join(lines)
        return pd.read_csv(StringIO(csv_data))

    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement streaming : {e}")


@st.cache_data
def cached_preview(url):
    return load_preview_csv(url)



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
Les données proviennent du dataset Kaggle :  
<a class='link' href="https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data">
Steam Games Dataset
</a>

<br><br>
Transformation des fichiers :
<ul>
<li>Dataset brut : <code>games.csv</code></li>
<li>Dataset corrigé : <code>games_fixed.csv</code></li>
<li>Dataset final nettoyé : <code>games_clean.csv</code></li>
</ul>
</div>
""", unsafe_allow_html=True)


# =========================================================
# Aperçu léger des datasets
# =========================================================
def display_preview(url, title):
    try:
        df = cached_preview(url)
        st.write(f"### {title}")
        st.dataframe(df, use_container_width=True)
        st.caption("Aperçu limité (lecture streaming, ultra-rapide).")
    except Exception as e:
        st.error(str(e))


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

# lecture super légère : on stream seulement 15 lignes
df_cols = cached_preview(URL_GAMES_CLEAN)

with st.expander("Liste des colonnes"):
    st.write(df_cols.columns.tolist())

with st.expander("Description des colonnes"):
    descriptions = {
        "AppID": "Identifiant Steam.",
        "Name": "Nom du jeu.",
        "Release_date": "Date précise.",
        "Release_year": "Année.",
        "Developer": "Développeur.",
        "Publisher": "Éditeur.",
        "Positive": "Avis positifs.",
        "Negative": "Avis négatifs.",
        "Total_reviews": "Avis totaux.",
        "Ratio_Positive": "% d’avis positifs.",
        "Genres": "Genres bruts.",
        "Genres_list": "Genres nettoyés.",
        "Tags": "Tags Steam.",
        "Price": "Prix du jeu.",
        "Discount": "Réduction.",
        "DLC_count": "Nombre de DLC.",
        "Windows": "Disponible sur Windows.",
        "Mac": "Disponible sur Mac.",
        "Linux": "Disponible sur Linux."
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
Évolution des sorties de jeux et dynamique du marché.
</div>

<div class='block'>
<strong>Jeux populaires</strong><br>
Classement des jeux les plus influents.
</div>
""", unsafe_allow_html=True)

with colB:
    st.markdown("""
<div class='block'>
<strong>Genres & stratégie</strong><br>
Analyse croisée popularité × qualité × croissance.
</div>

<div class='block'>
<strong>Recommandations</strong><br>
Moteur de similarité pour proposer des jeux proches.
</div>
""", unsafe_allow_html=True)


# --------------------------------------
# Footer
# --------------------------------------
st.markdown("<div class='footer'>Analyse du marché Steam (2014–2024)</div>", unsafe_allow_html=True)

st.page_link("pages/02_Marché_global.py", label="➡️ Page suivante : Marché global")

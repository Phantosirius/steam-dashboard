import streamlit as st
import pandas as pd
import os

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

# --------------------------------------
# TITRE
# --------------------------------------
st.title("Analyse du marché Steam (2014–2024)")
st.markdown(
    "<p class='small-note'>Étude interactive du marché vidéoludique sur dix années d’évolution.</p>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------
# Problématique
# --------------------------------------
st.markdown("<div class='section-title'>Problématique</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">
Quels sont les facteurs qui déterminent le succès d’un jeu sur Steam, et comment ces éléments permettent-ils d’identifier les genres les plus prometteurs entre 2014 et 2024 ?
</div>
""", unsafe_allow_html=True)

# --------------------------------------
# Présentation des datasets
# --------------------------------------
st.markdown("<div class='section-title'>Datasets utilisés</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">
L’application repose sur les données du dataset Kaggle :  
<a class='link' href="https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data">
Steam Games Dataset
</a>

<br><br>
Les étapes de nettoyage présentées ci-dessous expliquent le passage :
<ul>
<li>du dataset brut (<code>games.csv</code>)</li>
<li>au dataset corrigé (<code>games_fixed.csv</code>)</li>
<li>au dataset final utilisé (<code>games_clean.csv</code>)</li>
</ul>
</div>
""", unsafe_allow_html=True)

DATA_DIR = "data"

@st.cache_data
def load_dataset(path):
    return pd.read_csv(path)

def display_limited_dataset(path, title):
    if not os.path.exists(path):
        st.error(f"Fichier introuvable : {path}")
        return

    df = load_dataset(path)
    st.write(f"### {title}")
    st.markdown(f"Taille originale : **{df.shape[0]} lignes × {df.shape[1]} colonnes**")
    st.dataframe(df.head(15), use_container_width=True)
    st.caption("Aperçu limité aux 15 premières lignes.")
    return df

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Dataset brut"):
        display_limited_dataset(os.path.join(DATA_DIR, "games.csv"), "Dataset brut")

with col2:
    if st.button("Dataset corrigé"):
        display_limited_dataset(os.path.join(DATA_DIR, "games_fixed.csv"), "Dataset corrigé")

with col3:
    if st.button("Dataset nettoyé"):
        display_limited_dataset(os.path.join(DATA_DIR, "games_clean.csv"), "Dataset nettoyé")

st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------
# Étapes du nettoyage (mise à jour exacte)
# --------------------------------------
st.markdown("<div class='section-title'>Étapes du nettoyage des données</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">

<strong>1. Correction structurelle</strong><br>
Réalignement de la colonne <code>Discount / DLC count</code> qui entraînait un décalage global sur le dataset brut.

<br><br>

<strong>2. Normalisation des formats</strong><br>
• Conversion des dates en année de sortie (<code>Release_year</code>)<br>
• Correction des types numériques (avis, prix, DLC…)<br>
• Nettoyage des chaînes de caractères

<br><br>

<strong>3. Reconstruction des indicateurs analytiques</strong><br>
• <code>Total_reviews = Positive + Negative</code><br>
• <code>Ratio_Positive = Positive / Total_reviews</code><br>
• Parsing avancé des genres (<code>Genres_list</code>)<br>
• Normalisation des genres (fusion des variantes de “Free to Play”, capitalisation, RPG/MMORPG…)

<br><br>

<strong>4. Filtrage qualité global</strong><br>
• Exclusion des contenus NSFW (dans <code>Name</code> et <code>Genres</code>)<br>
• Suppression des doublons sur <code>AppID</code><br>
• Retrait des valeurs incohérentes (avis négatifs, ratio hors intervalle)

<br><br>

<strong>5. Export final</strong><br>
Le fichier <code>games_clean.csv</code> constitue la base unique pour l'ensemble de l'application.

</div>
""", unsafe_allow_html=True)

# --------------------------------------
# Structure du dataset final
# --------------------------------------
st.markdown("<div class='section-title'>Structure du dataset final</div>", unsafe_allow_html=True)

df_clean = load_dataset(os.path.join(DATA_DIR, "games_clean.csv"))

with st.expander("Liste des colonnes"):
    st.write(df_clean.columns.tolist())

with st.expander("Description des colonnes"):
    descriptions = {
        "AppID": "Identifiant unique du jeu sur Steam.",
        "Name": "Nom du jeu.",
        "Release_date": "Date exacte de sortie.",
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
        "Price": "Prix.",
        "Discount": "Réduction.",
        "DLC_count": "Nombre de DLC.",
        "Windows": "Disponible sur Windows.",
        "Mac": "Disponible sur Mac.",
        "Linux": "Disponible sur Linux."
    }
    st.write(pd.DataFrame.from_dict(descriptions, orient="index", columns=["Description"]))

st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------
# Navigation
# --------------------------------------
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
Identification des leaders du marché selon les avis et les notes.
</div>
""", unsafe_allow_html=True)

with colB:
    st.markdown("""
<div class='block'>
<strong>Genres & stratégie</strong><br>
Analyse croissance × qualité × popularité pour comparer les genres.
</div>

<div class='block'>
<strong>Recommandations finales</strong><br>
Synthèse stratégique pour orienter un développement de jeu.
</div>
""", unsafe_allow_html=True)

# --------------------------------------
# Footer
# --------------------------------------
st.markdown("<div class='footer'>Analyse du marché Steam (2014–2024)</div>", unsafe_allow_html=True)

st.page_link("pages/02_Marché_global.py", label="Page suivante : Marché global")

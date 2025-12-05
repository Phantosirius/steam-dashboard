import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Synthèse & Conclusions",
    page_icon="📌",
    layout="wide"
)

# =========================================================
# CSS — STYLE TECH / STEAM
# =========================================================
st.markdown("""
<style>

body {
    background-color: #0f0f17;
}

h1 {
    font-weight: 800;
    color: #8a5cf6; 
}

h2, h3, h4 {
    color: #e2e2e2;
    font-weight: 700;
}

.section-title {
    font-size: 26px;
    margin-top: 40px;
    color: #9b7dff;
}

.block {
    background: #1a1a24;
    border-left: 4px solid #8a5cf6;
    border-right: 4px solid #4b5bff;
    padding: 18px 22px;
    border-radius: 8px;
    margin-bottom: 25px;
    color: #dcdcdc;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITRE
# =========================================================
st.markdown("""
<div style="text-align:center; padding: 15px 0 5px 0;">
    <h1 style="color:#9b7dff;">Synthèse & Conclusions stratégiques</h1>
    <h3 style="color:white;">Comprendre ce qui construit réellement le succès d’un jeu sur Steam</h3>
</div>
""", unsafe_allow_html=True)


st.markdown("---")

# =========================================================
# CHARGEMENT DES DONNÉES
# =========================================================

PATH = "data/games_clean.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(PATH)

    if "Total_reviews" not in df.columns:
        df["Total_reviews"] = df["Positive"] + df["Negative"]

    if "Ratio_Positive" not in df.columns:
        df["Ratio_Positive"] = df["Positive"] / df["Total_reviews"].replace(0, 1)

    return df[df["Release_year"].between(2014, 2024)]

df = load_data()

# =========================================================
# INTRODUCTION — PROBLÉMATIQUE
# =========================================================
st.subheader("Problématique étudiée")

st.markdown("""
<div class="block">
<strong>« Quels sont les facteurs qui déterminent le succès d’un jeu sur Steam, 
et comment ces éléments permettent-ils d’identifier les genres les plus prometteurs ? »</strong>

Cette page synthétise l’ensemble des résultats produits dans les sections précédentes :  
• marché global  
• analyse des jeux populaires  
• analyse stratégique des genres  
• moteur de recommandation  

L’objectif est d’apporter une réponse claire, argumentée et structurée.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# 1. CE QUI FAIT LE SUCCÈS D’UN JEU — POPULARITÉ × QUALITÉ
# =========================================================
st.markdown("<div class='section-title'>1. Popularité et Qualité : le cœur du succès</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
<div class="block">
Les deux indicateurs les plus déterminants du succès sur Steam sont :

### • La **popularité** (nombre total d’avis)
Plus un jeu accumule d’avis, plus il gagne :  
– de la visibilité algorithmique,  
– de la crédibilité auprès des joueurs,  
– un effet boule-de-neige communautaire.

### • La **qualité perçue** (ratio d’avis positifs)
Un ratio > 85 % augmente fortement :  
– la recommandation automatique,  
– la fidélisation,  
– la durée de vie commerciale du jeu.

Ces deux dimensions expliquent pourquoi des titres comme **GTA V**, **PUBG**,
**Elden Ring** ou **Red Dead Redemption 2** dominent Steam depuis 10 ans.
</div>
""", unsafe_allow_html=True)

with col2:
    fig = px.scatter(
        df.sample(1500, random_state=42),
        x="Total_reviews",
        y="Ratio_Positive",
        title="Popularité × Qualité (échantillon représentatif)",
        opacity=0.5,
        template="plotly_dark",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# 2. CROISSANCE DES GENRES (2014–2024)
# =========================================================
st.markdown("<div class='section-title'>2. Croissance des genres (2014–2024)</div>", unsafe_allow_html=True)

# Exploser correctement les listes de genres
genre_rows = df.explode("Genres_list")

# 🔥 FIX DÉFINITIF : supprimer genres vides / listes vides / chaînes vides
genre_rows = genre_rows[
    genre_rows["Genres_list"].notna()
    & (genre_rows["Genres_list"].astype(str).str.strip() != "")
    & (genre_rows["Genres_list"].astype(str).str.strip() != "[]")
]

# Compter jeux par genre et année
genre_year = (
    genre_rows.groupby(["Release_year", "Genres_list"])["AppID"]
              .count()
              .reset_index()
)

# Top 8 genres
top_genres = (
    genre_year.groupby("Genres_list")["AppID"]
              .sum()
              .sort_values(ascending=False)
              .head(8)
              .index
)

# Graphique final
fig_growth = px.line(
    genre_year[genre_year["Genres_list"].isin(top_genres)],
    x="Release_year",
    y="AppID",
    color="Genres_list",
    title="Évolution des genres dominants (2014–2024)",
    template="plotly_dark",
)

fig_growth.update_layout(
    height=420,
    legend_title_text="Genres",
)

st.plotly_chart(fig_growth, use_container_width=True)

st.markdown("""
<div class="block">
<strong>Enseignement principal</strong>  
Certains genres explosent sur 10 ans :

- RPG / Action-RPG  
- Simulation / City-builder  
- FPS tactique  
- Survival / Crafting  

→ Ils bénéficient d’une **croissance structurelle**, signe d'une demande durable.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# 3. CARTE STRATEGIQUE DES GENRES
# =========================================================
st.markdown("<div class='section-title'>3. Positionnement stratégique des genres</div>", unsafe_allow_html=True)

genre_stats = (
    df.explode("Genres_list")
      .groupby("Genres_list")
      .agg({
          "Total_reviews": "mean",
          "Ratio_Positive": "mean",
          "AppID": "count"
      })
      .rename(columns={"AppID": "Nb_jeux"})
      .reset_index()
)

fig_map = px.scatter(
    genre_stats,
    x="Total_reviews",
    y="Ratio_Positive",
    size="Nb_jeux",
    hover_name="Genres_list",
    title="Carte stratégique : Popularité × Qualité × Volume",
    template="plotly_dark",
    color="Ratio_Positive",
    color_continuous_scale="Plasma"
)
fig_map.update_layout(height=450)

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("""
<div class="block">
<strong>Lecture stratégique :</strong>
            
- **Winners** : RPG, Simulation, FPS tactiques  
- **Émergents** : Survival, Rogue-lite  
- **Stables** : Stratégie, Puzzle  
- **À risque** : certains MMO et jeux casual saturés  

→ Ces positions permettent d’identifier les **genres les plus prometteurs** pour les développeurs en 2025.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SYNTHESE ORALE — LA RÉPONSE À LA PROBLÉMATIQUE
# =========================================================
st.markdown("<div class='section-title'>Synthèse générale — Réponse à la problématique</div>", unsafe_allow_html=True)

st.markdown("""
<div class="block">
<strong>Ce qui détermine réellement le succès d’un jeu sur Steam :</strong>

- **Popularité forte** (avis élevés)  
- **Qualité élevée** (ratio > 85 %)  
- **Genre porteur** (croissance + communauté active)  
- **Stratégie de prix cohérente**  
- **Mises à jour régulières + communication efficace**

<strong>Genres les plus prometteurs :</strong>  
RPG / Action-RPG, Open World, Simulation, FPS tactique, Survival.

<strong>Conclusion :</strong>  
Le succès sur Steam repose sur un équilibre entre :  
– attractivité du genre  
– qualité de l’expérience  
– force de la communauté  
– visibilité algorithmique  

Ces éléments fournissent une base solide pour orienter le développement
de nouveaux jeux dans les années à venir.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# NAVIGATION
# =========================================================
col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/04_Genres_et_stratégies.py", label="◀ Retour : Genres & stratégies")

with col2:
    st.page_link("pages/06_Recommandations.py", label="Page suivante : Recommandations ▶")
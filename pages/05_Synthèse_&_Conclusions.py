import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Synthèse & Conclusions",
    page_icon="📌",
    layout="wide"
)

st.markdown("""
<div style="text-align:center; padding: 15px 0;">
    <h1 style="color:#9b59b6;"> Synthèse & Conclusions stratégiques</h1>
    <h3 style="color:#bdc3c7;">Comment les analyses précédentes répondent à la problématique</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# 🔥 CHARGEMENT DES DONNÉES VIA GOOGLE DRIVE
# =========================================================

URL_GAMES_CLEAN = "https://drive.google.com/uc?export=download&id=1qbrm-9C9PQ861r6D0-M03HFU036iOjNS"

df = pd.read_csv(URL_GAMES_CLEAN)

# sécurités
df["Total_reviews"] = df.get("Total_reviews", df["Positive"] + df["Negative"])
df["Ratio_Positive"] = df.get("Ratio_Positive", df["Positive"] / df["Total_reviews"].replace(0, 1))

# cohérence 2014–2024
df = df[df["Release_year"].between(2014, 2024)]

# =========================================================
# INTRO
# =========================================================
st.subheader(" Problématique étudiée")

st.markdown("""
### « Quels sont les facteurs qui déterminent le succès d’un jeu sur Steam, et comment ces éléments permettent-ils d’identifier les genres les plus prometteurs entre 2014 et 2024 ? »

Cette page relie et synthétise les résultats issus des trois analyses précédentes :
1. **Marché global (2014–2024)**  
2. **Jeux populaires & Facteurs de succès**  
3. **Genres & Stratégies**  
4. **Moteur de recommandation**

L'objectif est de dégager une réponse claire et argumentée.
""")

st.markdown("---")

# =========================================================
# SECTION 1 — FACTEURS DE SUCCÈS
# =========================================================
st.header(" Ce qui fait le succès d’un jeu sur Steam")

col1, col2 = st.columns([1.4, 1])

with col1:
    st.markdown("""
Les analyses de la page **« Jeux populaires »** ont permis d’identifier plusieurs 
leviers déterminants du succès :

### ✔ 1. **La popularité mesurée par les avis**
Plus un jeu cumule d’avis, plus il bénéficie :
- d’une visibilité forte dans l’algorithme Steam  
- d’un effet boule de neige lié aux communautés

### ✔ 2. **La qualité perçue (ratio d’avis positifs)**
Un ratio élevé (> 85%) favorise :
- la recommandation automatique  
- la longévité du jeu  
- les achats impulsifs

### ✔ 3. **L'année de sortie et la tendance du marché**
Certaines périodes (2016–2020) ont vu exploser :
- les Battle Royale  
- les action-open world  
- les FPS tactiques  

### ✔ 4. **La stratégie de prix**
Le marché 2014–2024 se caractérise par :
- une **explosion des free-to-play**  
- une baisse générale des prix moyens  
→ favoriser l'adoption rapide et le volume

### ✔ 5. **L’appartenance à un genre porteur**
Certains genres structurent mieux la communauté que d'autres (RPG, Simulation…).

En combinant ces éléments, on comprend mieux pourquoi certains jeux 
ont dominé Steam : GTA V, PUBG, Elden Ring, RDR2, etc.
""")

with col2:
    fig = px.scatter(
        df.sample(2000, random_state=42),
        x="Total_reviews",
        y="Ratio_Positive",
        opacity=0.5,
        title="Popularité vs Qualité (échantillon)",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 2 — GENRES LES PLUS PROMETTEURS
# =========================================================
st.header(" Quels genres sont les plus prometteurs ?")

st.markdown("""
Grâce à la **page « Genres & stratégies »**, il est possible d’évaluer chaque genre selon :

- sa **popularité totale**  
- sa **qualité moyenne**  
- sa **croissance** (2014 → 2024)  
- son **positionnement stratégique** (Winner, Émergent, Stable, Risque)

Voici les enseignements principaux :
""")

colg1, colg2 = st.columns(2)

with colg1:
    st.markdown("""
### Genres **Winner**
Croissance élevée + excellente qualité  
→ Exemples :
- **RPG / Action-RPG**  
- **Simulation / City-builder**  
- **Souls-like**  
- **FPS tactiques**  

Ces genres bénéficient d'un public fidèle et d’une demande constante.
""")

with colg2:
    st.markdown("""
### Genres **Émergents**
Croissance forte mais qualité encore variable  
→ Exemples :
- **Survival / Crafting**  
- **Rogue-lite**  
- **Deckbuilding**  

Très porteurs pour des studios indé ou AA.
""")

colg3, colg4 = st.columns(2)

with colg3:
    st.markdown("""
### Genres **Stables et fiables**
Qualité élevée mais croissance modérée  
→ Exemples :
- **Stratégie / 4X**  
- **Puzzle / Relaxing**  

Public solide, faible volatilité.
""")

with colg4:
    st.markdown("""
### Genres **à risque**
Faible croissance + qualité moyenne  
→ Exemples :
- certains **MMO**  
- certains **casuals** sursaturés  

Rentabilité incertaine, concurrence forte.
""")

st.markdown("---")

# =========================================================
# SECTION 3 — SYNTHESE GENERALE
# =========================================================
st.header(" Synthèse générale — Réponse à la problématique")

st.markdown("""
### ✔ Facteurs déterminants du succès
Un jeu a tendance à performer sur Steam lorsqu'il combine :
- **Popularité forte (avis)** → visibilité & crédibilité  
- **Qualité élevée** → recommandation & fidélisation  
- **Genre porteur** → attentes claires du public  
- **Stratégie de prix cohérente**  
- **Mises à jour régulières & communauté active**

### ✔ Genres les plus prometteurs (2014–2024)
D’après nos analyses stratégiques :
- **RPG / Action-RPG**
- **Open World narratif**
- **Simulation / City-Builder**
- **FPS tactiques & extraction shooters**
- **Rogue-lite & Survivals**

### ✔ Conclusion
Le succès sur Steam repose sur un équilibre entre **qualité**, **popularité**, 
**communauté**, et **pertinence du genre**.  
À partir de ces observations, plusieurs genres apparaissent comme les plus **porteurs** 
pour concevoir un jeu compétitif sur les dix prochaines années.
""")

st.markdown("---")

# =========================================================
# SECTION 4 — OUVERTURE VERS LA PAGE RECOMMANDATION
# =========================================================
st.header(" Mise en pratique : moteur de recommandation")

st.markdown("""
La page **« Recommandations »** illustre comment ces facteurs permettent 
de rapprocher les jeux entre eux et d’identifier :

- des jeux similaires,  
- des alternatives crédibles,
- un positionnement stratégique cohérent.

C’est la concrétisation pratique de toute l’analyse précédente.
""")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/04_Genres_et_stratégies.py", label="Retour : Genres & stratégies")

with col2:
    st.page_link("pages/06_Recommandations.py", label="Page suivante : Recommandations")

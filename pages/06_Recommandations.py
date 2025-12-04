import os
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIG STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Recommandations — Steam",
    page_icon="🎮",
    layout="wide"
)

st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <h1 style="color:#9b59b6;">Recommandations de jeux</h1>
    <h3 style="color:#bdc3c7;">Sélectionnez un jeu et découvrez des titres proches dans la même famille</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# 🔥 CHARGEMENT DES DONNÉES VIA GOOGLE DRIVE
# =========================================================
URL_GAMES_CLEAN = "https://drive.google.com/uc?export=download&id=1qbrm-9C9PQ861r6D0-M03HFU036iOjNS"

@st.cache_data
def load_cleaned_data():
    df = pd.read_csv(URL_GAMES_CLEAN)

    df["Name"] = df["Name"].fillna("Unknown")
    df["Genres"] = df["Genres"].fillna("")
    df["Positive"] = df["Positive"].fillna(0).astype(int)
    df["Negative"] = df["Negative"].fillna(0).astype(int)

    df["Total_reviews"] = df["Positive"] + df["Negative"]
    df["Ratio_Positive"] = df["Positive"] / df["Total_reviews"].replace(0, 1)

    # cohérence analyse → période du projet
    if "Release_year" in df.columns:
        df = df[df["Release_year"].between(2014, 2024)]

    # parsing genres
    df["Genres_list"] = df["Genres"].apply(safe_parse_genres)
    df["Genres_list"] = df["Genres_list"].apply(
        lambda lst: [normalize_genre(g) for g in lst if normalize_genre(g)]
    )

    # ---------- FILTRE NSFW FORT ----------
    NSFW_PATTERNS = [
        "sex", "sexual", "adult", "hentai", "nsfw", "erotic", "porn",
        "pussy", "boob", "dick", "naked", "nude", "orgasm",
        "futa", "fetish", "milf", "bdsm", "bondage", "deepthroat",
        "sperm", "vagina", "cum", "penetrat", "tits", "stripper"
    ]

    def is_nsfw(row):
        txt = (str(row["Name"]) + " " + str(row["Genres"])).lower()
        return any(k in txt for k in NSFW_PATTERNS)

    df = df[~df.apply(is_nsfw, axis=1)]

    # jeux quasi inconnus
    df = df[df["Total_reviews"] >= 50]

    # trop de tags
    df = df[df["Genres_list"].apply(lambda x: len(x) <= 6)]

    # titres étranges
    df = df[df["Name"].apply(lambda x: len(str(x)) < 80)]
    df = df[df["Name"].apply(lambda x: sum(c.isupper() for c in str(x)) < 20)]

    df["log_reviews"] = np.log1p(df["Total_reviews"])

    return df


# outils genres
def safe_parse_genres(x):
    if isinstance(x, list):
        return x
    if not isinstance(x, str) or x.strip() == "":
        return []
    s = x.strip()
    if s.startswith("[") and s.endswith("]"):
        items = re.findall(r"'(.*?)'|\"(.*?)\"", s)
        return [a or b for (a, b) in items if (a or b)]
    return [t.strip() for t in re.split(r"[,;/|]", s) if t.strip()]


def normalize_genre(g):
    if not isinstance(g, str):
        return None
    s = g.strip()
    return s.title() if s else None


df = load_cleaned_data()
st.caption(f"{len(df):,} jeux pris en compte après nettoyage.".replace(",", " "))

# =========================================================
# 2. CATÉGORISATION PRINCIPALE
# =========================================================

KNOWN_OPEN_WORLD = [
    "gta", "grand theft auto",
    "red dead", "watch dogs",
    "saints row", "sleeping dogs",
    "mafia", "just cause",
    "assassin",
    "far cry",
    "spider-man", "spiderman",
    "batman arkham"
]

def infer_main_category(name, genres):
    if not isinstance(genres, list):
        genres = []
    gl = [g.lower() for g in genres]
    name_low = str(name).lower()

    def contains_any(words):
        return any(any(k in g for k in words) for g in gl)

    if any(k in name_low for k in KNOWN_OPEN_WORLD) or contains_any(["open world", "sandbox", "crime"]):
        return "Open World / Sandbox"

    if contains_any(["battle royale"]):
        return "Battle Royale"

    if contains_any(["fps", "first-person shooter", "shooter"]) and not contains_any(["battle royale"]):
        return "FPS"

    if contains_any(["rpg", "jrpg", "role-playing", "action rpg"]):
        return "RPG"

    if contains_any(["mmorpg", "mmo", "massively multiplayer"]):
        return "MMO / MMORPG"

    if contains_any(["strategy", "rts", "4x", "turn-based"]):
        return "Strategy"

    if contains_any(["simulation", "simulator", "city builder", "building", "tycoon"]):
        return "Simulation"

    if contains_any(["sports", "racing", "football", "soccer", "f1", "basketball"]):
        return "Sports / Racing"

    if contains_any(["survival", "horror", "zombie"]):
        return "Survival / Horror"

    if contains_any(["indie", "casual", "puzzle", "relaxing"]):
        return "Indie / Casual"

    if contains_any(["action", "adventure"]):
        return "Action / Adventure"

    return "Autre"


df["main_category"] = df.apply(
    lambda row: infer_main_category(row["Name"], row["Genres_list"]),
    axis=1
)

# =========================================================
# 3. CHOIX DU JEU
# =========================================================
st.subheader("Sélection du jeu de référence")

selected_game = st.selectbox(
    "Choisissez un jeu :",
    sorted(df["Name"].unique())
)

game_row = df[df["Name"] == selected_game].iloc[0]
cat = game_row["main_category"]

st.info(f"Jeu sélectionné : **{selected_game}** — catégorie détectée : **{cat}**")
st.markdown("---")

# =========================================================
# 4. MOTEUR DE SIMILARITÉ
# =========================================================
def genre_overlap_count(target_row, ref_row):
    return len(set(ref_row["Genres_list"]).intersection(target_row["Genres_list"]))


def similarity_score(target_row, ref_row):
    g1 = set(ref_row["Genres_list"])
    g2 = set(target_row["Genres_list"])

    genre_score = len(g1.intersection(g2)) / len(g1) * 50 if len(g1) else 0

    ratio_diff = abs(ref_row["Ratio_Positive"] - target_row["Ratio_Positive"])
    qual_score = max(0, (1 - ratio_diff) * 30)

    pop_diff = abs(ref_row["log_reviews"] - target_row["log_reviews"])
    pop_score = max(0, (1 - pop_diff / 5) * 20)

    return genre_score + qual_score + pop_score


candidates = df[df["Name"] != selected_game].copy()
same_cat = candidates[candidates["main_category"] == cat].copy()
base = same_cat if len(same_cat) >= 20 else candidates

base["common_genres"] = base.apply(lambda r: genre_overlap_count(r, game_row), axis=1)
work = base[base["common_genres"] >= 1] if len(base[base["common_genres"] >= 1]) >= 5 else base

work["score_similarité"] = work.apply(lambda r: similarity_score(r, game_row), axis=1)
top5 = work.sort_values("score_similarité", ascending=False).head(5)

if top5.empty:
    st.error("Pas assez de données pour générer des recommandations pertinentes.")
    st.stop()

# =========================================================
# 5. AFFICHAGE RECOMMANDATIONS
# =========================================================
st.subheader(f"Jeux recommandés pour **{selected_game}**")

for _, row in top5.iterrows():
    genres_txt = ", ".join(row["Genres_list"]) if row["Genres_list"] else "Non renseigné"
    st.markdown(f"""
    <div style="background:#2c2c2c; padding:15px; border-radius:8px; margin-bottom:10px;">
        <h4 style="color:#9b59b6; margin-bottom:4px;">🎮 {row['Name']}</h4>
        <p style="color:#d0d0d0; margin:0;">
            Score de similarité : <b>{row['score_similarité']:.1f} / 100</b><br>
            Catégorie : <b>{row['main_category']}</b><br>
            Ratio positif : {row['Ratio_Positive']*100:.1f} %<br>
            Avis totaux : {int(row['Total_reviews']):,} avis<br>
            Genres : {genres_txt}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# 6. VISUALISATION
# =========================================================
st.subheader("Popularité × Qualité des jeux recommandés")

fig = px.scatter(
    top5,
    x="Total_reviews",
    y="Ratio_Positive",
    size="Total_reviews",
    color="score_similarité",
    hover_name="Name",
    color_continuous_scale="Plasma",
    height=600,
)

fig.add_scatter(
    x=[game_row["Total_reviews"]],
    y=[game_row["Ratio_Positive"]],
    mode="markers+text",
    text=[selected_game],
    textposition="top center",
    marker=dict(size=20, color="white", line=dict(width=2, color="black")),
    name="Jeu sélectionné"
)

fig.update_layout(
    xaxis_title="Nombre d'avis",
    yaxis_title="Ratio d'avis positifs",
    template="plotly_dark",
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# 7. EXPLICATION
# =========================================================
st.subheader("Pourquoi ces recommandations ?")

ratio_ref = game_row["Ratio_Positive"] * 100
avis_ref = int(game_row["Total_reviews"])

ratio_rec = top5["Ratio_Positive"].mean() * 100
avis_rec = int(top5["Total_reviews"].mean())

st.markdown(f"""
Les jeux recommandés appartiennent à la même famille que **{selected_game}** :  
👉 **{cat}**

Ils ont été sélectionnés sur la base de :

- **Genres partagés**  
- **Qualité comparable**  
- **Popularité similaire**

Ces trois dimensions produisent un score de similarité robuste,
garantissant des recommandations réellement proches de l’expérience
offerte par **{selected_game}**.
""")

st.page_link("pages/05_Synthèse_&_Conclusions.py", label="Page précédente : Synthèse & Conclusion")

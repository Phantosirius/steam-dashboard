import os
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
# Titre
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <h1 style="color:#9B59B6;">Genres & stratégies</h1>
    <h3 style="color:#ecf0f1;">Quels genres représentent les meilleures opportunités sur Steam ?</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

DATA_DIR = "data"
FILE = os.path.join(DATA_DIR, "games_clean.csv")


# =========================================================
# 1. CHARGEMENT + NETTOYAGE GLOBAL
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv(FILE)

    # Le dataset est déjà nettoyé (NSFW retirés, 2014–2024, avis propres)
    # Ici : uniquement sécurisation minimale.

    df["Genres"] = df["Genres"].fillna("")
    df["Name"] = df["Name"].fillna("Unknown")

    # Sécurité release year
    if "Release_year" not in df.columns:
        if "Release date" in df.columns:
            df["Release_year"] = pd.to_datetime(
                df["Release date"], errors="coerce"
            ).dt.year
        else:
            df["Release_year"] = None

    df = df[df["Release_year"].notna()]

    # Sécurité total reviews
    if "Total_reviews" not in df.columns:
        df["Positive"] = df["Positive"].fillna(0).astype(int)
        df["Negative"] = df["Negative"].fillna(0).astype(int)
        df["Total_reviews"] = df["Positive"] + df["Negative"]

    # Sécurité ratio
    if "Ratio_Positive" not in df.columns:
        df["Ratio_Positive"] = df["Positive"] / df["Total_reviews"].replace(0, 1)

    return df


df = load_data()
st.success("Dataset chargé.")

# =========================================================
# 2. PRÉPARATION DES GENRES
# =========================================================
def safe_parse_genres(x):
    """
    Convertit une chaîne 'Genres' en liste de genres.
    Gère :
      - listes Python style "['Action', 'Indie']"
      - chaînes séparées par virgules / slash / pipe
      - valeurs manquantes
    """
    if isinstance(x, list):
        return x

    if not isinstance(x, str) or x.strip() == "":
        return []

    s = x.strip()

    # Cas liste Python "[...]" avec quotes
    if s.startswith("[") and s.endswith("]"):
        items = re.findall(r"'(.*?)'|\"(.*?)\"", s)
        cleaned = [a or b for (a, b) in items if (a or b)]
        if cleaned:
            return cleaned

    # Cas séparateurs simples
    tokens = re.split(r"[,;/|]", s)
    return [t.strip() for t in tokens if t.strip()]


def normalize_genre(g):
    """
    Uniformise certains genres (notamment Free to Play).
    """
    if not isinstance(g, str):
        return None

    s = g.strip()
    if s == "":
        return None

    low = s.lower()

    # Fusion des variantes Free to Play
    if "free to play" in low or "free-to-play" in low or "f2p" in low:
        return "free to play"

    # On laisse RPG / MMORPG en majuscules
    if low in {"rpg", "mmorpg"}:
        return low.upper()

    # Sinon : capitalisation
    return s.title()


@st.cache_data
def compute_genre_table(min_nb_jeux_for_display: int = 1):
    """
    Renvoie :
      - la table agrégée par genre (genre_final),
      - et celle filtrée par nb_jeux >= min_nb_jeux_for_display (genre_filtered).
    """
    df_g = df.copy()

    # Parsing / normalisation
    df_g["Genres_list"] = df_g["Genres"].apply(safe_parse_genres)
    df_g = df_g.explode("Genres_list")
    df_g["Genres_list"] = df_g["Genres_list"].apply(normalize_genre)

    # On retire NaN / vides
    df_g = df_g[df_g["Genres_list"].notna() & (df_g["Genres_list"] != "")]

    # ---------- AGRÉGATION ----------
    genre_stats = df_g.groupby("Genres_list").agg(
        nb_jeux=("AppID", "count"),
        total_reviews=("Total_reviews", "sum"),
        total_pos=("Positive", "sum"),
        total_neg=("Negative", "sum"),
        ratio_moyen=("Ratio_Positive", "mean"),
    ).reset_index()

    # Comptage par année pour la croissance
    genre_year = df_g.groupby(
        ["Release_year", "Genres_list"]
    ).size().reset_index(name="count")

    genre_year = genre_year[
        (genre_year["Release_year"] >= 2014) &
        (genre_year["Release_year"] <= 2024)
    ]

    pivot_growth = genre_year.pivot(
        index="Genres_list",
        columns="Release_year",
        values="count"
    ).fillna(0)

    # Sécuriser colonnes 2014 / 2024
    for y in [2014, 2024]:
        if y not in pivot_growth.columns:
            pivot_growth[y] = 0

    pivot_growth["croissance"] = pivot_growth[2024] - pivot_growth[2014]

    # Merge final
    genre_final = genre_stats.merge(
        pivot_growth[["croissance"]],
        left_on="Genres_list",
        right_index=True,
        how="left"
    ).fillna(0)

    # Taille des bulles (popularité)
    max_reviews = genre_final["total_reviews"].max() or 1
    genre_final["taille"] = (
        genre_final["total_reviews"] / max_reviews * 3000 + 200
    )

    # Filtre d’affichage
    genre_filtered = genre_final[
        genre_final["nb_jeux"] >= min_nb_jeux_for_display
    ].copy()

    return genre_final, genre_filtered


# =========================================================
# 3. PARAMÈTRE UTILISATEUR SUR LA PAGE
# =========================================================

st.subheader("Paramètre d’analyse")

min_nb_jeux = st.slider(
    "Nombre minimum de jeux pour considérer un genre",
    min_value=200,
    max_value=10000,
    value=500,
    step=100,
    help="Filtre les genres ayant un volume trop faible pour être représentatif."
)

# Calcul avec le paramètre sélectionné
genre_final, genre_filtered = compute_genre_table(
    min_nb_jeux_for_display=min_nb_jeux
)

if genre_filtered.empty:
    st.error(
        "Aucun genre ne respecte ce seuil de jeux. "
        "Veuillez réduire le seuil pour afficher les analyses."
    )
    st.stop()

# Colonne supplémentaire pour le pourcentage (pour hover Plotly)
genre_filtered["ratio_moyen_pct"] = (genre_filtered["ratio_moyen"] * 100).round(1)

st.caption(f"Filtre appliqué : minimum {min_nb_jeux} jeux par genre.")

st.markdown("---")


# =========================================================
# 4. METRICS RAPIDES
# =========================================================
col_a, col_b, col_c = st.columns(3)

# --- Genre le plus populaire ---
g_pop = genre_filtered.sort_values("total_reviews", ascending=False).iloc[0]

# --- Meilleure qualité (avec volume minimum) ---
g_quality_df = genre_filtered[
    genre_filtered["total_reviews"] >= 1_000_000
]
if not g_quality_df.empty:
    g_quality = g_quality_df.sort_values("ratio_moyen", ascending=False).iloc[0]
else:
    g_quality = genre_filtered.sort_values("ratio_moyen", ascending=False).iloc[0]

# --- Plus forte croissance ---
g_growth = genre_filtered.sort_values("croissance", ascending=False).iloc[0]

with col_a:
    st.metric(
        "Genre le plus populaire",
        g_pop["Genres_list"],
        f"{int(g_pop['total_reviews']):,} avis".replace(",", " ")
    )

with col_b:
    st.metric(
        "Meilleure qualité moyenne",
        g_quality["Genres_list"],
        f"{g_quality['ratio_moyen']*100:.1f} % d’avis positifs"
    )

with col_c:
    st.metric(
        "Croissance la plus forte",
        g_growth["Genres_list"],
        f"{int(g_growth['croissance']):,} jeux".replace(",", " ")
    )

st.markdown("---")

# =========================================================
# 5. VISUALISATIONS STRATÉGIQUES — Tabs 2D / 3D
# =========================================================

st.header("Analyses stratégiques des genres")

# Onglets 2D / 3D comme dans la page Jeux populaires
tab2d, tab3d = st.tabs(["Vue 2D", "Vue 3D"])

# Médianes pour la catégorisation
med_croissance = genre_filtered["croissance"].median()
med_ratio = genre_filtered["ratio_moyen"].median()

def categorize(row):
    if row["croissance"] >= med_croissance and row["ratio_moyen"] >= med_ratio:
        return "Winner"
    elif row["croissance"] >= med_croissance and row["ratio_moyen"] < med_ratio:
        return "Émergent"
    elif row["croissance"] < med_croissance and row["ratio_moyen"] >= med_ratio:
        return "Stable & fiable"
    else:
        return "Risque"

genre_filtered["categorie"] = genre_filtered.apply(categorize, axis=1)

category_order = ["Winner", "Émergent", "Stable & fiable", "Risque"]
color_map = {
    "Winner": "#2ecc71",
    "Émergent": "#f1c40f",
    "Stable & fiable": "#3498db",
    "Risque": "#e74c3c"
}

# =========================================================
# A) MATRICE STRATÉGIQUE 2D
# =========================================================
with tab2d:
    st.subheader("Matrice stratégique — Croissance × Qualité")

    fig_scatter = px.scatter(
        genre_filtered,
        x="croissance",
        y="ratio_moyen",
        size="total_reviews",
        color="categorie",
        color_discrete_map=color_map,
        category_orders={"categorie": category_order},
        hover_name="Genres_list",
        hover_data={
            "nb_jeux": True,
            "total_reviews": True,
            "ratio_moyen_pct": True,
            "croissance": True,
            "categorie": False,
        },
        size_max=60,
        template="plotly_dark",
    )

    fig_scatter.update_layout(
        height=650,
        legend_title_text="Catégorie stratégique",
        xaxis_title="Croissance (2014 → 2024)",
        yaxis_title="Ratio moyen d'avis positifs",
    )

    # Lignes médianes
    fig_scatter.add_vline(
        x=med_croissance,
        line_width=1,
        line_dash="dash",
        line_color="white",
    )
    fig_scatter.add_hline(
        y=med_ratio,
        line_width=1,
        line_dash="dash",
        line_color="white",
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    st.caption("""
Lecture :
- Winner : genres en croissance + très bien notés  
- Stable & fiable : qualité forte mais croissance modérée  
- Émergent : en croissance mais qualité moyenne  
- Risque : faible qualité + faible croissance  
""")


# =========================================================
# B) VISUALISATION 3D
# =========================================================
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

    fig3d.update_layout(
        height=650,
        scene=dict(
            xaxis_title="Croissance (2014 → 2024)",
            yaxis_title="Ratio moyen d'avis positifs",
            zaxis_title="Nombre de jeux",
        ),
        legend_title_text="Catégorie stratégique",
    )

    st.plotly_chart(fig3d, use_container_width=True)

st.markdown("---")

# =========================================================
# 6. ANALYSES CROISÉES AVANCÉES
# =========================================================

st.header("Analyses croisées avancées par genre")

col1, col2 = st.columns(2)

# -----------------------------------------------
# A) Top 10 genres les plus populaires
# -----------------------------------------------
with col1:
    st.subheader("Top 10 — Genres les plus populaires")

    top_pop_genres = genre_filtered.sort_values(
        "total_reviews", ascending=False
    ).head(10)

    fig_bar_pop = px.bar(
        top_pop_genres[::-1],  # affiche du meilleur au moins bon
        x="total_reviews",
        y="Genres_list",
        orientation="h",
        template="plotly_dark",
        color="total_reviews",
        color_continuous_scale="Tealgrn",
    )

    fig_bar_pop.update_layout(
        height=500,
        xaxis_title="Nombre total d'avis",
        yaxis_title="Genre",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_bar_pop, use_container_width=True)


# -----------------------------------------------
# B) Top 10 genres les mieux notés (volume minimum)
# -----------------------------------------------
with col2:
    st.subheader("Top 10 — Genres les mieux notés (volume suffisant)")

    high_vol = genre_filtered[genre_filtered["total_reviews"] >= 1_000_000]

    if not high_vol.empty:
        top_quality_genres = high_vol.sort_values(
            "ratio_moyen", ascending=False
        ).head(10)
    else:
        top_quality_genres = genre_filtered.sort_values(
            "ratio_moyen", ascending=False
        ).head(10)

    fig_bar_quality = px.bar(
        top_quality_genres[::-1],
        x="ratio_moyen",
        y="Genres_list",
        orientation="h",
        template="plotly_dark",
        color="ratio_moyen",
        color_continuous_scale="Viridis",
    )

    fig_bar_quality.update_layout(
        height=500,
        xaxis_title="Ratio moyen d'avis positifs",
        yaxis_title="Genre",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig_bar_quality, use_container_width=True)

st.markdown("---")

# -----------------------------------------------
# C) Genres à plus forte croissance
# -----------------------------------------------
st.subheader("Genres à plus forte croissance (nombre de jeux publiés)")

top_growth_genres = genre_filtered.sort_values(
    "croissance", ascending=False
).head(10)

fig_bar_growth = px.bar(
    top_growth_genres,
    x="Genres_list",
    y="croissance",
    template="plotly_dark",
    color="croissance",
    color_continuous_scale="Turbo",
)

fig_bar_growth.update_layout(
    height=450,
    xaxis_title="Genre",
    yaxis_title="Croissance (2024 − 2014)",
    coloraxis_showscale=False
)

st.plotly_chart(fig_bar_growth, use_container_width=True)

st.markdown("---")


# =========================================================
# 7. SYNTHÈSE STRATÉGIQUE
# =========================================================

st.header("Synthèse stratégique")

st.markdown("""
Les analyses montrent des différences marquées entre les genres :

- Certains genres, comme Action ou Adventure, combinent popularité élevée et bonne qualité.  
- D'autres genres affichent une forte croissance mais une qualité plus variable : ils représentent des opportunités, mais demandent un positionnement précis.  
- Les genres très bien notés mais en croissance modérée peuvent constituer un terrain sûr pour un projet avec moins de risque.  
- Les genres cumulant faible qualité et absence de dynamique doivent être considérés avec prudence.

Ces éléments permettent d'orienter la sélection d'un genre pour un nouveau jeu, en tenant compte à la fois du marché, de la concurrence et des attentes des joueurs.
""")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/03_Jeux_populaires.py", label="Retour : Jeux Populaires")

with col2:
    st.page_link("pages/05_Synthèse_&_Conclusions.py", label="Page suivante : Synthèses & Conclusions")

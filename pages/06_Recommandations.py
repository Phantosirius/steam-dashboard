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

import streamlit as st

st.set_page_config(
    page_title="Analyse Steam – 2014 à 2024",
    page_icon="🎮",
    layout="centered"
)

# ---------------------------------------------------------
# LANDING PAGE STYLÉE
# ---------------------------------------------------------
st.markdown("""
<style>
.title {
    text-align:center;
    font-size:45px;
    font-weight:700;
    color:#6377F8;
    margin-top:40px;
}
.subtitle {
    text-align:center;
    font-size:20px;
    color:#CCCCCC;
    margin-top:-10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>Analyse du marché Steam</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Étude des tendances 2014–2024</div>", unsafe_allow_html=True)

st.write("")
st.write("")

st.markdown(
    "<p style='text-align:center; font-size:17px; color:#DDDDDD;'>"
    "Cliquez ci-dessous pour entrer dans l'application."
    "</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Bouton pour accéder à ta page d'accueil complète
# ---------------------------------------------------------
if st.button("➤ Entrer dans l'application", use_container_width=True):
    st.switch_page("pages/01_Page_d'accueil.py")

st.write("")
st.write("")

st.markdown(
    "<p style='text-align:center; font-size:13px; color:gray;'>"
    "Projet DataViz — Steam 2014–2024"
    "</p>",
    unsafe_allow_html=True
)

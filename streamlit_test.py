import streamlit as st

titel_container = st.container()

with titel_container:
    st.title("Test programma start")

col_opname = st.columns([4.15, 0.85])
with col_opname[0]:
    opname_klant = st.button("Programma is klaar")
    if opname_klant:
        st.success("Je hebt op de knop gedrukt – programma gestart!")

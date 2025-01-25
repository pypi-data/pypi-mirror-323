import streamlit as st

if 'df' not in st.session_state:
    st.session_state.df = {'ID': [0, 1], 'name': ["a", "b"]}

st.session_state.df1 = st.data_editor(st.session_state.df)

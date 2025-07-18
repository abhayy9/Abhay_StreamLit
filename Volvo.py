import streamlit as st
st.header("Welcome to first streamlit ")
name=st.text_input("enter your name")
button=st.button("enter",on_click=lambda: st.write(f"Welcome {name}"))

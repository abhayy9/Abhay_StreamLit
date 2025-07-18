import streamlit as st
st.header("Welcome to first streamlit ")
name=st.text_input("enter yur name")
button=st.button("enter",on_click=lambda: st.write(f"your name is {name}"))

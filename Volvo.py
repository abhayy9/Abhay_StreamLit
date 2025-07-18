# csv_name_upload_app.py

import streamlit as st
import pandas as pd

# Title
st.title("Welcome to the CSV Viewer App")

# Get user's name
name = st.text_input("Enter your name:")

# Greeting message
if name:
    st.success(f"Hello, {name}! 👋 Please upload a CSV file to continue.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# If a file is uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Preview of Uploaded CSV")
    st.dataframe(df)

    st.subheader("📊 Summary Statistics")
    st.write(df.describe())

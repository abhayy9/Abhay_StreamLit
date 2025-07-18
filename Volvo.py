# csv_upload_app.py

import streamlit as st
import pandas as pd

# Title
st.title("CSV File Uploader")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Show preview
    st.subheader("Preview of Uploaded CSV")
    st.dataframe(df)

    # Basic info
    st.subheader("Summary")
    st.write(df.describe())

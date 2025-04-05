import streamlit as st

def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = f"data:image/png;base64,{data.encode('base64').decode()}"
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

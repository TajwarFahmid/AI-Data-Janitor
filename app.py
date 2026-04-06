import streamlit as st
import pandas as pd
from groq import Groq
import os

# Streamlit Cloud handles secrets differently than local .env files
# This line looks for the key you put in the "Secrets" box during deployment
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="AI Data Janitor", layout="wide")
st.title("🧹 AI Data Janitor")
st.markdown("### Senior Capstone-Style Data Quality Engine")

uploaded_file = st.file_uploader("Upload a messy CSV (e.g., messy_data.csv)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    tab1, tab2 = st.tabs(["Raw Data Audit", "AI Cleaning Engine"])
    
    with tab1:
        st.write("#### 📊 Initial Data Health")
        col_a, col_b = st.columns(2)
        with col_a:
            st.dataframe(df)
        with col_b:
            st.write("**Missing Values Per Column:**")
            st.write(df.isnull().sum())

    with tab2:
        if st.button("✨ Run AI Clean & Repair"):
            cleaned_df = df.copy()
            
            # --- THE "JANITOR" LOGIC ---
            # 1. Clean Names
            if 'Full_Name' in cleaned_df.columns:
                cleaned_df['Full_Name'] = cleaned_df['Full_Name'].str.strip().str.title()
            
            # 2. Fix Ages & Outliers (Math/Stats Logic)
            if 'User_Age' in cleaned_df.columns:
                cleaned_df['User_Age'] = pd.to_numeric(cleaned_df['User_Age'], errors='coerce')
                median_age = cleaned_df['User_Age'].median()
                cleaned_df.loc[cleaned_df['User_Age'] > 100, 'User_Age'] = median_age
                cleaned_df['User_Age'] = cleaned_df['User_Age'].fillna(median_age)

            # 3. Standardize Dates
            if 'Join_Date' in cleaned_df.columns:
                cleaned_df['Join_Date'] = pd.to_datetime(cleaned_df['Join_Date'], errors='coerce')

            st.success("Data Cleaned Successfully!")
            st.dataframe(cleaned_df)
            
            # Download link
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Cleaned Results", data=csv, file_name="cleaned_data.csv", mime="text/csv")

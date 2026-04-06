import streamlit as st
import pandas as pd
from groq import Groq
import os

# 1. Setup - MUST BE AT THE TOP
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="AI Data Janitor", layout="wide")
st.title("🧹 AI Data Janitor")
st.markdown("### Senior Capstone-Style Data Quality Engine")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload a messy CSV", type="csv")

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
        # --- THIS IS THE PART WE UPDATED ---
        if st.button("✨ Run AI Clean & Repair"):
            cleaned_df = df.copy()
            
            # --- THE UNIVERSAL JANITOR LOGIC ---
            for col in cleaned_df.columns:
                # 1. Dynamic Text Cleaning
                if cleaned_df[col].dtype == 'object' and ('name' in col.lower() or 'text' in col.lower()):
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip().str.title()
                
                # 2. Dynamic Number Cleaning (IQR Method)
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    
                    q1 = cleaned_df[col].quantile(0.25)
                    q3 = cleaned_df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    cleaned_df[col] = cleaned_df[col].clip(lower=lower_bound, upper=upper_bound)

                # 3. Dynamic Date Cleaning
                if 'date' in col.lower() or 'time' in col.lower():
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')

            st.success("✅ Universal Cleaning & Repair Complete!")
            
            # --- SIDE-BY-SIDE COMPARISON ---
            col_raw, col_clean = st.columns(2)
            with col_raw:
                st.error("❌ Original 'Dirty' Data")
                st.dataframe(df.head(10))
            with col_clean:
                st.success("✨ AI-Cleaned 'Gold' Data")
                st.dataframe(cleaned_df.head(10))

            # Metric: Show how many "Fixes" were made
            total_nulls_fixed = df.isnull().sum().sum() - cleaned_df.isnull().sum().sum()
            st.metric("Data Health Improvement", f"+{total_nulls_fixed} Nulls Repaired")
            
            # Download link
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Cleaned Results", data=csv, file_name="cleaned_data.csv", mime="text/csv")

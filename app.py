import streamlit as st
import pandas as pd
from groq import Groq
import os

# 1. Setup
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="AI Data Janitor Pro", layout="wide", page_icon="🧹")
st.title("🧹 AI Data Janitor Pro")
st.markdown("### Universal Data Quality Pipeline (Type-Based Cleaning)")

# Sidebar for Branding
st.sidebar.title("Developer Profile")
st.sidebar.write("**Tajwar Fahmid**")
st.sidebar.caption("B.S. Data Science | UTA")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/tajwar-fahmid/)") # Replace with your actual link

uploaded_file = st.file_uploader("Upload any CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    tab1, tab2 = st.tabs(["📊 Initial Audit", "✨ Universal Cleaning"])
    
    with tab1:
        st.write("#### 🔍 Raw Data Health")
        c1, c2 = st.columns([2, 1])
        c1.dataframe(df)
        with c2:
            st.write("**Missing Values per Column:**")
            st.write(df.isnull().sum())
            st.write(f"**Total Rows:** {len(df)}")

    with tab2:
        if st.button("🚀 Execute Universal Pipeline"):
            cleaned_df = df.copy()
            
            # 0. Global Duplicate Removal
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Define a more aggressive list of "Bad Data" strings
            fake_nulls = ['nan', 'Nan', 'NAN', 'None', 'none', 'NULL', 'null', '?', 'N/A', 'n/a', '', 'ERROR', 'UNKNOWN']
            
            for col in cleaned_df.columns:
                # --- STEP A: STRIP & UNIFY FAKE NULLS ---
                # This ensures "  ERROR  " becomes a real Null (NaN)
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip().replace(fake_nulls, pd.NA)

                # --- STEP B: ATTEMPT NUMERIC CONVERSION ---
                # We try to turn the column into numbers. If it works for >50% of the data, 
                # we treat it as a numeric column.
                converted_numeric = pd.to_numeric(cleaned_df[col], errors='coerce')
                
                if converted_numeric.notnull().sum() > (len(cleaned_df) * 0.5):
                    # --- RULE 1: NUMERIC LOGIC ---
                    cleaned_df[col] = converted_numeric
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    
                    # Outlier Capping (IQR)
                    q1, q3 = cleaned_df[col].quantile(0.25), cleaned_df[col].quantile(0.75)
                    iqr = q3 - q1
                    cleaned_df[col] = cleaned_df[col].clip(lower=q1 - 1.5*iqr, upper=q3 + 1.5*iqr)
                
                elif 'date' in col.lower() or 'time' in col.lower():
                    # --- RULE 2: DATETIME LOGIC ---
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    # Fill missing dates with the most common date
                    if cleaned_df[col].isnull().any():
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
                
                else:
                    # --- RULE 3: CATEGORICAL/TEXT LOGIC ---
                    cleaned_df[col] = cleaned_df[col].str.title()
                    if cleaned_df[col].isnull().any():
                        valid_modes = cleaned_df[col].dropna().mode()
                        mode_val = valid_modes[0] if not valid_modes.empty else "Unknown"
                        cleaned_df[col] = cleaned_df[col].fillna(mode_val)

            st.success("✅ Universal Pipeline Complete!")

            # Download link
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Validated CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

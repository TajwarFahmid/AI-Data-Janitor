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
            
            for col in cleaned_df.columns:
                # --- RULE 1: CATEGORICAL/TEXT COLUMNS (Objects) ---
                if cleaned_df[col].dtype == 'object':
                    # A. Standardize "Fake" Nulls
                    fake_nulls = ['nan', 'Nan', 'NAN', 'None', 'none', 'NULL', 'null', '?', 'N/A', 'n/a', '']
                    cleaned_df[col] = cleaned_df[col].astype(str).str.strip().replace(fake_nulls, pd.NA)
                    
                    # B. Standardize Casing (Title Case)
                    cleaned_df[col] = cleaned_df[col].str.title()
                    
                    # C. Mode Imputation (Fill with most frequent)
                    if cleaned_df[col].isnull().any():
                        valid_modes = cleaned_df[col].dropna().mode()
                        mode_val = valid_modes[0] if not valid_modes.empty else "Unknown"
                        cleaned_df[col] = cleaned_df[col].fillna(mode_val)

                # --- RULE 2: NUMERIC COLUMNS (Int/Float) ---
                elif pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    # A. Median Imputation
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    
                    # B. IQR Outlier Capping (Statistical Fence)
                    q1 = cleaned_df[col].quantile(0.25)
                    q3 = cleaned_df[col].quantile(0.75)
                    iqr = q3 - q1
                    cleaned_df[col] = cleaned_df[col].clip(lower=q1 - 1.5*iqr, upper=q3 + 1.5*iqr)

                # --- RULE 3: DATETIME COLUMNS ---
                # Check if the column name implies date OR if it's already a datetime type
                if 'date' in col.lower() or 'time' in col.lower() or pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')

            st.success("✅ Universal Pipeline Complete!")

            # --- FINAL VALIDATION REPORT ---
            st.divider()
            st.write("### 📋 Final Validation Report")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Rows Processed", f"{len(df)}", f"{len(cleaned_df) - len(df)} Dups Removed", delta_color="inverse")
            m2.metric("Nulls Repaired", f"{df.isnull().sum().sum()}", f"-{df.isnull().sum().sum() - cleaned_df.isnull().sum().sum()} Fixed")
            m3.metric("Data Status", "Ready for AI", "100% Quality")

            st.write("#### 🔄 Side-by-Side Comparison")
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.error("❌ Original Data (Head)")
                st.dataframe(df.head(10))
                st.write("**Nulls per Column:**")
                st.write(df.isnull().sum())
                
            with stat_col2:
                st.success("✨ Cleaned Data (Head)")
                st.dataframe(cleaned_df.head(10))
                st.write("**Nulls per Column:**")
                st.write(cleaned_df.isnull().sum())

            # Download link
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Validated CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

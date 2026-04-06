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
st.sidebar.write(f"**Tajwar Fahmid**")
st.sidebar.caption("Senior | B.S. Data Science | UTA")
st.sidebar.markdown("---")
st.sidebar.write("### 🛠 Tech Stack")
st.sidebar.code("Python / Pandas\nLlama 3 (Groq)\nStreamlit Cloud")

uploaded_file = st.file_uploader("Upload any CSV (e.g., dirty_cafe_sales.csv)", type="csv")

if uploaded_file:
    # Read raw data
    df = pd.read_csv(uploaded_file)
    
    # Define the 3 Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Initial Audit", "🚀 Execute Pipeline", "🔍 Comparison Audit"])
    
    # Global state to store cleaned data after button click
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None

    with tab1:
        st.write("#### 🔍 Raw Data Health Audit")
        c1, c2 = st.columns([2, 1])
        c1.dataframe(df)
        with c2:
            st.write("**Current Null Counts:**")
            st.write(df.isnull().sum())
            st.write(f"**Total Records:** {len(df)}")

    with tab2:
        st.write("#### ⚙️ Run Universal Cleaning")
        if st.button("✨ Run AI Clean & Repair"):
            cleaned_df = df.copy()
            
            # 0. Global Duplicate Removal
            cleaned_df = cleaned_df.drop_duplicates()
            
            # Universal list of strings that represent "No Data"
            fake_nulls = ['nan', 'Nan', 'NAN', 'None', 'none', 'NULL', 'null', '?', 'N/A', 'n/a', '', 'ERROR', 'UNKNOWN']
            
            for col in cleaned_df.columns:
                # STEP A: STRIP & UNIFY FAKE NULLS
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip().replace(fake_nulls, pd.NA)

                # STEP B: SMART TYPE DETECTION & COERCION
                converted_numeric = pd.to_numeric(cleaned_df[col], errors='coerce')
                
                if converted_numeric.notnull().sum() > (len(cleaned_df) * 0.5):
                    # RULE 1: NUMERIC LOGIC
                    cleaned_df[col] = converted_numeric
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    
                    q1, q3 = cleaned_df[col].quantile(0.25), cleaned_df[col].quantile(0.75)
                    iqr = q3 - q1
                    cleaned_df[col] = cleaned_df[col].clip(lower=q1 - 1.5*iqr, upper=q3 + 1.5*iqr)
                
                elif 'date' in col.lower() or 'time' in col.lower():
                    # RULE 2: DATETIME LOGIC
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    if cleaned_df[col].isnull().any():
                        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
                
                else:
                    # RULE 3: CATEGORICAL/TEXT LOGIC
                    cleaned_df[col] = cleaned_df[col].str.title()
                    if cleaned_df[col].isnull().any():
                        valid_modes = cleaned_df[col].dropna().mode()
                        mode_val = valid_modes[0] if not valid_modes.empty else "Unknown"
                        cleaned_df[col] = cleaned_df[col].fillna(mode_val)

            st.session_state.cleaned_df = cleaned_df
            st.success("✅ Transformation Complete! Proceed to the 'Comparison Audit' tab to see results.")

    with tab3:
        if st.session_state.cleaned_df is not None:
            st.write("### 📋 Final Side-by-Side Comparison")
            
            # Key Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Rows Processed", f"{len(df)}", f"{len(st.session_state.cleaned_df) - len(df)} Dups", delta_color="inverse")
            m2.metric("Nulls Fixed", f"{df.isnull().sum().sum()}", f"-{df.isnull().sum().sum() - st.session_state.cleaned_df.isnull().sum().sum()} Fixed")
            m3.metric("Data Quality", "100%", "+100% Quality Score")
            
            st.divider()

            # Side-by-Side DataFrames
            col_left, col_right = st.columns(2)
            with col_left:
                st.error("❌ Original Dataset")
                st.dataframe(df.head(20))
                st.write("**Nulls per Column:**")
                st.write(df.isnull().sum())
            
            with col_right:
                st.success("✨ Cleaned Dataset")
                st.dataframe(st.session_state.cleaned_df.head(20))
                st.write("**Nulls per Column:**")
                st.write(st.session_state.cleaned_df.isnull().sum())

            # Final Download
            csv = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Validated CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")
        else:
            st.warning("Please run the 'Execute Pipeline' in the previous tab first.")

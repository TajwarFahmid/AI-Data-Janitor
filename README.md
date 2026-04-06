# 🧹 AI Data Janitor Pro: Universal Data Quality Pipeline
### *Automated Data Cleaning, Repair, and Validation Engine for AI-Ready Datasets*

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Groq](https://img.shields.io/badge/Llama_3-Groq-orange?style=for-the-badge)

## 🚀 Overview
The **AI Data Janitor Pro** is a schema-agnostic data engineering tool designed to transform "dirty" raw CSVs into high-integrity, model-ready datasets. Developed as a Senior Capstone project at the **University of Texas at Arlington**, this application automates the most time-consuming stages of the ETL (Extract, Transform, Load) process.

## ✨ Core Features
* **Universal Type-Coercion:** Automatically identifies numeric columns masked as objects (due to "ERROR" or "NULL" strings) and forces safe conversion.
* **Statistical Repair (IQR Logic):** Implements **Winsorization** to cap 99th-percentile outliers using the Interquartile Range method.
* **Smart Imputation:** * *Numeric:* Median-based filling to preserve distribution despite outliers.
    * *Categorical:* Mode-based filling to handle missing "Unknown" strings.
* **Audit-Ready Comparison:** A dedicated **Comparison Audit** tab providing a head-to-head statistical breakdown of Data Health before and after processing.
* **Duplicate Extermination:** Global row-level de-duplication to ensure data uniqueness.

## 🛠 Tech Stack
* **Frontend:** Streamlit (Cloud Deployed)
* **Backend:** Python / Pandas
* **Inference:** Groq API (Llama 3 8B) for metadata analysis
* **Statistics:** Numpy / Scipy (IQR Method)

## 📊 How to Use
1.  **Upload:** Drop any "dirty" CSV (Cafe Sales, Real Estate, etc.).
2.  **Audit:** View initial null counts and data types.
3.  **Execute:** Run the Universal Pipeline to repair corrupted strings ("ERROR", "UNKNOWN").
4.  **Validate:** Compare the side-by-side results and download your cleaned **Gold-Standard** CSV.

---
**Developed by:** Tajwar Fahmid | B.S. Data Science, UT Arlington (2026)

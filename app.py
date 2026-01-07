import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="URL Extractor", layout="wide")

st.title("📂 URL & Company Extractor")

st.markdown("""
Upload a CSV or JSON file to extract 'Company Name' and 'URL' information.
""")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "json"])

if uploaded_file is not None:
    try:
        # Load the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)

        st.success(f"Successfully loaded {uploaded_file.name}")
        
        # Column detection
        columns = df.columns.tolist()
        
        # Heuristics for auto-detection
        company_col_candidate = next((col for col in columns if 'company' in col.lower() or 'name' in col.lower()), None)
        url_col_candidate = next((col for col in columns if 'url' in col.lower() or 'website' in col.lower() or 'link' in col.lower()), None)

        st.subheader("Select Columns")
        col1, col2 = st.columns(2)
        
        with col1:
            company_col = st.selectbox(
                "Select 'Company Name' column", 
                options=columns, 
                index=columns.index(company_col_candidate) if company_col_candidate else 0
            )
            
        with col2:
            url_col = st.selectbox(
                "Select 'URL' column", 
                options=columns, 
                index=columns.index(url_col_candidate) if url_col_candidate else 0
            )

        if company_col and url_col:
            # Filter and display data
            result_df = df[[company_col, url_col]].dropna()
            
            st.divider()
            st.subheader("Extracted Data")
            st.dataframe(result_df, use_container_width=True)
            
            # Download button
            csv = result_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"extracted_{uploaded_file.name.split('.')[0]}.csv",
                mime='text/csv',
            )
            
    except Exception as e:
        st.error(f"Error processing file: {e}")

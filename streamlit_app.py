import streamlit as st
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="Company Data Extractor", layout="wide")

st.title("📊 Company Data Extractor")
st.markdown("Upload a JSON or CSV file to extract company names and URLs")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['json', 'csv'])

def find_matching_columns(columns, keywords):
    """Find columns that match given keywords (case-insensitive)"""
    for col in columns:
        for keyword in keywords:
            if keyword.lower() in col.lower():
                return col
    return None

def parse_file(file):
    """Parse uploaded file and return a DataFrame"""
    try:
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'csv':
            df = pd.read_csv(file)
        elif file_type == 'json':
            content = file.read().decode('utf-8')
            data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a dict, try to find the main data array
                if len(data) == 1:
                    df = pd.DataFrame(list(data.values())[0])
                else:
                    df = pd.DataFrame([data])
            else:
                st.error("Unsupported JSON structure")
                return None
            
        return df
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return None

if uploaded_file is not None:
    df = parse_file(uploaded_file)
    
    if df is not None and not df.empty:
        st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Try to automatically find company name and URL columns
        company_keywords = ['company', 'name', 'business', 'organization', 'org', 'title']
        url_keywords = ['url', 'website', 'link', 'site', 'web', 'joburl']
        
        auto_company_col = find_matching_columns(df.columns, company_keywords)
        auto_url_col = find_matching_columns(df.columns, url_keywords)
        
        # Column selection section
        st.subheader("📋 Column Selection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_col = st.selectbox(
                "Select Company Name Column",
                options=['None'] + list(df.columns),
                index=list(['None'] + list(df.columns)).index(auto_company_col) if auto_company_col else 0,
                key='company_selector'
            )
        
        with col2:
            url_col = st.selectbox(
                "Select URL/Website Column",
                options=['None'] + list(df.columns),
                index=list(['None'] + list(df.columns)).index(auto_url_col) if auto_url_col else 0,
                key='url_selector'
            )
        
        # Extract and display results
        if company_col != 'None' or url_col != 'None':
            st.subheader("✨ Extracted Data")
            
            # Create result dataframe
            result_data = {}
            
            if company_col != 'None':
                result_data['Company Name'] = df[company_col]
            
            if url_col != 'None':
                result_data['URL'] = df[url_col]
            
            result_df = pd.DataFrame(result_data)
            
            # Remove rows where all values are NaN
            result_df = result_df.dropna(how='all')
            
            # Remove duplicate rows
            result_df = result_df.drop_duplicates()
            
            # Display summary metrics
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Records", len(result_df))
            with col_m2:
                st.metric("Unique Entries", len(result_df))
            with col_m3:
                if 'URL' in result_df.columns:
                    valid_urls = result_df['URL'].notna().sum()
                    st.metric("Valid URLs", valid_urls)
            
            # Display table with better formatting
            st.dataframe(
                result_df, 
                use_container_width=True, 
                height=400,
                column_config={
                    "URL": st.column_config.LinkColumn("URL"),
                }
            )
            
            # Download section
            st.subheader("💾 Download Results")
            
            # Prepare CSV
            csv = result_df.to_csv(index=False)
            
            col_d1, col_d2 = st.columns([1, 3])
            
            with col_d1:
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="company_data_extracted.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_d2:
                st.info(f"Ready to download {len(result_df)} records")
        
        else:
            st.warning("⚠️ Please select at least one column to display.")
        
        # Show preview of original data
        with st.expander("📋 View Original Data Preview"):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Showing first 10 of {len(df)} rows")
    
    elif df is not None:
        st.warning("The uploaded file appears to be empty.")

else:
    st.info("👆 Please upload a JSON or CSV file to get started.")
    
    # Sample data format info
    with st.expander("ℹ️ Supported File Formats & Examples"):
        st.markdown("""
        ### CSV Example:
        ```
        Company Name,URL,Other Info
        Acme Corp,https://acme.com,Info
        Tech Inc,https://techinc.com,Info
        ```
        
        ### JSON Example (Array of Objects):
        ```json
        [
            {
                "title": "Job Title",
                "jobUrl": "https://example.com/job1"
            },
            {
                "title": "Another Job",
                "jobUrl": "https://example.com/job2"
            }
        ]
        ```
        
        ### JSON Example (Nested Object):
        ```json
        {
            "data": [
                {"company": "Acme Corp", "website": "https://acme.com"},
                {"company": "Tech Inc", "website": "https://techinc.com"}
            ]
        }
        ```
        
        ---
        
        **Automatic Column Detection:**
        - **Company Name**: Looks for columns containing "company", "name", "business", "title", "organization"
        - **URL**: Looks for columns containing "url", "website", "link", "site", "web", "joburl"
        
        If automatic detection doesn't work, you can manually select the correct columns from the dropdown menus.
        """)

st.markdown("---")
st.markdown("Built with Streamlit | 🚀 Upload • 🔍 Extract • 💾 Download")

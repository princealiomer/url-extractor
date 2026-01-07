import streamlit as st
import pandas as pd
import json
import re
from io import StringIO

st.set_page_config(page_title="Company Data Extractor", layout="wide")

st.title("📊 Company Data Extractor")
st.markdown("Upload a JSON or CSV file to extract job titles and URLs from text content")

def extract_urls_from_text(text):
    """Extract URLs from text content"""
    if pd.isna(text) or not isinstance(text, str):
        return []
    
    # Pattern to match URLs (http/https and common domains without protocol)
    url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?(?:/[^\s]*)?)'
    
    urls = re.findall(url_pattern, text)
    
    # Clean and filter URLs
    cleaned_urls = []
    exclude_domains = ['upwork.com', 'example.com', 'google.com', 'facebook.com', 'twitter.com', 'linkedin.com']
    
    for url in urls:
        # Remove trailing punctuation
        url = re.sub(r'[.,;:)\]]+$', '', url)
        
        # Skip if it's an excluded domain or robots.txt
        if any(domain in url.lower() for domain in exclude_domains) or 'robots.txt' in url.lower():
            continue
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        cleaned_urls.append(url)
    
    return list(set(cleaned_urls))  # Remove duplicates

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

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['json', 'csv'])

if uploaded_file is not None:
    df = parse_file(uploaded_file)
    
    if df is not None and not df.empty:
        st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Auto-detect columns
        company_keywords = ['company', 'name', 'business', 'organization', 'org', 'title']
        text_keywords = ['description', 'content', 'text', 'body', 'details']
        
        auto_company_col = find_matching_columns(df.columns, company_keywords)
        auto_text_col = find_matching_columns(df.columns, text_keywords)
        
        # Column selection section
        st.subheader("📋 Column Selection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_col = st.selectbox(
                "Select Job Title Column",
                options=['None'] + list(df.columns),
                index=list(['None'] + list(df.columns)).index(auto_company_col) if auto_company_col else 0,
                key='company_selector',
                help="Column containing company/job titles"
            )
        
        with col2:
            text_col = st.selectbox(
                "Select Text Column (for URL extraction)",
                options=['None'] + list(df.columns),
                index=list(['None'] + list(df.columns)).index(auto_text_col) if auto_text_col else 0,
                key='text_selector',
                help="Column containing descriptions or text with URLs"
            )
        
        # Option to extract URLs from text
        st.subheader("🔍 URL Extraction Options")
        
        extract_from_text = st.checkbox(
            "Extract URLs from text content",
            value=True,
            help="Automatically extract company websites mentioned in descriptions"
        )
        
        # Extract and display results
        if company_col != 'None' or text_col != 'None':
            st.subheader("✨ Extracted Data")
            
            # Create result dataframe
            result_data = {}
            
            if company_col != 'None':
                result_data['Job Title'] = df[company_col]
            
            # Extract URLs from text if enabled
            if extract_from_text and text_col != 'None':
                with st.spinner('Extracting URLs from text...'):
                    extracted_urls = df[text_col].apply(extract_urls_from_text)
                    result_data['Extracted URLs'] = extracted_urls.apply(lambda x: ', '.join(x) if x else '')
            
            result_df = pd.DataFrame(result_data)
            
            # Remove rows where all values are empty
            result_df = result_df.replace('', pd.NA)
            result_df = result_df.dropna(how='all')
            
            # Display summary metrics
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Records", len(result_df))
            with col_m2:
                if 'Extracted URLs' in result_df.columns:
                    records_with_urls = (result_df['Extracted URLs'].notna() & (result_df['Extracted URLs'] != '')).sum()
                    st.metric("Records with URLs", records_with_urls)
            with col_m3:
                if 'Extracted URLs' in result_df.columns:
                    total_urls = result_df['Extracted URLs'].str.split(', ').apply(lambda x: len([i for i in x if i]) if isinstance(x, list) else 0).sum()
                    st.metric("Total URLs Found", int(total_urls))
            
            # Display table
            st.dataframe(
                result_df, 
                use_container_width=True, 
                height=400
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
            
            # Show sample of extracted URLs
            if 'Extracted URLs' in result_df.columns:
                with st.expander("🔗 Sample Extracted URLs"):
                    sample_urls = result_df[result_df['Extracted URLs'].notna() & (result_df['Extracted URLs'] != '')].head(10)
                    if not sample_urls.empty:
                        for idx, row in sample_urls.iterrows():
                            st.write(f"**{row.get('Job Title', 'N/A')}**")
                            urls = [u.strip() for u in str(row['Extracted URLs']).split(',') if u.strip()]
                            for url in urls:
                                st.write(f"  • {url}")
                    else:
                        st.write("No URLs found in the selected text column")
        
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
    with st.expander("ℹ️ How URL Extraction Works"):
        st.markdown("""
        ### Automatic URL Extraction
        
        This app can **automatically extract company websites** mentioned in text content like job descriptions.
        
        **Example:**
        If your data contains:
        ```
        "We at http://veliovgroup.com specialize in technical SEO..."
        ```
        
        The app will extract: `https://veliovgroup.com`
        
        ---
        
        ### Features:
        - ✅ Extracts URLs from any text field (descriptions, content, etc.)
        - ✅ Automatically adds `https://` if missing
        - ✅ Filters out common platforms (Upwork, Facebook, LinkedIn, etc.)
        - ✅ Removes duplicate URLs
        - ✅ Handles both `http://` and `https://` URLs
        
        ---
        
        ### Supported Formats:
        - **CSV files** with company names and descriptions
        - **JSON files** with arrays of objects containing text fields
        
        ### Column Detection:
        - **Job Title**: Looks for "company", "name", "title", "business"
        - **Text Content**: Looks for "description", "content", "text", "details"
        
        You can always manually select different columns if auto-detection doesn't work.
        """)

st.markdown("---")
st.markdown("Built with Streamlit | 🚀 Upload • 🔍 Extract URLs • 💾 Download")

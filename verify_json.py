import pandas as pd
import json

file_path = "d:/url-extractor/upwork_jobs_1767712772953.json"
print(f"Loading {file_path}...")

try:
    df = pd.read_json(file_path)
    print(f"Successfully loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    columns = df.columns.tolist()
    
    # Simulate auto-detection
    company_col_candidate = next((col for col in columns if 'company' in col.lower() or 'name' in col.lower()), None)
    url_col_candidate = next((col for col in columns if 'url' in col.lower() or 'website' in col.lower() or 'link' in col.lower()), None)
    
    print(f"Auto-detected Company Column: {company_col_candidate}")
    print(f"Auto-detected URL Column: {url_col_candidate}")
    
    # Simulate extraction with manual selection if needed (e.g. using 'title' and 'jobUrl')
    # If auto-detection fails for company, we'll assume user picks 'title'
    selected_company_col = company_col_candidate if company_col_candidate else 'title'
    selected_url_col = url_col_candidate if url_col_candidate else 'jobUrl'
    
    print(f"Selected Company Column: {selected_company_col}")
    print(f"Selected URL Column: {selected_url_col}")
    
    if selected_company_col in df.columns and selected_url_col in df.columns:
        result = df[[selected_company_col, selected_url_col]].dropna().head(5)
        print("First 5 extracted rows:")
        print(result)
    else:
        print("Could not find selected columns in dataframe.")

except Exception as e:
    print(f"Error: {e}")

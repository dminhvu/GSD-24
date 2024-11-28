import streamlit as st
import pandas as pd
import io

# Invoice type conversion dictionary
INVOICE_TYPE_MAP = {
    'PM': 'Regular Charges',
    'T&M': 'T&M Billing - R3',
    'Projects': 'Constr Proj - R3',
    'Quote': 'QTN Billing - R3'
}

def convert_excel_to_csv(df):
    """
    Convert Excel dataframe according to specified transformation rules
    """
    # Create new dataframe with required columns
    new_df = pd.DataFrame()
    
    # 1st column: Debtor Reference
    new_df['Debtor Reference'] = df['Custome'].astype(str) + '_' + df['Invoice Type'].map(INVOICE_TYPE_MAP)
    
    # 2nd column: Transaction Type
    new_df['Transaction Type'] = df['Amount in Company Code Currency'].apply(
        lambda x: 'INV' if x >= 0 else 'CRD'
    )
    
    # 3rd column: Document Number
    new_df['Document Number'] = df['Reference Document'].astype(str)
    
    # 4th column: Document Date (convert to DD/MM/YYYY)
    new_df['Document Date'] = pd.to_datetime(df['Posting Date']).dt.strftime('%d/%m/%Y')
    
    # 5th column: Document Balance
    new_df['Document Balance'] = df['Amount in Company Code Currency'].apply(lambda x: f'{x:.2f}')
    
    return new_df

def main():
    st.title('Ledger Upload Reformatting Tool')
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Read file
        try:
            df = pd.read_excel(uploaded_file)
            st.write("### Original Data Preview")
            st.dataframe(df)
            
            # Transformation steps explanation
            with st.expander("Transformation Steps"):
                st.markdown("""
                1. **Debtor Reference**: 
                   - Combines Customer Code with converted Invoice Type
                   - Conversion mapping:
                     - PM → Regular Charges
                     - T&M → T&M Billing - R3
                     - Projects → Constr Proj - R3
                     - Quote → QTN Billing - R3
                
                2. **Transaction Type**:
                   - 'INV' if Amount ≥ 0
                   - 'CRD' if Amount < 0
                
                3. **Document Number**:
                   - Uses Reference Document from original file
                
                4. **Document Date**:
                   - Converted to DD/MM/YYYY format
                
                5. **Document Balance**:
                   - Uses Amount in Company Code Currency
                """)
            
            # Convert dataframe
            converted_df = convert_excel_to_csv(df)
            
            st.write("### Converted Data Preview")
            st.dataframe(converted_df)
            
            # Download button
            output = io.BytesIO()
            converted_df.to_csv(output, index=False)
            output.seek(0)
            
            st.download_button(
                label="Download Converted CSV",
                data=output,
                file_name='converted_data.csv',
                mime='text/csv'
            )
        
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == '__main__':
    main()
import streamlit as st
import requests
import pandas as pd
import logging
from PIL import Image
import io
import json
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = 'http://localhost:5000/api/v1'

def main():
    st.set_page_config(
        page_title="Bank Check Parser",
        page_icon="🏦",
        layout="wide"
    )
    
    # Header with author info
    st.title("🏦 Bank Check Parser (ABC Parser)")
    st.markdown("### Developed by Bechir Mathlouthi")
    st.markdown("---")
    
    st.sidebar.title("Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a page", 
        ["Upload Check", "View History"]
    )
    
    if page == "Upload Check":
        show_upload_page()
    else:
        show_history_page()
        
    # Footer
    st.markdown("---")
    st.markdown("© 2024 Bechir Mathlouthi | [GitHub](https://github.com/Bechir-Mathlouthi)")

def show_upload_page():
    st.header("Upload Check Image")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a check image...", 
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Supported formats: JPG, JPEG, PNG, PDF"
    )
    
    if uploaded_file is not None:
        # Log file details
        logger.info(f"File uploaded: {uploaded_file.name} (type: {uploaded_file.type})")
        
        # Display the uploaded image
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption='Uploaded Check', use_column_width=True)
        elif uploaded_file.type == 'application/pdf':
            st.info("PDF file uploaded. Preview not available for PDF files.")
        
        if st.button("Process Check"):
            with st.spinner('Processing check...'):
                try:
                    # Prepare the file for upload
                    files = {
                        'file': (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }
                    
                    # Log request details
                    logger.debug(f"Sending request to: {API_BASE_URL}/checks/upload")
                    
                    # Send to API
                    response = requests.post(
                        f'{API_BASE_URL}/checks/upload',
                        files=files
                    )
                    
                    # Log response
                    logger.debug(f"Response status: {response.status_code}")
                    logger.debug(f"Response content: {response.text}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Check processed successfully!")
                        
                        # Display results in a nice format
                        st.subheader("📄 Extracted Information")
                        check_data = result['check_data']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Amount", f"${check_data.get('amount_numeric', 0):,.2f}")
                            st.metric("Date", check_data.get('date', 'N/A'))
                            st.metric("Bank Code", check_data.get('bank_code', 'N/A'))
                        
                        with col2:
                            st.metric("Account Number", check_data.get('account_number', 'N/A'))
                            st.metric("Check Number", check_data.get('check_number', 'N/A'))
                            
                        # Security Analysis
                        st.subheader("🔒 Security Analysis")
                        fraud_status = "🚨 Suspicious" if check_data.get('fraud_detected', False) else "✅ Valid"
                        signature_status = "✅ Verified" if check_data.get('signature_verified', False) else "❌ Not Verified"
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Fraud Detection", fraud_status)
                        with col4:
                            st.metric("Signature Status", signature_status)
                            
                    else:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', 'Unknown error occurred')
                        except:
                            if response.status_code == 404:
                                error_msg = "API endpoint not found"
                            elif response.status_code == 500:
                                error_msg = "Server error"
                            else:
                                error_msg = f"Error {response.status_code}"
                        
                        st.error(f"❌ {error_msg}")
                        logger.error(f"Error response: {error_msg}")
                        
                except requests.exceptions.ConnectionError:
                    error_msg = "Could not connect to the server. Please make sure the Flask server is running."
                    st.error(f"❌ {error_msg}")
                    logger.error(error_msg)
                except Exception as e:
                    error_msg = f"An unexpected error occurred: {str(e)}"
                    st.error(f"❌ {error_msg}")
                    logger.error(error_msg)

def show_history_page():
    st.header("Check Processing History")
    
    try:
        with st.spinner('Loading check history...'):
            response = requests.get(f'{API_BASE_URL}/checks')
            
            if response.status_code == 200:
                checks = response.json()
                if checks:
                    # Convert to DataFrame and format
                    df = pd.DataFrame(checks)
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['amount_numeric'] = df['amount_numeric'].apply(lambda x: f"${x:,.2f}")
                    
                    # Display with formatting
                    st.dataframe(
                        df,
                        column_config={
                            "created_at": "Date Created",
                            "amount_numeric": "Amount",
                            "check_number": "Check #",
                            "fraud_detected": "Fraud Detected",
                            "signature_verified": "Signature Verified"
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No processed checks found in the database.")
            else:
                error_msg = "Failed to load check history"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                st.error(f"❌ {error_msg}")
                
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to the server. Please make sure the Flask server is running.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 
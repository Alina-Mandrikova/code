import os
import streamlit as st
from PIL import Image
import openai

from datetime import datetime
import io

# Import your DataExtractor class here
from data_extraction import DataExtractor

# Get the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
else:
    openai.api_key = api_key

# Add custom CSS for better styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #A1B0F6;
    }}
    .title {{
        color: #223FC0;
        font-family: 'Arial';
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }}
    .upload-box {{
        border: 2px dashed #223FC0;
        padding: 20px;
        border-radius: 10px;
        background-color: #E0E5FB;
        margin-bottom: 20px;
    }}
    .sidebar .sidebar-content {{
        background-image: linear-gradient(#A1B0F6, #E0E5FB);
        color: black;
    }}
    .stButton>button {{
        background-color: #223FC0;
        color: white;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write("")
    
    with col2:
        st.image("logo.png", use_column_width=True)  # Display the high-resolution logo
        st.markdown('<div class="title">AI Contract Quitter</div>', unsafe_allow_html=True)
    
    with col3:
        st.write("")

    st.write("Upload an image or PDF of the contract, or input the contract text directly.")
    
    # Sidebar for customization options
    st.sidebar.title("Customization Options")
    analysis_depth = st.sidebar.selectbox("Select Analysis Depth", ["Basic", "Intermediate", "Advanced"])
    include_risk_assessment = st.sidebar.checkbox("Include Risk Assessment")
    
    upload_type = st.selectbox("Select input type", ["Image", "PDF", "Text"])
    
    data_extractor = DataExtractor(file_path=None, file_type=None, image_path=None)  # Initialize with placeholder values

    if upload_type == "Image":
        st.write("### Upload an Image")
        image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], help="Upload a contract image")
        if image_file:
            st.markdown('<div class="upload-box">', unsafe_allow_html=True)
            image = Image.open(image_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            data_extractor.image_path = image_file
            text = data_extractor.extract_text_from_image()
            if text:
                st.write("Extracted Text:", text)
                analysis_result = data_extractor.analyze_contract(text)
                data = data_extractor.analyze_and_extract_contract_info(text)
                if analysis_result:
                    st.write("Analysis Result:", analysis_result)
                    st.write("Extracted Data:", data)
                    if st.button("Generate Termination Contract"):
                        signature = data_extractor.generate_signature(data_extractor.get_name(data))
                        pdf = data_extractor.generate_termination_pdf(data, signature)
                        if pdf:
                            st.download_button("Download Termination Contract", pdf, file_name="termination_contract.pdf")

    elif upload_type == "PDF":
        st.write("### Upload a PDF")
        pdf_file = st.file_uploader("Upload a PDF", type=["pdf"], help="Upload a contract PDF")
        if pdf_file:
            st.markdown('<div class="upload-box">', unsafe_allow_html=True)
            data_extractor.file_path = pdf_file
            text = data_extractor.extract_text_from_pdf()
            if text:
                st.write("Extracted Text:", text)
                analysis_result = data_extractor.analyze_contract(text)
                data = data_extractor.analyze_and_extract_contract_info(text)
                if analysis_result:
                    st.write("Analysis Result:", analysis_result)
                    st.write("Extracted Data:", data)
                    if st.button("Generate Termination Contract"):
                        signature = data_extractor.generate_signature(data_extractor.get_name(data))
                        pdf = data_extractor.generate_termination_pdf(data, signature)
                        if pdf:
                            st.download_button("Download Termination Contract", pdf, file_name="termination_contract.pdf")

    else:
        st.write("### Input Text")
        text_input = st.text_area("Input the contract text", help="Paste the contract text here")
        if text_input:
            analysis_result = data_extractor.analyze_contract(text_input)
            data = data_extractor.analyze_and_extract_contract_info(text_input)
            if analysis_result:
                st.write("Analysis Result:", analysis_result)
                st.write("Extracted Data:", data)
                if st.button("Generate Termination Contract"):
                    signature = data_extractor.generate_signature(data_extractor.get_name(data))
                    pdf = data_extractor.generate_termination_pdf(data, signature)
                    if pdf:
                        st.download_button("Download Termination Contract", pdf, file_name="termination_contract.pdf")

if __name__ == "__main__":
    main()

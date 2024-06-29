from data_extraction import DataExtractor
import streamlit as st
import openai
import os
from PIL import Image


file_path = './termination_letter.pdf'
signature_path = './signature.png'
data_extractor = DataExtractor(file_path, 'pdf', None)

#if data_extractor.file_type == 'pdf':
text = data_extractor.extract_text_from_pdf()
extracted_info = data_extractor.analyze_and_extract_contract_info(text)
analysis_result = data_extractor.analyze_contract(extracted_info)
name = data_extractor.get_name(analysis_result)
signature = data_extractor.generate_signature(name)
termination_pdf = data_extractor.create_termination_pdf(analysis_result, signature)



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
    
    if upload_type == "Image":
        st.write("### Upload an Image")
        image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], help="Upload a contract image")
        if image_file:
            st.markdown('<div class="upload-box">', unsafe_allow_html=True)
            image = Image.open(image_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            text = extract_text_from_image(image)
            if text:
                st.write("Extracted Text:", text)
                analysis_result, data = analyze_contract(text, analysis_depth, include_risk_assessment)
                if analysis_result:
                    st.write("Analysis Result:", analysis_result)
                    st.write("Extracted Data:", data)
                    if st.button("Generate Termination Contract"):
                        if generate_termination_pdf(data):
                            st.success("Termination Contract generated: termination_contract.pdf")
    
    elif upload_type == "PDF":
        st.write("### Upload a PDF")
        pdf_file = st.file_uploader("Upload a PDF", type=["pdf"], help="Upload a contract PDF")
        if pdf_file:
            st.markdown('<div class="upload-box">', unsafe_allow_html=True)
            text = extract_text_from_pdf(pdf_file)
            if text:
                st.write("Extracted Text:", text)
                analysis_result, data = analyze_contract(text, analysis_depth, include_risk_assessment)
                if analysis_result:
                    st.write("Analysis Result:", analysis_result)
                    st.write("Extracted Data:", data)
                    if st.button("Generate Termination Contract"):
                        if generate_termination_pdf(data):
                            st.success("Termination Contract generated: termination_contract.pdf")
    
    else:
        st.write("### Input Text")
        text_input = st.text_area("Input the contract text", help="Paste the contract text here")
        if text_input:
            analysis_result, data = analyze_contract(text_input, analysis_depth, include_risk_assessment)
            if analysis_result:
                st.write("Analysis Result:", analysis_result)
                st.write("Extracted Data:", data)
                if st.button("Generate Termination Contract"):
                    if generate_termination_pdf(data):
                        st.success("Termination Contract generated: termination_contract.pdf")

if __name__ == "__main__":
    main()









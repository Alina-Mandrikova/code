import os
import streamlit as st
import openai
from data_extraction import DataExtractor


# Add custom CSS for better styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #A1B0F6;
    }
    .title {
        color: #223FC0;
        font-family: 'Arial';
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-box {
        border: 2px dashed #223FC0;
        padding: 20px;
        border-radius: 10px;
        background-color: #E0E5FB;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #223FC0;
        color: white;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("logo.png", use_column_width=True)
        st.markdown('<div class="title">AI Contract Quitter</div>', unsafe_allow_html=True)

    st.write("Upload a PDF of the contract for analysis.")
    
    data_extractor = DataExtractor(file_path=None, file_type=None, image_path=None)

    st.write("### Upload a PDF")
    pdf_file = st.file_uploader("Upload a PDF", type=["pdf"], help="Upload a contract PDF")
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
        st.session_state.analysis_attempts = 0

    if pdf_file:
        st.write(f"Uploaded: {pdf_file.name}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        data_extractor.file_path = pdf_file
        data_extractor.file_type = pdf_file.type
        
        if st.button("Analyze", key=f"analyze_button_{st.session_state.analysis_attempts}"):
            st.session_state.analysis_attempts += 1
            with st.spinner("Analyzing PDF..."):
                try:
                    text = data_extractor.extract_text_from_pdf()
                    if text:
                        st.write("Extracted text (first 500 characters):", text[:500])  # Display a preview of extracted text
                        try:
                            data = data_extractor.analyze_and_extract_contract_info(text)
                            if data:
                                st.write("Analysis Result:", data)
                                st.session_state.analysis_complete = True
                                if st.button("Accept Analysis"):
                                    st.success("Analysis accepted!")
                                    # Here you can add code to proceed with the next steps
                                if st.button("Retry Analysis"):
                                    st.session_state.analysis_complete = False
                                    st.experimental_rerun()
                            else:
                                st.error("Failed to extract structured data from the PDF. Raw text was extracted but could not be parsed.")
                        except Exception as e:
                            st.error(f"An error occurred in analyze_and_extract_contract_info: {str(e)}")
                            st.write("Debug: Text passed to analyze_and_extract_contract_info:", text[:1000])  # Show first 1000 characters
                    else:
                        st.error("Failed to extract any text from the PDF. The file may be empty or corrupted.")
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

        if not st.session_state.analysis_complete:
            st.info("You can press the 'Analyze' button again to retry the analysis.")
        else:
            st.success("Analysis completed successfully. You can accept the result or retry if needed.")

if __name__ == "__main__":
    main()
import streamlit as st
from PIL import Image
import pytesseract
import pdfplumber
from fpdf import FPDF
import openai

# Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def analyze_contract(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Analyze the following contract text and extract the key points for contract termination:\n\n{text}\n\n",
        max_tokens=500
    )
    analysis_result = response.choices[0].text.strip()
    # Simulate extracting structured data from the response (to be customized as per actual response)
    data = {
        "parties": "Extracted parties from analysis",
        "termination_clause": "Extracted termination clause from analysis",
        "effective_date": "Extracted effective date from analysis"
    }
    return data

def generate_termination_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = "Termination Contract", ln = True, align = 'C')
    pdf.cell(200, 10, txt = f"Parties: {data['parties']}", ln = True)
    pdf.cell(200, 10, txt = f"Termination Clause: {data['termination_clause']}", ln = True)
    pdf.cell(200, 10, txt = f"Effective Date: {data['effective_date']}", ln = True)
    pdf.output("termination_contract.pdf")

def main():
    st.title("AI Contract Quitter")
    st.write("Upload an image or PDF of the contract, or input the contract text directly.")
    
    upload_type = st.selectbox("Select input type", ["Image", "PDF", "Text"])
    
    if upload_type == "Image":
        image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if image_file:
            image = Image.open(image_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            text = extract_text_from_image(image)
            st.write("Extracted Text:", text)
            data = analyze_contract(text)
            st.write("Analysis Result:", data)
            if st.button("Generate Termination Contract"):
                generate_termination_pdf(data)
                st.success("Termination Contract generated: termination_contract.pdf")
    
    elif upload_type == "PDF":
        pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
        if pdf_file:
            text = extract_text_from_pdf(pdf_file)
            st.write("Extracted Text:", text)
            data = analyze_contract(text)
            st.write("Analysis Result:", data)
            if st.button("Generate Termination Contract"):
                generate_termination_pdf(data)
                st.success("Termination Contract generated: termination_contract.pdf")
    
    else:
        text_input = st.text_area("Input the contract text")
        if text_input:
            data = analyze_contract(text_input)
            st.write("Analysis Result:", data)
            if st.button("Generate Termination Contract"):
                generate_termination_pdf(data)
                st.success("Termination Contract generated: termination_contract.pdf")

if __name__ == "__main__":
    main()

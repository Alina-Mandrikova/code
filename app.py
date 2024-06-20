import streamlit as st
from PIL import Image
import pytesseract
import pdfplumber
from fpdf import FPDF
import openai

# Insert your OpenAI API key
openai.api_key = "Your API reference here"

def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error extracting text from image: {e}")
        return None

def extract_text_from_pdf(file):
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def analyze_contract(text, depth="Basic", risk_assessment=False):
    try:
        prompt = f"Analyze the following contract text with {depth} analysis and {'include' if risk_assessment else 'do not include'} risk assessment:\n\n{text}\n\n"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )
        analysis_result = response.choices[0].text.strip()
        # Simulate extracting structured data from the response (to be customized as per actual response)
        data = {
            "parties": "Extracted parties from analysis",
            "termination_clause": "Extracted termination clause from analysis",
            "effective_date": "Extracted effective date from analysis"
        }
        return analysis_result, data
    except Exception as e:
        st.error(f"Error analyzing contract: {e}")
        return None, None

def generate_termination_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Termination Contract", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Parties: {data['parties']}", ln=True)
        pdf.cell(200, 10, txt=f"Termination Clause: {data['termination_clause']}", ln=True)
        pdf.cell(200, 10, txt=f"Effective Date: {data['effective_date']}", ln=True)
        pdf.output("termination_contract.pdf")
        return True
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return False

def main():
    # Add custom CSS for better styling
    st



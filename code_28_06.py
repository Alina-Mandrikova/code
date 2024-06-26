import streamlit as st
from PIL import Image
import pytesseract
import pdfplumber
from fpdf import FPDF
import openai
import os
import requests
import io

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

def analyze_contract(text):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Analyze the following contract text and extract the contract party, contract number, date of birth, and quitting party:\n\n{text}\n\n"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500
        )
        analysis_result = response.choices[0].message["content"].strip()
        return analysis_result
    except Exception as e:
        print(f"Error analyzing contract: {e}")
        return None

def generate_signature(name):
    try:
        response = openai.Image.create(
            prompt=f"Handwritten signature of the name {name} in readable letters on white background",
            n=1,
            size="256x64"
        )
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        signature_path = "/tmp/signature.png"
        image.save(signature_path)
        return signature_path
    except Exception as e:
        st.error(f"Error generating signature: {e}")
        return None

def generate_termination_pdf(data, signature_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Termination Contract", ln=True, align='C')
        pdf.ln(10)
        
        static_text = """
        Kündigung zum nächstmöglichen Zeitpunkt           {data['effective_date']}

        Sehr geehrte Damen und Herren,

        hiermit kündige ich meinen Vertrag fristgerecht zum nächstmöglichen Zeitpunkt. 
        Bitte senden Sie mir eine schriftliche Bestätigung der Kündigung unter Angabe des Beendigungszeitpunktes zu.

        Mit freundlichen Grüßen
        """
        
        pdf.multi_cell(0, 10, static_text)
        pdf.ln(10)
        
        pdf.cell(200, 10, txt=f"Parties: {data['parties']}", ln=True)
        pdf.cell(200, 10, txt=f"Customer Number: {data['customer_number']}", ln=True)
        pdf.cell(200, 10, txt=f"Customer Name: {data['customer_name']}", ln=True)
        pdf.cell(200, 10, txt=f"Contract Type: {data['contract_type']}", ln=True)
        pdf.cell(200, 10, txt=f"Termination Clause: {data['termination_clause']}", ln=True)
        pdf.cell(200, 10, txt=f"Effective Date: {data['effective_date']}", ln=True)
        pdf.ln(20)
        pdf.cell(200, 10, txt="Sincerely,", ln=True)
        pdf.ln(20)
        if signature_path:
            pdf.image(signature_path, x=10, y=pdf.get_y(), w=60)
        pdf.output("/tmp/termination_contract.pdf")
        return True
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return False

def main():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write("")
    
    with col2:
        st.image("logo.png", use_column_width=True)  # Use the absolute path for the logo
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
            if text and st.button("Generate Termination Contract"):
                analysis_result, data = analyze_contract(text, analysis_depth, include_risk_assessment)
                if analysis_result:
                    signature_path = generate_signature(data.get('customer_name', ''))
                    if generate_termination_pdf(data, signature_path):
                        st.success("Termination Contract generated: termination_contract.pdf")
                        with open("/tmp/termination_contract.pdf", "rb") as f:
                            st.download_button("Download PDF", f, file_name="termination_contract.pdf")
    
    elif upload_type == "PDF":
        st.write("### Upload a PDF")
        pdf_file = st.file_uploader("Upload a PDF", type=["pdf"], help="Upload a contract PDF")
        if pdf_file:
            st.markdown('<div class="upload-box">', unsafe_allow_html=True)
            text = extract_text_from_pdf(pdf_file)
            if text and st.button("Generate Termination Contract"):
                analysis_result, data = analyze_contract(text, analysis_depth, include_risk_assessment)
                if analysis_result:
                    signature_path = generate_signature(data.get('customer_name', ''))
                    if generate_termination_pdf(data, signature_path):
                        st.success("Termination Contract generated: termination_contract.pdf")
                        with open("/tmp/termination_contract.pdf", "rb") as f:
                            st.download_button("Download PDF", f, file_name="termination_contract.pdf")
    
    elif upload_type == "Text":
        st.write("### Input Text")
        text = st.text_area("Input the contract text", help="Paste the contract text here")
        if text and st.button("Generate Termination Contract"):
            analysis_result, data = analyze_contract(text, analysis_depth, include_risk_assessment)
            if analysis_result:
                signature_path = generate_signature(data.get('customer_name', ''))
                if generate_termination_pdf(data, signature_path):
                    st.success("Termination Contract generated: termination_contract.pdf")
                    with open("/tmp/termination_contract.pdf", "rb") as f:
                        st.download_button("Download PDF", f, file_name="termination_contract.pdf")

if __name__ == "__main__":
    main()


import re
from PIL import Image
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from fpdf import FPDF
import openai
import os
from datetime import datetime
import requests
import streamlit as st
import io

#create class for data extraction
class DataExtractor:
    def __init__(self, file_path, file_type, image_path):
        self.file_path = file_path
        self.file_type = file_type
        self.image_path = None

    #extract text from image using pytesseract
    def extract_text_from_image(self):
        try:
            image = Image.open(self.image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return None
        
    def extract_text_from_pdf(self):
        try:
            text = ""
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
        
    def extract_contract_info(self, text):
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Analyze the following contract text and extract the name of the person as a quitting party, company with whom we want to cancel the contract, contract number, date of birth:\n\n{text}\n\n"}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500
            )
            analysis_result = response.choices[0].message["content"].strip()

            # Initialize the dictionary to store the extracted information
            extracted_info = {
                "company": [],
                "contract_number": [],
                "date_of_birth": [],
                "quitting_party": []
            }

            # Here, you can implement a parsing logic based on the expected format of analysis_result
            lines = analysis_result.split('\n')
            for line in lines:
                if "Company:" in line:
                    extracted_info["company"].append(line.split("Company:")[1].strip())
                if "Contract Number:" in line:
                    extracted_info["contract_number"].append(line.split("Contract Number:")[1].strip())
                if "Date of Birth:" in line:
                    extracted_info["date_of_birth"].append(line.split("Date of Birth:")[1].strip())
                if "Quitting Party:" in line:
                    extracted_info["quitting_party"].append(line.split("Quitting Party:")[1].strip())

            return extracted_info

        except Exception as e:
            print(f"Error analyzing contract: {e}")
            return None
    
    def analyze_and_extract_contract_info(self, text):
        try:
            # Define the messages for the API request
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Analyze the following contract text and extract the company, contract number, date of birth, and quitting party as a name of the person:\n\n{text}\n\n"}
            ]

            # Call the OpenAI API to analyze the contract text
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500
            )

            # Extract the response content
            analysis_result = response.choices[0].message["content"].strip()

            # Initialize the dictionary to store the extracted information
            extracted_info = {
                "company": [],
                "contract_number": [],
                "date_of_birth": [],
                "quitting_party": []
            }

            # Parsing logic based on the expected format of analysis_result
            lines = analysis_result.split('\n')
            for line in lines:
                if "Company:" in line:
                    extracted_info["company"].append(line.split("Company:")[1].strip())
                elif "Contract Number:" in line:
                    extracted_info["contract_number"].append(line.split("Contract Number:")[1].strip())
                elif "Date of Birth:" in line:
                    extracted_info["date_of_birth"].append(line.split("Date of Birth:")[1].strip())
                elif "Quitting Party:" in line:
                    extracted_info["quitting_party"].append(line.split("Quitting Party:")[1].strip())

            return extracted_info

        except Exception as e:
            print(f"Error analyzing contract: {e}")
            return None
        
    def analyze_contract(self, text):
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
        
    def generate_signature(self, name):
        prompt = (
            f"Generate a realistic handwritten signature for the name '{name}'. "
            "The signature should be elegant, clear, and written in a cursive style. "
            "The background should be transparent, and the signature should be centered "
            "with no additional text or decorations. Ensure that the handwriting appears "
            "natural and fluid, resembling an authentic signature."
        )

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256"
        )

        image_url = response['data'][0]['url']
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        
        # Convert image to binary format
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
    


    def generate_termination_pdf(data, signature_path_or_data):
        contract_number = data['contract_number'][0] if isinstance(data['contract_number'], list) and data['contract_number'] else ''
        company = data['company'][0] if isinstance(data['company'], list) and data['company'] else ''
        quitting_party = data['quitting_party'][0] if isinstance(data['quitting_party'], list) and data['quitting_party'] else ''
        
        date_pattern = re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b')
        if isinstance(data['date_of_birth'], list) and data['date_of_birth']:
            candidate = data['date_of_birth'][0]
            if date_pattern.match(candidate):
                date_of_birth = candidate
            else:
                date_of_birth = None
        else:
            date_of_birth = None

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add contract party information
            pdf.cell(200, 10, txt="", ln=True)  # Empty line

            # Add company and contract number information
            pdf.cell(200, 10, txt=f"{company}", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)
            pdf.cell(200, 10, txt="", ln=True)  # Empty line

            # Add contract number and date of birth information
            pdf.cell(200, 10, txt=f"Contract Number: {contract_number}", ln=True)

            if date_of_birth is not None:
                pdf.cell(200, 10, txt=f"Date of Birth: {date_of_birth}", ln=True)

            pdf.cell(200, 10, txt="", ln=True)  # Empty line

            # Add termination information
            pdf.set_font("Arial", size=14, style='B')
            pdf.cell(200, 10, txt="Termination at the next possible date", ln=True)
            pdf.set_font("Arial", size=12)
            today_date = datetime.today().strftime('%d.%m.%Y')
            pdf.cell(200, 10, txt=today_date, ln=True, align='R')
            pdf.cell(200, 10, txt="", ln=True)  # Empty line
            pdf.cell(200, 10, txt="", ln=True)  # Empty line

            # Add termination letter content
            pdf.multi_cell(200, 10, txt="Dear Sir or Madam,\n\n"
                                        "I hereby give notice of termination of my contract with effect from the next possible date. \n"
                                        "Please send me a written confirmation of the termination stating the date of termination.\n\n"
                                        "Never text here again.\n\n")
            pdf.set_font("Arial", size=16, style='B')
            pdf.cell(200, 10, txt=f"{quitting_party}", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"{quitting_party}", ln=True)

            # Handle signature image
            if isinstance(signature_path_or_data, str):
                # If it's a file path
                image_path = signature_path_or_data
            else:
                # If it's image data
                signature_io = io.BytesIO(signature_path_or_data)
                image = Image.open(signature_io)
                image_path = "signature_temp.png"
                image.save(image_path)

            pdf.ln(10)
            pdf.image(image_path, x=10, y=pdf.get_y(), w=50)

            # Save PDF to a binary stream
            pdf_output = io.BytesIO()
            pdf_content = pdf.output(dest='S').encode('latin1')
            pdf_output.write(pdf_content)
            pdf_output.seek(0)

            return pdf_output.read()

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None

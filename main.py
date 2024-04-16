from dotenv import load_dotenv
import streamlit as st
import json
import os
import pandas as pd
from PIL import Image
import google.generativeai as genai
load_dotenv()  # take environment variables from .env.
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

 
 
# Define CSS styles for the navbar
navbar_style = """
<style>
.navbar {
  overflow: hidden;
  background-color: #333;
  display: flex;
  justify-content: space-between;
}
 
.navbar a {
  float: left;
  display: block;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 20px;
  text-decoration: none;
  font-size: 17px;
}
 
.navbar a:hover {
  background-color: #ddd;
  color: black;
}
body {
    background-color: black;
    color: white; /* Set default text color to white */
}
 
/* Set background color of sidebar */
.sidebar .sidebar-content {
    background-color: black;
}
</style>
"""
 
# Display the navbar using st.markdown() with HTML/CSS
st.markdown(navbar_style, unsafe_allow_html=True)
 
# Define document details
document_details = {
    "Aadhar": '''Separate the name, dob, gender, Aadhar Number, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB :  DOB from the document
GENDER: Gender from the document
AADHAR Number : Passport number from the document
ADDRESS: Address from the document.''',
 
    "PAN": '''Separate the name, gender, dob, PAN Number, address(if found) with exclamatory mark(!) and returns the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
PAN Number : Passport number from the document
ADDRESS: Address from the document.''',
    "PASSPORT": '''Separate the name, dob, gender, Aadhar Number, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
Passport Number : Passport number from the document
ADDRESS: Address from the document.''',
 
    "Driving License": '''Separate the name, dob, gender, License Class(if found), License Number, License date of issue, License Date of expiry, Restrictions(if found), address(if found) with exclamatory mark(!) and returns the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
License Class : License class from the document
License Number: License number from the document
Date of issue : Date of issue from the document
Date of expiry: Date of expiry from the document
Restrictions : Restrictions from the document
ADDRESS: Address from the document.
''',
 
    "I-94": '''Separate the name, dob, gender, I94 Number, Address(if found) with exclamatory mark(!) and returns the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
I94 ID : I-94 number from the document
I94 class: Class of admit from the document
Date of entry: Date of entry from the document
Admit until date : Admit until date from the document
ADDRESS: Address from the document.''',
    "Void Check": '''Separate the name, Address(if found), Cheque date, Amount in the cheque, Routing number, Account number, Cheque number with exclamatory mark(!) and return it's text in capital letters from the image in this format only:
Name : Name from the cheque
ADDRESS : Address from the cheque
Cheque date : Cheque date from the cheque
Routing number : Routing number from the cheque
Account number :Account number from the cheque
Cheque number : Cheque number from the cheque.''',
    "Resume": '''Seperate the Name, Email, Mobile, Skills, Work Experience, Address with exclamatory mark(!) and return it's text from the given Resume in this format only:
    Name : Name from the Resume
    Email : Email from the Resume
    Mobile : Mobile number from the Resume
    Skills : Skills and Technologies from the Resume
    Work Experience: Work Experience details from the Resume
    Address : Address of the candidate from the Resume.'''
}
 
# Function to load OpenAI model and get response
def get_gemini_response(input, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    safe = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
    if input != "":
        response = model.generate_content([input, image], safety_settings=safe)
        print(response.prompt_feedback)
    else:
        response = model.generate_content(image)
        print(response.prompt_feedback)
    print(response.prompt_feedback)
    return response.text
 
# Preprocess function
def preprocess_output(output_text):
    details = {}
    lines = output_text.split('!')
    for line in lines:
        if line.strip():
            key_value = line.split(':')
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                details[key] = value if value else "No data available"
            else:
                key = key_value[0].strip()
                details[key] = "No data available"
    return details
 
# Function to process documents
def process_document(category, details_text, image):
    st.header(category)
    uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        submit = st.button("Submit")
        if submit:
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            response_text = get_gemini_response(details_text, image)
            if category!='Resume':
                details = preprocess_output(response_text)
                # Calculate maximum key length
                max_key_length = max(len(key) for key in details.keys()) if details else 0
 
                # Format the details with the calculated maximum key length
                formatted_details = ""
                for key, value in details.items():
                    padding = max_key_length - len(key) + 2  # Calculate padding based on key length
                    formatted_details += f"{key.ljust(max_key_length + padding)}: {value}\n"
 
                # Display the formatted details in the text area
                edited_details = st.text_area("Edit Details", value=formatted_details, height=300)
 
                # Convert edited details back to dictionary
                edited_details_dict = {}
                for line in edited_details.split("\n"):
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        edited_details_dict[key] = value
 
                # Update JSON download
                st.download_button(
                    label=f"Download {category} Details as JSON",
                    data=json.dumps(edited_details_dict, indent=4),
                    file_name=f"{category.lower().replace(' ', '_')}_details.json",
                    mime="application/json"
                )
 
                # Convert edited details to DataFrame
                df = pd.DataFrame([edited_details_dict])
 
                # Update CSV download
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label=f"Download {category} Details as CSV",
                    data=csv_data,
                    file_name=f"{category.lower().replace(' ', '_')}_details.csv",
                    mime="text/csv"
                )
            else:
                st.text_area("Edit Details", value=response_text, height=500)
               
 
           
# Main Streamlit app
def main():
    st.title("DOCUMENT PROCESSING")
 
    # Define categories for the navbar
    categories = list(document_details.keys())
 
    # Display horizontal navbar
    selected_category = st.sidebar.radio("Select", categories)
 
    # Process document for the selected category
    process_document(selected_category, document_details[selected_category], None)
 
# Run the app
if __name__ == "__main__":
    main()
 
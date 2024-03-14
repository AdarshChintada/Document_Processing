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
</style>
"""

# Display the navbar using st.markdown() with HTML/CSS
st.markdown(navbar_style, unsafe_allow_html=True)

# Function to load OpenAI model and get response
def get_gemini_response(input, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    if input != "":
        response = model.generate_content([input, image])
    else:
        response = model.generate_content(image)
    return response.text


Aadhar_details = '''Separate the name, dob, gender, Aadhar Number, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB :  DOB from the document
GENDER: Gender from the document
AADHAR Number : Passport number from the document
ADDRESS: Address from the document.'''

Pan_details = '''Separate the name, gender, dob, Aadhar Number, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
PAN Number : Passport number from the document
ADDRESS: Address from the document.'''

Passport_details = '''Separate the name, dob, gender, Aadhar Number, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
Passport Number : Passport number from the document
ADDRESS: Address from the document.'''

License_details = '''Separate the name, dob, gender, License Class, License Number, License date of issue, address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
License Class : License class from the document
License Number: License number from the document
Date of issue : Date of issue from the document
Date of expiry: Date of expiry from the document
ADDRESS: Address from the document.
'''

I94_details = '''Separate the name, dob, gender, I94 Number, Address(if found) with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the document
DOB : DOB from the document
GENDER: Gender from the document
I94 ID : I-94 number from the document
I94 class: Class of admit from the document
ADDRESS: Address from the document.'''

voidCheck_details = '''Separate the name, Address(if found), Cheque date, Amount in the cheque, Routing number, Account number, Cheque number with exclamatory mark(!) and return the text in capital letters from the image in this format only:
Name : Name from the cheque
ADDRESS : Address from the cheque
Cheque date : Cheque date from the cheque
Routing number : Routing number from the cheque
Account number :Account number from the cheque
Cheque number : Cheque number from the cheque.'''

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
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        submit = st.button("Submit")
        if submit:
            response_text = get_gemini_response(details_text, image)
            details = preprocess_output(response_text)

            # Convert details to DataFrame
            df = pd.DataFrame([details])

            # Display editable JSON data
            json_data = json.dumps(details, indent=4)
            edited_json_data = st.text_area("JSON Data", value=json_data, height=300)

            # Convert edited JSON data back to dictionary
            edited_details = json.loads(edited_json_data)

            # Download button for edited JSON data
            st.download_button(
                label=f"Download {category} Details as JSON",
                data=json.dumps(edited_details, indent=4),
                file_name=f"{category.lower().replace(' ', '_')}_details.json",
                mime="application/json"
            )

            # Download button for CSV data
            csv_data = df.to_csv(index=False)
            st.download_button(
                label=f"Download {category} Details as CSV",
                data=csv_data,
                file_name=f"{category.lower().replace(' ', '_')}_details.csv",
                mime="text/csv"
            )

# Main function for document processing app
def document_processing_app():
    st.title("DOCUMENT PROCESSING")

    # Define categories for the navbar
    categories = {
        "Aadhar": Aadhar_details,
        "PAN": Pan_details,
        "PASSPORT": Passport_details,
        "Driving License": License_details,
        "I-94": I94_details,
        "Void Check": voidCheck_details
    }

    # Display horizontal navbar
    selected_category = st.sidebar.radio("Select", list(categories.keys()))

    process_document(selected_category, categories[selected_category], None)

# Run the app
if __name__ == "__main__":
    document_processing_app()
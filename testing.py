# Q&A Chatbot
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
import streamlit as st
from pdf2image import convert_from_bytes
import os
from PIL import Image

import google.generativeai as genai

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load OpenAI model and get response
def get_gemini_response(input, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    if input != "":
        response = model.generate_content([input, image])
    else:
        response = model.generate_content(image)
    return response.text

##initialize our streamlit app
import streamlit as st

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

# Main Streamlit app
def main():
    st.title("DOCUMENT PROCESSING")

    # Define categories for the navbar
    categories = ["Aadhar", "PAN", "PASSPORT", "Driving License", "Resume", "I-94", "Void Check"]

    # Display horizontal navbar
    selected_category = st.sidebar.radio("Select", categories)

    # Display results based on selected category
    display_results(selected_category)

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


# Function to display results for each category
def display_results(category):
    if category == "Aadhar":
        st.header("Aadhar Card")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(Aadhar_details, image))
                text_input = st.text_input(
        "Enter some text 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )

    elif category == "PAN":
        st.header("PAN Card")
        uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(Pan_details, image))
                

    elif category == "PASSPORT":
        st.header("PASSPORT")
        uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(Passport_details, image))

    elif category == "Driving License":
        st.header("Driving License")
        uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(License_details, image))
    


    elif category == "I-94":
        st.header("I-94 Results")
        uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(I94_details, image))

    elif category == "Void Check":
        st.header("Void Check")
        uploaded_file = st.file_uploader("Choose an image..", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", use_column_width=True)
            submit = st.button("Submit")
            if submit:
                st.write(get_gemini_response(voidCheck_details, image))

# Run the app
if __name__ == "__main__":
    main()

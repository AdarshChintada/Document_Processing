# API FOR DOCUMENT PROCESSING 
import re
import os
import fitz
import io  
import json
import google.generativeai as genai
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")


app = FastAPI(title="DOCUMENT PROCESSING API", description="API for extracting the information from documents.", redoc_url=None)

json_example1 = '''{ {"NAME": "SRIRAM MAMUNDI",
                     "DOB": "11/04/1992", 
                     "GENDER": "MALE", 
                     "AADHAAR NUMBER": "8416 1590 3267"}, 
                     {"DOCUMENT TYPE": "AADHAAR"} } '''

json_example2 = '''{
  "summary": "To obtain a challenging position that allows me to fully utilize my problem solving abilities & innovation. looking forward to work for an organization which helps to enhance skills, providing better opportunities and to contribute the best in developing the organization.",
  "education": [
    {
      "degree": "B.Tech Computer Science Engineering",
      "institution": "Rajiv Gandhi University of Knowledge Technologies",
      "startDate": "Nov 2020",
      "endDate": "present",
      "cgpa": "8.6",
      "location": "Srikakulam, India"
    },
    {
      "degree": "Pre University Course",
      "institution": "Rajiv Gandhi University of Knowledge Technologies",
      "startDate": "Jul 2018",
      "endDate": "Nov 2020",
      "cgpa": "8.78",
      "location": "Srikakulam, India"
    },
    {
      "degree": "Secondary School Education",
      "institution": "Laxmi Nagar High School(G)",
      "startDate": "Jul 2017",
      "endDate": "Apr 2018",
      "cgpa": "10.00",
      "location": "Srikakulam, India"
    }
  ],
  "certifications": [
    {
      "name": "Microsoft Professionally Certified in Azure Data Fundamentals",
      "details": "with 766 grade marks."
    },
    {
      "name": "Python crash course",
      "details": "Google | Coursera"
    },
    {
      "name": "Data Science Certificate",
      "details": "from Sparks Foundation"
    }
  ],
  "extracurricularActivities": [
    "Volunteered at Teckzite, a technical fest organized by SDCAC in our college.",
    "Volunteer in Helping Hands, a Student Welfare Organization"
  ],
  "hobbies": [
    "Singing Songs",
    "Playing Badminton",
    "Meditation"
  ],
  "skills": {
    "programming": ["Python", "Java", "C"],
    "web": ["HTML", "CSS", "JavaScript"],
    "subjects": ["Computer networks & CNS(fundamentals)", "Linux"],
    "databases": ["SQL", "MongoDB"]
  },
  "projects": [
    {
      "name": "Real Estate Price prediction",
      "technologies": ["Machine learning", "Python", "HTML", "CSS", "Flask"],
      "role": "Machine Learning Engineer",
      "details": "Develop a predictive system with an accuracy of 89% by reducing 30% of features."
    },
    {
      "name": "Placement prediction using ML",
      "technologies": ["Machine learning", "Python", "HTML", "CSS"],
      "role": "Model Architect",
      "details": "Develop a ML model that can predict the student placement using gradient boosting."
    },
    {
      "name": "BBMS- The Blood Bank Management System",
      "technologies": ["HTML", "CSS", "Java Script", "Bootstrap", "PHP", "MySQL"],
      "details": [
        "Developed user-friendly, responsive, and thought-provoking web interface to promote blood donation in the society.",
        "Implemented donor authentication, admin control, blood inventory management functionalities, and CRUD operations."
      ]
    },
    {
      "name": "Sports Celebrity Image Classification",
      "technologies": ["OpenCv", "Machine Learning", "HTML", "CSS"],
      "details": "Built a website where one can drag-and-drop an image to instant recognition."
    }
  ],
  "achievements": [
    "Selected for National Means Cum-Merit Scholarship by Govt., of India",
    "State level 2nd rank in Career Foundation Course organized by Andhra Pradesh."
  ],
  "languages": ["English", "Hindi", "Telugu"],
  "name": "Adarsh Chintada",
  "email": "adarsh2@gmail.com",
  "phone": "89851122222",
  "linkedin": "LinkedIn",
  "github": "Github"
},
{
"Document Type" : "Resume"
}'''

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


def has_text(pdf_document):
    # Check if the document contains any text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        if page.get_text().strip():
            return True
    return False

# Routes

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/document_processing", response_class=JSONResponse)
async def extract_entities(doc: UploadFile = File(...)):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    prompt = f'''You will be given a document, it might be any type. Your reply should have extracting all the information with the keys and values in the document in JSON format. Include the "type of the document" at the end of JSON as illustrated below.
                 Example document : Identity document
                 Example reply : {json_example1}
                 
                Another Example : Resume
                Example Reply : {json_example2}'''

    if doc.content_type.startswith("image/"):
        # Read the image from the uploaded file
        img = Image.open(doc.file)
        response = model.generate_content([prompt, img], safety_settings=safe, 
                                          generation_config=genai.types.GenerationConfig(temperature=0.2))
    elif doc.content_type == "application/pdf":
        # Read the PDF file
        pdf_document = fitz.open(stream=doc.file.read(), filetype="pdf")
        
        # Extract text if it is text-based PDF
        if has_text(pdf_document):
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            
            pdf_prompt = prompt + "\n" + "Here is the document info:\n" + text
            response = model.generate_content([pdf_prompt], safety_settings=safe, 
                                              generation_config=genai.types.GenerationConfig(temperature=0.2))
        else:
            # Process image-based PDF as an image
            pdf_images = []
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                pdf_images.append(img)
            
            # We can handle multiple images if needed. Here, I am only processing the first image.
            response = model.generate_content([prompt, pdf_images[0]], safety_settings=safe, 
                                              generation_config=genai.types.GenerationConfig(temperature=0.2))
    else:
        raise ValueError("Unsupported file type. Please upload an image/PDF/imagedocument.")
    
    def convert_to_json(input_string):
        input_string = input_string.replace('\n', '').replace('\" ', '\"').replace(' \"', '\"')
        
        input_string = re.sub(r'(\})(\s*\{)', r'\1,\2', input_string)
        
        # Convert the string to a JSON object
        json_object = json.loads(f"[{input_string}]")
        return json_object

    gemini_response = convert_to_json(response.text)

    return gemini_response

    
if __name__ == "__main__":
    uvicorn.run("api:app", host="localhost", port=8000, reload=True)




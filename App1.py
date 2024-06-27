from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

load_dotenv()

# Configure the generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_prompt, pdf_content, input_text):
    print("Entering get_gemini_response function")
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    print("Model initialized")
    response = model.generate_content([input_prompt, pdf_content[0], input_text])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            # Convert the PDF to image
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
                }
            ]
            return pdf_parts
        except pdf2image.exceptions.PDFInfoNotInstalledError:
            st.error("PDFInfo is not installed. Please make sure poppler-utils is installed on the server.")
            return None
        except Exception as e:
            st.error(f"An error occurred while processing the PDF: {e}")
            return None
    else:
        raise FileNotFoundError("No file uploaded")

# Authentication function
def authenticate(username, password):
    if username == st.secrets["username"] and password == st.secrets["password"]:
        return True
    return False

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Check if the user is authenticated
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
else:
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    if uploaded_file is not None:
        st.write("PDF Uploaded Successfully")

    submit1 = st.button("Tell Me About the Resume")
    submit3 = st.button("Percentage match")

    input_prompt1 = """
    You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """

    input_prompt3 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
    Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
    the job description. First, the output should come as a percentage, then keywords missing, and finally, final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content is not None:
                response = get_gemini_response(input_prompt1, pdf_content, input_text)
                st.subheader("The Response is")
                st.write(response)
        else:
            st.write("Please upload the resume")

    elif submit3:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            if pdf_content is not None:
                response = get_gemini_response(input_prompt3, pdf_content, input_text)
                st.subheader("The Response is")
                st.write(response)
        else:
            st.write("Please upload the resume")

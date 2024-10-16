import streamlit as st
import PyPDF2
import re
from groq import Groq

# Initialize Groq API client
api = st.secrets['groq_api_key']
client = Groq(api_key=api)

# Function to load and process the PDF
def load_pdf(file):
    # Use PyPDF2 to read the uploaded file
    reader = PyPDF2.PdfReader(file)
    pages = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        pages.append(page.extract_text())
    return pages

# Function to clean the loaded document content
def clean_document_output(documents):
    cleaned_pages = []
    for content in documents:
        # Clean the page content
        content = re.sub(r'\uf097', '', content)  # Remove unicode artifacts
        content = re.sub(r'\s+', ' ', content).strip()  # Remove extra spaces
        cleaned_pages.append(content)
    return "\n".join(cleaned_pages)

# Chat function to process the cleaned text with the LLM
def chat(query):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": '''You are a literature specialist and computer scientist. Remove redundant concepts, 
                make the concepts coherent, and remove irrelevant information. Generate concise 
                and informative results.Make the not too much short that can skip important information. Do not include unnecessary details in the output.'''
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return chat_completion.choices[0].message.content

# Streamlit UI for uploading the PDF file
st.header('Summarize your PDF file! ')
file = st.file_uploader('Upload your PDF file here...', type='pdf')

if file is not None:
    # Load and process the uploaded PDF file
    pages = load_pdf(file)
    cleaned_text = clean_document_output(pages)

    # Send cleaned text to the LLM for summarization or further processing
    output = chat(cleaned_text)

    # Display the final output
    st.markdown(output)

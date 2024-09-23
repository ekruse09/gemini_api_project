import os
import genai
import vertexai

# Configure Gemini API for later use
def configure_api(api_key, project, location, model_name):
    genai.configure(api_key=api_key)
    vertexai.init(project=project, location=location)
    return genai.GenerativeModel(model_name)

def generate_content(model, pdf_path, prompt):
    try:
        gemini_response = model.generate_content(prompt=prompt, input_file=pdf_path)
        return gemini_response
    except Exception as e:
        return str(e)

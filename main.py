import os
import logging
import pandas as pd
from gemini_api_handler import configure_api, generate_content
from pdf_processor import extract_pages_with_keyword

# Setup logging
logging.basicConfig(filename='errors.txt', level=logging.ERROR)

def process_directory(input_dir, model, keyword):
    error_files = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                company_code = os.path.basename(root)  # Adjust as necessary
                prompt = f"Process the following PDF: {pdf_path}"

                response = generate_content(model, pdf_path, prompt)
                
                if isinstance(response, str) and "error" in response.lower():
                    logging.error(f"Error processing {pdf_path}: {response}")
                    error_files.append(pdf_path)
                else:
                    output_dir = os.path.join(root.replace("input", "output"), f"{company_code}_output")
                    os.makedirs(output_dir, exist_ok=True)
                    with open(os.path.join(output_dir, f"{company_code}_output.txt"), 'w') as output_file:
                        output_file.write(response)

    return error_files

def rerun_errors(error_files, model, keyword):
    additional_errors = []

    for pdf_path in error_files:
        response = generate_content(model, pdf_path, "Reprocess this PDF")
        
        if isinstance(response, str) and "file too big" in response.lower():
            filtered_pdf_path = extract_pages_with_keyword(pdf_path, keyword)
            response = generate_content(model, filtered_pdf_path, "Reprocess this filtered PDF")
            
            if isinstance(response, str) and "error" in response.lower():
                additional_errors.append(pdf_path)
                logging.error(f"Error processing {pdf_path} after filtering: {response}")
            else:
                # Save output as before
                company_code = os.path.basename(os.path.dirname(pdf_path))
                output_dir = os.path.join(os.path.dirname(pdf_path).replace("input", "output"), f"{company_code}_output")
                os.makedirs(output_dir, exist_ok=True)
                with open(os.path.join(output_dir, f"{company_code}_output.txt"), 'w') as output_file:
                    output_file.write(response)

    return additional_errors

def create_dataframe(output_dir):
    all_files = []
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    all_files.append({'file_name': file, 'content': content})

    df = pd.DataFrame(all_files)
    # Preprocess DataFrame for BigQuery
    df['processed_content'] = df['content'].str.replace('\n', ' ')
    
    # Save to Excel CSV
    df.to_csv('output_data.csv', index=False)

def main():
    api_key = "YOUR_API_KEY"
    project = "YOUR_PROJECT"
    location = "YOUR_LOCATION"
    model_name = "YOUR_MODEL_NAME"
    
    model = configure_api(api_key, project, location, model_name)
    input_dir = "path/to/your/input"
    output_dir = "path/to/your/output"
    keyword = "YourKeyword"

    # Initial processing
    error_files = process_directory(input_dir, model, keyword)

    # Rerun errors
    additional_errors = rerun_errors(error_files, model, keyword)

    # Create DataFrame from output files
    create_dataframe(output_dir)

if __name__ == "__main__":
    main()

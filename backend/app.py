from flask import Flask, request, jsonify, session, send_file
from azure.storage.blob import BlobServiceClient, ContentSettings
from flask_cors import CORS
import sys
import os
from dotenv import load_dotenv
from AzureOpenAIUtil.AzureFormRecognizer import AzureFormRecognizerRead
from AzureOpenAIUtil.Summerization import summarization
import json
import random
import string
import secrets
from flask_session import Session
from redis import Redis
import msal
from AzureOpenAIUtil.Embedding import DocumentEmbedding
import time
from PyPDF2 import PdfReader, PdfWriter

import logging

# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = ""
app.debug = True
CORS(app)

# Add these lines for Flask-Session configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'

# Initialize the Session
Session(app)

# Azure Blob Storage settings
ACCOUNT_NAME = ""
ACCOUNT_KEY = ""
CONTAINER_NAME = "r"

# connection_string = ""
# blob_service_client = BlobServiceClient.from_connection_string(
#     connection_string)
# container_client = blob_service_client.get_container_client(CONTAINER_NAME)
length = 10

load_dotenv()
RAW_DATA_FOLDER = 'data/pdf'
# -- extracted json file
EXTRACTED_DATA_FOLDER = 'data/extracted'
# -- summary files
SUMMARY_FOLDER = 'data/summary'
# Azure Form Recognizer Read
azure_fr = AzureFormRecognizerRead()
doc_emb = DocumentEmbedding(document_embedding_deployment_name=os.getenv('DOCUMENT_MODEL_NAME'),\
                            query_embedding_deployment_name=os.getenv('QUERY_MODEL_NAME'),\
                            summerization_deployment_name=os.getenv('DEPLOYMENT_NAME'))
global_data = {'last_processed_file': None}
@app.route('/upload_local', methods=['POST'])
def upload_pdf_local():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        # result_str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

        global file_name;
        # file_name = result_str + '-' + file.filename
        file_name = file.filename
        
        if not os.path.exists(RAW_DATA_FOLDER):
            os.makedirs(RAW_DATA_FOLDER)
        
        file_path = os.path.join(RAW_DATA_FOLDER, file_name)
        file.save(file_path)
        # Replace with your PDF file path
        files_extracted = False
        documents_loaded = False
        split_pdf_to_single_pages(file_path)
        if global_data['last_processed_file'] != file_name:
            files_extracted = azure_fr.extract_files(file_name, RAW_DATA_FOLDER, EXTRACTED_DATA_FOLDER)            
            global_data['last_processed_file'] = file_name
            documents_loaded = doc_emb.load_documents('data/extracted/')
        # doc_emb.load_documents(file_name,'data/extracted/')
        if files_extracted and documents_loaded:
            return jsonify({"success": True, "message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize_from_local/', methods=['GET'])
def summarize_from_local():

    # pause to make sure extracted file is ready to be consumed
    time.sleep(3)
    # Azure OpenAI util for summerization
    summary_eng = summarization(deployment_name=os.getenv('DEPLOYMENT_NAME'))

    # azure_fr.extract_files(file_name, RAW_DATA_FOLDER, EXTRACTED_DATA_FOLDER)
    
        
    doc_sum = summary_eng.generate_summary_files_local(file_name,source_folder=EXTRACTED_DATA_FOLDER, destination_folder=SUMMARY_FOLDER)
    
    return jsonify(doc_sum)

@app.route('/q_and_a', methods=['POST'])
def q_and_a():
    
    
        
    # Check if the request contains JSON data
    if request.is_json:
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the JSON data has a key called 'question'
        if 'question' in data:
            question = data['question']
            time.sleep(3)
            # file_name,          
            # doc_emb.load_documents('data/extracted/')
            # Process the string (in this case, just return it as-is)
            result = doc_emb.query(question,topK=2)
            
            # Return the result as a JSON response
            # output_text = result['output_text']
            # return jsonify(str(output_text))
            output_text = result['output_text']
            source = result['source']
            return jsonify({"output_text": str(output_text), "source": str(source)})

        else:
            return jsonify({'error': 'Missing question key in JSON data'}), 400
    else:
        return jsonify({'error': 'Invalid request, please send JSON data'}), 400


@app.route('/summerize/', methods=['GET'])
def summerize():
    # Azure Form Recognizer Read
    azure_fr = AzureFormRecognizerRead()
    print("global file_name is "+file_name)

    azure_fr.analyze_read_azure_blob(file_name,'raw','extracted')
    # Azure OpenAI util for summerization
    summary_eng = summarization(deployment_name=os.getenv('DEPLOYMENT_NAME'))

    doc_sum = summary_eng.generate_summary_files(file_name)
    # response_data = {"received_string": file_name}
    json_string = json.dumps(doc_sum)
    return jsonify(doc_sum)






@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file format"}), 400

    try:
        result_str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

        global file_name_;
        # file_name =   result_str+'-'+ file.filename
        file_name_ =   file.filename
        content_settings = ContentSettings(content_type='application/pdf')
        blob_client = container_client.get_blob_client(file_name_) #file_name file.filename
        blob_client.upload_blob(
            file, content_settings=content_settings, overwrite=True)
        
        return jsonify({"success": True, "message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(f'data/pages/{filename}', as_attachment=True)
    except Exception as e:
        return str(e)



def split_pdf_to_single_pages(file_path):
    output_folder = "data/pages"
    # Create output directory if not exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    pdf = PdfReader(file_path)

    # Loop through each page in the PDF
    for page_number in range(len(pdf.pages)):
        # Create a new PDF writer object and add the page to it
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page_number])

        # Write the page to a new file
        output_filename = f"{output_folder}/{os.path.basename(file_path)[:-4]}_page_{page_number + 1}.pdf"
        
        with open(output_filename, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

        print(f"Created: {output_filename}")







if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True,threaded=True)

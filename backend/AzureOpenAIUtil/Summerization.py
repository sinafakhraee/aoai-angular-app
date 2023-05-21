
import sys
sys.path.append('./.venv/Lib/site-packages/')

import os, json

from langchain.llms import AzureOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from azure.storage.blob import BlobServiceClient
import re


class summarization:
    # max_tokens=256
    def __init__(self, deployment_name, temperature = 1, max_tokens=256) -> None:
        self.llm = AzureOpenAI(temperature=temperature, deployment_name=deployment_name, max_tokens=max_tokens)


    def read_json_blob(self,blob_service_client, container_name, blob_name):
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        json_content = blob_client.download_blob().content_as_text()
        return json.loads(json_content)    

    def get_summary_local(self, file, summerization_type='map_reduce'):

        with open(file) as f:
            file_json = json.loads(f.read())

        docs = [Document(page_content = page['page_content']) for page in file_json['content']]
        chain = load_summarize_chain(self.llm, chain_type=summerization_type)
        return chain.run(docs)
            
    def generate_summary_files_local(self, file:str,source_folder, destination_folder, summerization_type='map_reduce', verbose=True):
        os.makedirs(destination_folder, exist_ok=True)

        all_summeries = []
        # for file in os.listdir(source_folder):
        # file = os.listdir(source_folder)[0]
        json_file = re.sub(r"\.pdf", ".json", file, flags=re.IGNORECASE)

        # json_file = file.replace(".pdf", ".json")
        if verbose:
            print('\n\nGenerate summary for file:', file)
        file_summary = self.get_summary_local(os.path.join(source_folder, json_file), summerization_type=summerization_type)
        summary = {'file': file, 'summerization_type':summerization_type, 'summary':file_summary}
        # with open(os.path.join(destination_folder, file), "w") as f:
        #     f.write(json.dumps(summary))
        if verbose:
            print(summary)
        all_summeries.append(summary)
        return all_summeries
    



    def get_summary(self, file:str, summerization_type='map_reduce'):
        
        # Usage example
        storage = os.environ["AZURE_BLOB_STORAGE_ACCOUNT_NAME"]
        key = os.environ["AZURE_BLOB_STORAGE_KEY"]
        connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage};AccountKey={key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        container_name = 'extracted'
        blob_name = file.replace(".pdf", ".json")

        file_json = self.read_json_blob(blob_service_client, container_name, blob_name)

        docs = [Document(page_content=page['page_content']) for page in file_json['content']]

        chain = load_summarize_chain(self.llm, chain_type=summerization_type)
        return chain.run(docs)
                
    def generate_summary_files(self, file:str, summerization_type='map_reduce', verbose=True):
        
        
        all_summeries = []
        
        if verbose:
            print('\n\nGenerate summary for file:', 'file')
        file_summary = self.get_summary(file, summerization_type=summerization_type)
        summary = {'file': file, 'summerization_type':summerization_type, 'summary':file_summary}
        # with open(os.path.join(destination_folder, file), "w") as f:
        #     f.write(json.dumps(summary))
        if verbose:
            print(summary)
        all_summeries.append(summary)
        return all_summeries
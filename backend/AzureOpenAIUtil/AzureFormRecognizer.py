import json
from flask import Flask, request, jsonify, session
class AzureFormRecognizerRead:

    def __init__(self):
        import os
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import DocumentAnalysisClient
        self.endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        self.key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        self.document_analysis_client = DocumentAnalysisClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

    
    def extract_local_single_file(self, file_name: str):
        not_completed = True
        while not_completed:
            with open(file_name, "rb") as f:
                poller = self.document_analysis_client.begin_analyze_document(
                    "prebuilt-read", document=f
                )
                not_completed=False
        result = poller.result()
        return self.get_page_content(file_name, result)

    def extract_files(self,file_name: str, folder_name: str, destination_folder_name: str):
        import os
        import json

        os.makedirs(destination_folder_name, exist_ok=True)
        for file in os.listdir(folder_name):
            if file == file_name:
                if file[-3:].upper() in ['PDF','JPG','PNG']:
                    print('Processing file:', file, end='')
                
                    page_content = self.extract_local_single_file(os.path.join(folder_name, file))
                    output_file = os.path.join(destination_folder_name, file[:-3] +'json')
                    print(f'    write output to {output_file}')
                    with open(output_file, "w") as f:
                        f.write(json.dumps(page_content))
        return True

    def get_page_content(self,file_name:str, result):
        page_content = []
        for page in result.pages:

            all_lines_content = []
            for line_idx, line in enumerate(page.lines):
                all_lines_content.append(' '.join([word.content for word in line.get_words()]))
            page_content.append({'page_number':page.page_number, 
                                    'page_content':' '.join(all_lines_content)})

        return {'filename':file_name, 'content':page_content}

    def _get_azure_container_0(self, blob_service_client, container_name:str):
        container_client = blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
        except:
            pass


    def _get_azure_container(self, blob_service_client, container_name: str):
        container_client = blob_service_client.get_container_client(container_name)
        try:
            container_client.create_container()
        except:
            pass
        return container_client


    def analyze_read_azure_blob(self,file_name, input_folder: str, text_output_folder: str, intemediate_output_folder: str = None):
        import os
        from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
        storage = os.environ["AZURE_BLOB_STORAGE_ACCOUNT_NAME"]
        key = os.environ["AZURE_BLOB_STORAGE_KEY"]
        connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage};AccountKey={key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        # Container client for raw container.
        raw_container_client = blob_service_client.get_container_client(input_folder)

        # Container client for intemediate
        if intemediate_output_folder != None:
            intemediate_container_client = self._get_azure_container(blob_service_client, intemediate_output_folder)

        text_container_client = self._get_azure_container(blob_service_client, text_output_folder)

        storageUrlBase = raw_container_client.primary_endpoint

        blob_list = raw_container_client.list_blobs()
        for blob in blob_list:
            if blob.name == file_name:
                blobUrl = f'{storageUrlBase}/{blob.name}'
                print(blobUrl)
                # poller = self.form_recognizer_client.begin_analyze_document_from_url("prebuilt-document", blobUrl)
                poller = self.document_analysis_client.begin_analyze_document_from_url(
                        "prebuilt-read", document_url=blobUrl
                    )
                # Get results
                doc = poller.result()

                if intemediate_output_folder!= None:
                    intemediate_blob_client = intemediate_container_client.get_blob_client(container=intemediate_output_folder, blob=blob.name)
                    intemediate_blob_client.upload_blob(doc, blob.blob_type, overwrite=True)
                
                # Create a blob client for the new file
                blob_client = text_container_client.get_blob_client(blob=blob.name)
                # Extract the content from the document analysis result
                page_content = self.get_page_content(blob.name, doc)
                json_content = json.dumps(page_content)

                # Change the blob name extension to .json
                json_blob_name = os.path.splitext(blob.name)[0] + '.json'

                # Create a new blob client with the updated name
                json_blob_client = text_container_client.get_blob_client(blob=json_blob_name)

                # Upload the JSON content
                json_blob_client.upload_blob(json_content, blob_type=blob.blob_type, overwrite=True)

                # blob_client = text_container_client.get_blob_client(container=text_output_folder, blob=blob.name)
                # blob_client.upload_blob(blob, blob.blob_type, overwrite=True)

                # Delete blob from raw now that its processed
                # raw_container_client.delete_blob(blob)
        # return docs
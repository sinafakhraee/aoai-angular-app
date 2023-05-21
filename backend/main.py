from AzureOpenAIUtil.Embedding import DocumentEmbedding
import os
from dotenv import load_dotenv


def main():
    # your code here
    
    load_dotenv()
    doc_emb = DocumentEmbedding(document_embedding_deployment_name=os.getenv('DOCUMENT_MODEL_NAME'),\
                            query_embedding_deployment_name=os.getenv('QUERY_MODEL_NAME'),\
                            summerization_deployment_name=os.getenv('DEPLOYMENT_NAME'))
    doc_emb.load_documents('data/extracted/')
    doc_emb.query('Automatically Generated Prompts',topK=2)
if __name__ == "__main__":
    main()
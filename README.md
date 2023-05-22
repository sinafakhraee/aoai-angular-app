# Azure OpenAI Embeddings and GPT models for document summarization and QnA

## 1) Overview of the application

This is a sample application written in Angular/PrimeNG as the frontend and Python/Flask as the backend services which use Azure OpenAI embeddings and GPT 3.0 models for text summarication and Q&A.  

### User Interface

![User Interface](https://github.com/sinafakhraee/aoai-angular-app/blob/main/images/webui.jpg)

### Architecture

![Architecture](https://github.com/sinafakhraee/aoai-angular-app/blob/main/images/architecture.png)

## 2) Prerequisite to run the application

To run the application, you need to have the following Azure services and tools:

- [Azure OpenAI service](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/)
- [Azure Form Recognizer](https://azure.microsoft.com/en-us/products/form-recognizer/)
- [Git](https://git-scm.com/downloads)

Once you have these services and tools, you can run the application on your local machine using the docker-compose command. 

**Make sure to add Azure API keys and OpenAI models to your .env file and have it in the same directory where you run the docker command.**

### Sample .env file:
```bash
OPENAI_API_KEY=XXXxxxxxxXXXXXxxxxxxx
OPENAI_API_BASE=https://youraoaiservice.openai.azure.com/
OPENAI_API_TYPE=azure
OPENAI_API_VERSION=2022-12-01
DOCUMENT_MODEL_NAME=curie-search-doc
QUERY_MODEL_NAME=curie-query-doc
DEPLOYMENT_NAME=text-davinci-003
AZURE_FORM_RECOGNIZER_ENDPOINT=https://formrecognizer-sf.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=XXXxxxxxxXXXXXxxxxxxx
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_USERNAME=test
REDIS_PASSWORD=
REDIS_SSL=False
```
### docker-compose.yml file:

```yml
version: '3'
services:
  flask:
    image: "sinafakhraee/aoai-backend-service:latest"
    env_file: .env
    ports:
      - "5000:5000"
  redis:
    image: "redislabs/redismod:latest"
  ng-app:
    image: "sinafakhraee/ng-app:latest"
    ports:
      - "8080:8080"
```

### docker-compose command:

```bash
docker-compose up
```
## <u>Referenced Repositories</u>

- [azure-openai-samples](https://github.com/Azure/azure-openai-samples)
- [azure-open-ai-embeddings-qna](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna)

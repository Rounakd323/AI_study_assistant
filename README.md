AI Study Assistant — FastAPI + RAG

A Retrieval-Augmented Generation (RAG) study assistant that allows students to learn from their own PDF study material.

The application combines FastAPI, LangChain, FAISS, Hugging Face Embeddings, and Ollama/Llama 3 to provide document-grounded summaries, quiz generation, semantic search, and question answering.

Overview

AI Study Assistant processes a user's study material and uses semantic retrieval to provide relevant context to a locally hosted LLM.

The system follows a complete RAG pipeline:

Upload a PDF

Extract text from the document

Split the text into smaller chunks

Generate vector embeddings

Store embeddings in FAISS

Retrieve the most relevant chunks for a query

Pass retrieved context to Llama 3

Generate a document-grounded response

Features

PDF upload and processing

Semantic search using FAISS

Hugging Face sentence embeddings

Topic-based summaries

Document-grounded question answering

Automatic quiz generation

FastAPI REST API

Web interface served through FastAPI

Local LLM inference using Ollama

Configurable embedding model and LLM

FastAPI Swagger documentation

Architecture

                    ┌──────────────────┐
                    │    Web Frontend  │
                    │   HTML/CSS/JS    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      FastAPI     │
                    │       API        │
                    └────────┬─────────┘
                             │
                       PDF Upload
                             │
                             ▼
                    ┌──────────────────┐
                    │   PyPDFLoader    │
                    │  Text Extraction │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Text Chunking    │
                    │ 500 / overlap 50 │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Hugging Face     │
                    │ all-MiniLM-L6-v2 │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      FAISS       │
                    │  Vector Search   │
                    └────────┬─────────┘
                             │
                         Top 5 chunks
                             │
                             ▼
                    ┌──────────────────┐
                    │  Ollama / Llama3 │
                    │     Local LLM    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Generated Result │
                    └──────────────────┘

RAG Workflow

1. Document Upload

The user uploads a PDF through the web interface.

FastAPI receives the file through the /api/upload/ endpoint.

2. Text Extraction

PyPDFLoader extracts readable text from each page of the PDF.

Empty pages are filtered out before processing.

3. Text Chunking

The extracted content is divided into smaller chunks using LangChain's RecursiveCharacterTextSplitter.

Current configuration:

Chunk size: 500
Chunk overlap: 50

The overlap helps preserve context between adjacent chunks.

4. Embedding Generation

Each chunk is converted into a numerical vector using:

all-MiniLM-L6-v2

These embeddings represent the semantic meaning of the text.

5. Vector Storage

The generated embeddings are stored in a FAISS vector index.

FAISS allows the application to efficiently search for chunks that are semantically similar to a user's query.

6. Similarity Retrieval

When a user asks a question or requests a topic summary, the query is converted into an embedding.

The application performs similarity search against the FAISS index and retrieves the most relevant chunks.

The current implementation retrieves the top 5 chunks.

7. LLM Generation

The retrieved context is passed to Llama 3 through Ollama.

The LLM generates the final response using the retrieved document context.

8. Response

The generated result is returned to the frontend and displayed to the user.

Why RAG?

Instead of sending the entire document to the LLM, the application first retrieves the most relevant sections of the uploaded material.

This provides a smaller and more relevant context for generation and helps keep responses grounded in the source document.

The architecture separates:

Retrieval
    ↓
Relevant document context
    ↓
Generation

This is the core principle behind the application's RAG implementation.

Technology Stack

Component

Technology

Backend

FastAPI

Frontend

HTML, CSS, JavaScript

RAG Framework

LangChain

Embeddings

Hugging Face all-MiniLM-L6-v2

Vector Store

FAISS

PDF Processing

PyPDFLoader

LLM Runtime

Ollama

LLM

Llama 3

ASGI Server

Uvicorn

Application Preview

Add screenshots of the application here.

Recommended screenshots:

Main dashboard

PDF upload interface

Study summary / Q&A interface

Quiz generation interface

Project Structure

AI_study_assistant/
│
├── backend/
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py
│   │   ├── study.py
│   │   ├── quiz.py
│   │   └── doubts.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── embeddings.py
│       ├── llm.py
│       └── pdf_service.py
│
├── frontend/
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       └── js/
│           └── app.js
│
├── api/
│   └── index.py
│
├── requirements.txt
├── .gitignore
└── README.md

Backend Structure

backend/main.py

The main FastAPI application entry point.

Responsibilities include:

Creating the FastAPI application

Configuring CORS

Mounting frontend static files

Loading Jinja2 templates

Registering API routers

Starting the Uvicorn server

backend/routers/upload.py

Handles PDF uploads and document processing.

The uploaded document is processed and converted into a FAISS vector index.

backend/routers/study.py

Handles topic-based study summary generation.

The requested topic is used to retrieve relevant document chunks before generating the response.

backend/routers/quiz.py

Generates quizzes based on the uploaded study material.

backend/routers/doubts.py

Handles document-based question answering.

backend/services/pdf_service.py

Responsible for:

Loading PDFs

Extracting text

Filtering empty pages

Splitting documents into chunks

Creating embeddings

Building the FAISS index

Performing similarity search

backend/services/embeddings.py

Manages the Hugging Face embedding model and FAISS vector database.

The embedding model and FAISS database are maintained as singleton instances to avoid repeatedly initializing them.

backend/services/llm.py

Provides a wrapper around the Ollama LLM.

The current implementation uses:

llama3

Prerequisites

Before running the application, install:

Python 3.11+

Ollama

Llama 3

Verify that Ollama is available:

ollama --version

Pull the Llama 3 model:

ollama pull llama3

Start the Ollama service:

ollama serve

Setup

1. Clone the repository

git clone https://github.com/Rounakd323/AI_study_assistant.git
cd AI_study_assistant

2. Create a virtual environment

python -m venv venv

3. Activate the virtual environment

Windows:

venv\Scripts\activate

Linux/macOS:

source venv/bin/activate

4. Install dependencies

pip install -r requirements.txt

5. Start the application

From the project root:

cd backend
python main.py

The application will be available at:

http://localhost:8000

FastAPI's interactive API documentation is available at:

http://localhost:8000/docs

API Endpoints

Method

Endpoint

Description

POST

/api/upload/

Upload PDF and build FAISS index

GET

/api/upload/status

Check whether a document is loaded

POST

/api/study/

Generate topic summary

POST

/api/quiz/

Generate a 5-question quiz

POST

/api/doubts/

Answer a question from the document

GET

/docs

FastAPI Swagger UI

API Examples

Upload PDF

POST /api/upload/

Content-Type: multipart/form-data

Body:
file=<pdf>

Example response:

{
  "message": "PDF processed successfully",
  "filename": "study_material.pdf",
  "pages": 42,
  "chunks": 186
}

Study Summary

POST /api/study/

Request:

{
  "topic": "Photosynthesis"
}

Response:

{
  "topic": "Photosynthesis",
  "summary": "...",
  "context_snippets": [
    "...",
    "..."
  ]
}

Quiz

POST /api/quiz/

Request:

{
  "topic": "Photosynthesis"
}

Response:

{
  "topic": "Photosynthesis",
  "quiz": "1. ..."
}

Doubt Solving

POST /api/doubts/

Request:

{
  "question": "What is ATP?",
  "topic": "Photosynthesis"
}

Response:

{
  "question": "What is ATP?",
  "answer": "..."
}

Configuration

Embedding Device

The embedding model currently runs on CPU.

In:

backend/services/embeddings.py

the current configuration is:

model_kwargs={"device": "cpu"}

For a compatible NVIDIA GPU, this can be changed to:

model_kwargs={"device": "cuda"}

LLM Model

The application currently uses Llama 3 through Ollama.

In:

backend/services/llm.py

the model is configured as:

Ollama(model="llama3")

Another compatible Ollama model can be configured if required.

Chunking Configuration

Chunking is configured in:

backend/services/pdf_service.py

Current configuration:

chunk_size = 500
chunk_overlap = 50

These values can be adjusted depending on the type of documents being processed.

Local LLM Requirement

This project uses Ollama for local LLM inference.

The GitHub repository contains the application source code, but the LLM itself is not hosted inside the repository.

To run the complete RAG pipeline, Ollama must be installed and running on the local machine.

Install and download the model:

ollama pull llama3

Then start Ollama:

ollama serve

The application communicates with the locally running Ollama service to generate responses.

Running Without the Local LLM

The repository can be inspected without installing Ollama.

The source code, API structure, frontend, RAG pipeline, embedding implementation, and FAISS integration can all be reviewed directly from the repository.

However, features that require LLM generation will not produce responses unless Ollama and the configured model are available.

Data Flow

User
 │
 ▼
Web Interface
 │
 ▼
FastAPI Endpoint
 │
 ├─────────────── PDF Upload
 │                     │
 │                     ▼
 │               PyPDFLoader
 │                     │
 │                     ▼
 │               Text Chunks
 │                     │
 │                     ▼
 │            Hugging Face Embeddings
 │                     │
 │                     ▼
 │                  FAISS
 │
 └─────────────── User Query
                       │
                       ▼
                Query Embedding
                       │
                       ▼
                FAISS Similarity
                       │
                       ▼
                  Top 5 Chunks
                       │
                       ▼
                  Llama 3
                       │
                       ▼
                 Final Response

Design Decisions

Local LLM Inference

Ollama was selected to keep LLM inference local rather than relying on an external hosted API.

This makes the application suitable for experimenting with local models and avoids requiring an external LLM API key.

FAISS

FAISS was selected as the vector store because it provides efficient similarity search and is lightweight enough for a local RAG application.

Hugging Face Embeddings

all-MiniLM-L6-v2 provides a lightweight sentence embedding model suitable for semantic retrieval on consumer hardware.

FastAPI

FastAPI provides:

Asynchronous request handling

Automatic API documentation

Pydantic-based request validation

Simple router-based API organization

Easy integration with Python ML tooling

Limitations

Requires a local Ollama installation for LLM inference.

Embeddings currently run on CPU by default.

The current implementation maintains a local FAISS index.

PDF processing is primarily designed for text-based PDFs.

The application currently maintains a single active document index.

The current architecture is intended primarily as a local/demo application rather than a production multi-user deployment.

Future Improvements

Potential improvements include:

Cloud-based LLM inference

Persistent cloud vector database

Authentication

User-specific document collections

Multi-document retrieval

Streaming LLM responses

Conversation history

Improved citation and source tracking

Background PDF processing

Production deployment

Monitoring and logging

Automated testing

CI/CD pipeline

Repository

GitHub:

https://github.com/Rounakd323/AI_study_assistant

License

This project is currently provided for educational and portfolio purposes.
# DOC RAG – Backend

## Project Overview

DOC RAG is a personal Retrieval-Augmented Generation (RAG) backend project that combines document processing, semantic retrieval, and a large language model (LLM) to answer questions based on uploaded documents.

The system allows users to upload documents such as PDFs, DOCX, and TXT files, processes and indexes their content, and enables users to query the documents using natural language.



## Core Workflow

```text
Document Upload
      ↓
Document Validation
      ↓
Upload to Amazon S3
      ↓ 
Text Extraction
      ↓
Text Chunking
      ↓
Embeddings
      ↓
Vector Storage
      ↓
Semantic Retrieval
      ↓
LLM
      ↓
Natural Language Answer
```



## Technology Stack

| Category                  | Technology                                  |
| ------------------------- | ------------------------------------------- |
| Language                  | Python 3                                    |
| Framework                 | Django 5.2.11, Django REST Framework 3.16.1 |
| Database                  | PostgreSQL 15 (Docker container)            |
| Cache / Message Broker    | Redis 7 (Docker container), Celery 5.6.2    |
| Cloud Storage             | Amazon S3, django-storages, Boto3           |
| Document Processing       | pypdf, python-docx                          |
| File Validation           | filetype                                    |
| HTTP Client               | Requests                                    |
| Environment Configuration | python-dotenv                               |
| Testing                   | Pytest                                      |
| Containerization          | Docker, Docker Compose                      |
| CI/CD                     | GitHub Actions                              |
| API Documentation         | OpenAPI, Swagger UI                         |

    
 

```
├── .env.example
├── .github
│   └── workflows
│       └── ci.yml
├── .gitignore
├── README.md
├── apps
│   ├── common                    # Shared utilities used across applications
│   │   ├── apiexceptions         # Custom API exceptions and error handling
│   │   ├── constants              # Shared constants and application values
│   │   └── validators             # Reusable validation logic
│   │
│   └── documents                 # Document upload and RAG processing
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── migrations
│       ├── models.py
│       ├── repositories          # Database access/query logic
│       ├── serializers.py
│       ├── services               # Business logic and external service integrations
│       │   └── s3_services.py     # AWS S3 upload and storage operations
│       ├── tasks.py               # Celery background tasks
│       ├── tests.py
│       ├── urls.py
│       └── views.py
│
├── config                        # Main Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py                 # Celery application configuration
│   ├── settings.py               # Django and environment configuration
│   ├── urls.py
│   └── wsgi.py
│
├── docker                        # Docker and container configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
│
├── docs                          # Technical project documentation
│   ├── api_design.md
│   └── images
├── manage.py
└── requirements.txt
```
## 🛠 Getting Started

### Prerequisites

Before running the project, make sure you have the following installed:

* Python 3
* Docker
* Git

### Clone the Repository

```bash
git clone https://github.com/C0mlan/rag_ai.git
cd rag_ai
```

### Configure Environment Variables

Create a .env file in the project root.

Copy the variables from `.env.example` into `.env` and update the values according to your local environment.

### Start the Application

The project runs all required services inside Docker containers, including:

* Django
* PostgreSQL
* Redis
* Celery

Build and start the containers with:

```bash
docker compose up --build
```

Once the containers are running, the Django application will be available at:

```text
http://localhost:8001
```

### Apply Database Migrations

Run the Django migrations inside the web container:

```bash
docker exec -it employee_chat-web-1 python manage.py migrate
```

### Create a Superuser

To create a Django admin account:

```bash
docker exec -it employee_chat-web-1 python manage.py createsuperuser
```

Follow the prompts to enter the superuser credentials.

### Verify Running Services

To check that all Docker services are running:

```bash
docker compose ps
```

You should see the project's containers for Django, PostgreSQL, Redis, and Celery.

### Run the Application

Start the Django application using:

```bash
doker compose up
```

### Run Tests

Run the complete test suite inside the Django container:

```bash
docker compose exec web pytest -v
```

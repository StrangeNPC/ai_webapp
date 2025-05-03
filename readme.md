# AI News Analyzer Web Application

This repository contains the source code and documentation for an AI-powered web application. The application allows users to submit news articles (via text input or file upload) and receive an AI-generated summary and a list of mentioned nationalities/countries. Enhanced versions also extract organizations/people and integrate with AWS S3.

The project is divided into several components, each residing in its own folder. Additionally, it includes an architectural design proposal for scaling the system to handle high-volume processing for Part 2.

## 📂 Repository Structure

This repository is organized into the following main directories:

*   **`frontend/`**: Contains the React-based single-page application (SPA) that serves as the user interface for interacting with the backend API.
*   **`backend_v1/`**: The initial FastAPI backend implementation. It handles text/file uploads, interacts with the OpenAI API for summarization and nationality extraction, and is designed for deployment on AWS Elastic Beanstalk.
*   **`backend_v2_wRDS_S3_WIP/`**: An enhanced version of the backend. This iteration adds:
    *   Extraction of Organizations and People entities.
    *   Integration with AWS S3 for storing uploaded files.
    *   Work-in-progress (WIP) setup for potential integration with AWS RDS (PostgreSQL) for storing analysis results (Note: RDS integration is not fully completed due to lack of time).
*   **`Backend_test/`**: Contains Python test scripts designed to test the API endpoints of both `backend_v1` and `backend_v2_wRDS_S3_WIP`.
*   **`part_2/`**: Includes the architectural design document (`README.md`) and diagram (`Architecture.png`) outlining a scalable system capable of processing a high volume (10,000/hour) of news articles using AWS services like ECS, RabbitMQ, Bedrock, S3, RDS, Langfuse, and DeepEval.

## ✨ Key Features (Part 1 Implementation)

*   **Frontend UI:** Clean interface (React/Vite) allowing text input or `.txt`/`.docx` file uploads. Displays loading states, results (summary, nationalities, etc.), and error messages.
*   **Backend API:** FastAPI-based REST API (`POST /analyze`) processing requests.
*   **AI Analysis:** Leverages OpenAI API (e.g., GPT-3.5-turbo) with prompt engineering to:
    *   Generate concise summaries.
    *   Extract mentioned nationalities/countries.
    *   (Bonus in v2) Extract organizations and people (Not integrated with frontend yet).
*   **File Handling:** Supports direct text input and uploads of `.txt` and `.docx` files.
*   **Cloud Deployment:** Backend designed for AWS Elastic Beanstalk. Frontend deployable to S3 Static Hosting, Vercel, etc.
*   **S3 Integration (Bonus in v2):** Uploaded files are stored in an AWS S3 bucket.
*   **Configuration:** Secure handling of API keys and settings via environment variables.
*   **Testing:** Dedicated test suite for backend API validation.

## 🛠️ Technology Stack (Core)

*   **Frontend:** React (with Vite)
*   **Backend:** Python, FastAPI, Uvicorn, OpenAI Python Client
*   **File Parsing:** `python-docx`, `python-multipart`
*   **Testing:** Python `requests`
*   **Cloud:** AWS (Elastic Beanstalk, S3, potentially RDS)

## 🚀 Getting Started

To explore, set up, or run specific parts of this project, please navigate to the relevant folder and consult its dedicated `README.md` file:

*   For the user interface: `cd frontend`
*   For the initial backend: `cd backend_v1`
*   For the enhanced backend with S3/RDS: `cd backend_v2_wRDS_S3_WIP`
*   For running backend tests: `cd Backend_test`

Each sub-directory's README contains detailed instructions for setup, dependencies, configuration, running the code, deployment notes, and API documentation where applicable.



# AI News Analyzer Backend

A FastAPI-based REST API that analyzes news articles to generate concise summaries and extract mentioned nationalities/countries using OpenAI's API.

## 🔗 Live URLs

- **Backend API:** [Your Elastic Beanstalk Environment URL]
  - Example: `http://ai-news-analyzer-env.exampleURL.us-east-1.elasticbeanstalk.com`

> *Note: Add Frontend URL if/when deployed, e.g., to S3*

## 🛠️ Technology Stack

- **Backend:** Python 3.9
- **Framework:** FastAPI
- **Server:** Uvicorn
- **AI:** OpenAI API (Defaults to gpt-3.5-turbo)
- **File Handling:** `python-docx`, `python-multipart`
- **Environment Variables:** `python-dotenv` (for local development)
- **Deployment:** AWS Elastic Beanstalk (Python 3.9 on Amazon Linux 2023 platform)

## 📁 Project Structure

```
your_project_root/
├── .elasticbeanstalk/ (Not included in repo, please create with eb init)
│   └── config.yml
├── .gitignore
├── main.py            # Main FastAPI application code
├── requirements.txt   # Python dependencies
├── Procfile           # (Recommended) EB process definition
└── .env               # Local environment variables (DO NOT COMMIT)
```

## 🚀 Setup Instructions (Local Development)

### Prerequisites:
- Python 3.9 installed
- `pip` (Python package installer)
- Git (Optional, but recommended for version control)
- An OpenAI API Key

### Steps:

1. **Clone the Repository (if applicable):**
   ```bash
   git clone https://github.com/StrangeNPC/ai_webapp
   ```

2. **Navigate to Project Root:** 
   Ensure you are in the directory containing `main.py` and `requirements.txt`.

3. **Create and Activate Virtual Environment:**
   ```bash
   # Create venv
   python3 -m venv venv
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   
   # Activate (Windows)
   .\venv\Scripts\activate
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` File:**
   Create a file named `.env` in the project root directory (same level as `main.py`). Add your OpenAI API key:
   ```
   # .env (Ensure this file is listed in .gitignore)
   OPENAI_API_KEY=your_real_openai_api_key_here
   ```
   **Replace `your_real_openai_api_key_here` with your actual key.**

6. **Run the Backend Server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access API:**
   - The API will be running at `http://localhost:8000` or `http://127.0.0.1:8000`.
   - Access interactive documentation (Swagger UI) at `http://localhost:8000/docs`.

## ☁️ Deployment (AWS Elastic Beanstalk)

### Prerequisites:
- AWS Account
- AWS CLI configured (`aws configure`)
- EB CLI installed (`pip install awsebcli --upgrade`)

### Steps:

1. **Navigate to Project Root:**
   Ensure you are in the directory containing `main.py`, `requirements.txt` and the `.elasticbeanstalk` folder.

2. **Initialize EB (if not already done):**
   The `.elasticbeanstalk/config.yml` confirms this is likely done. The platform is set to "Python 3.9 running on 64bit Amazon Linux 2023".

3. **Create `Procfile`:**
   Create a file named `Procfile` (capital P, no extension) in the **root** of your project directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port 8080
   ```
   *Note:* Elastic Beanstalk maps public port 80 to port 8080 on the instance by default.

4. **Configure Environment Variables (CRITICAL):**
   - The `OPENAI_API_KEY` **must** be set securely in the Elastic Beanstalk environment configuration.
   - Go to your AWS Console → Elastic Beanstalk → Environments → `ai-news-analyzer-env`.
   - Click "Configuration".
   - Under the "Software" category, click "Edit".
   - Scroll down to "Environment properties".
   - Add a property:
     - **Name:** `OPENAI_API_KEY`
     - **Value:** `your_real_openai_api_key_here` (Paste your actual key)
   - Click "Apply" at the bottom. Wait for the environment to update.

5. **Deploy / Update:**
   - Ensure your latest code changes (including the `Procfile`) are saved (and committed if using Git).
   - Run the deployment command from the project root:
     ```bash
     eb deploy
     ```
   - This packages the code (using the `Procfile` if found at the root) and deploys it.

6. **Verify Deployment:**
   - Use `eb status` to check the environment health (should be Green).
   - Use `eb open` to open the application URL.
   - Test the deployed endpoint using `curl` or a tool like Postman/Insomnia:
     ```bash
     curl -X POST \
       -F 'text_content=London, UK - British politicians debated trade deals with Australian representatives. The discussions were observed by delegates from India.' \
       http://YOUR_EB_ENVIRONMENT_URL/analyze
     ```
     (Replace `YOUR_EB_ENVIRONMENT_URL` with your actual URL)
   - Use `eb logs` to check application logs if issues occur.

7. **HTTPS Configuration (Important for Secure Frontends):**
   - The current Elastic Beanstalk setup serves the API over HTTP.
   - If you connect from a frontend hosted on HTTPS, browsers will block the requests due to "mixed content".
   - To fix this, configure HTTPS on your Elastic Beanstalk environment:
     1. Ensure your environment uses an **Application Load Balancer (ALB)** (usually the default for newer platforms).
     2. Request or import an **SSL/TLS certificate** using **AWS Certificate Manager (ACM)** for your domain.
     3. Configure an **HTTPS listener (port 443)** on your environment's Load Balancer, associating it with the ACM certificate.

## 📚 API Documentation

### Root:
- `GET /`
- Returns a simple welcome message: `{"message": "Welcome to the AI News Analyzer API"}`.

### Analyze Article:
- `POST /analyze`
- **Description:** Analyzes news article text or an uploaded file (.txt or .docx) to generate a summary and extract mentioned nationalities/countries.
- **Request Body:** `multipart/form-data` containing *either*:
  - `text_content`: (string, optional) The raw text of the news article.
  - `file_upload`: (file, optional) An uploaded file (`.txt` or `.docx`).
- **Success Response (200 OK):**
  ```json
  {
    "filename": "string | null", // Name of uploaded file, or null if text was used
    "summary": "string",         // AI-generated summary
    "nationalities": ["string", ...] // List of extracted nationalities/countries
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Invalid input (e.g., no input provided, invalid file type, empty content, could not read file).
  - `413 Payload Too Large`: Input text exceeds the maximum length (currently 15000 chars).
  - `429 Too Many Requests`: OpenAI API rate limit exceeded.
  - `500 Internal Server Error`: General backend error or OpenAI API issue.
  - `503 Service Unavailable`: Error connecting to the OpenAI API.

## ⚠️ Assumptions and Limitations

- Assumes `.txt` files are encoded in UTF-8 or Latin-1.
- Relies entirely on OpenAI's API for analysis quality. Results depend on the model (`gpt-3.5-turbo` default) and the effectiveness of the prompts in `main.py`.
- The `.docx` reader extracts text from paragraphs; complex formatting, tables, or embedded objects are ignored.
- Input text length is limited to `15000` characters to manage costs and prevent abuse.
- No persistent storage (database, S3) for uploads or results is implemented in this code version.
- No user authentication or authorization.
- CORS is configured to allow all origins (`*`); this should be restricted to specific frontend domains in a production environment.
- Deployment currently uses HTTP; HTTPS setup required for secure frontend connections.
# AI News Analyzer - Backend Service

A FastAPI-based REST API that analyzes news articles using OpenAI's API to generate concise summaries and extract mentioned nationalities/countries, organizations, and people.

## 🔗 Live URLs

- **Backend API:** [Your Elastic Beanstalk Environment URL]
  - Example: `http://ai-news-analyzer-env.exampleURL.us-east-1.elasticbeanstalk.com`

## 🛠️ Technology Stack

- **Backend:** Python 3.9+
- **Framework:** FastAPI
- **Server:** Uvicorn
- **AI:** OpenAI API (defaults to `gpt-3.5-turbo`)
- **Database ORM:** SQLAlchemy
- **Database:** PostgreSQL (using `psycopg2-binary`) - *Not yet implemented*
- **File Parsing:** `python-docx`
- **Cloud:** AWS Elastic Beanstalk, AWS S3
- **Environment Variables:** `python-dotenv`
- **AWS SDK:** `boto3`

## 📚 API Documentation

### Root:
- `GET /`
- Returns a simple welcome message: `{"message": "Welcome to the AI News Analyzer API"}`.

### Analyze Article:
- `POST /analyze`
- **Description:** Analyzes news article content provided either as text or a file upload. Returns a summary and extracted entities.
- **Request:** `multipart/form-data` containing *either*:
  - `text_content`: (string, optional) Raw text content of the news article.
  - `file_upload`: (file, optional) An uploaded `.txt` or `.docx` file containing the article.
- **Success Response (200 OK):**
  ```json
  {
    "filename": "optional_original_filename.docx", // Null if text_content was used
    "s3_object_key": "optional_s3_key.docx",     // Null if S3 upload failed or wasn't used
    "summary": "A concise summary of the article...",
    "nationalities": ["American", "French", "Japanese"],
    "organizations": ["United Nations", "Example Corp"],
    "people": ["John Doe", "Jane Smith"]
  }
  ```
- **Error Responses:**
  - `400 Bad Request`: Invalid input (e.g., no input, invalid file type, empty content).
  - `413 Payload Too Large`: Input text exceeds `MAX_TEXT_LENGTH`.
  - `429 Too Many Requests`: OpenAI rate limit exceeded.
  - `500 Internal Server Error`: Unhandled server error during processing, OpenAI API issues, DB issues.
  - `503 Service Unavailable`: Cannot connect to OpenAI.

## ☁️ Deployment (AWS Elastic Beanstalk)

### Prerequisites:
- AWS Account
- AWS CLI configured (`aws configure`)
- EB CLI installed (`pip install awsebcli --upgrade`)

### Steps:

1. **Navigate to Project Root:**
   Ensure you are in the directory containing the project files.

2. **Initialize EB Application:**
   ```bash
   eb init -p "Python 3.9 running on 64bit Amazon Linux 2023" ai-news-analyzer-backend --region us-east-1
   ```
   You can adjust the platform version and region as needed.

3. **Create `Procfile`:**
   Create a file named `Procfile` (capital P, no extension) in the root directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port 8080
   ```
   *Note:* Elastic Beanstalk maps public port 80 to port 8080 on the instance by default.

4. **Create Environment:**
   ```bash
   eb create ai-news-analyzer-env
   ```
   This provisions the necessary AWS resources including EC2 instances, security groups, and load balancers.

5. **Configure Environment Variables (CRITICAL):**
   - Go to AWS Console → Elastic Beanstalk → Environments → `ai-news-analyzer-env`
   - Click "Configuration" → Under "Software" category, click "Edit"
   - Scroll down to "Environment properties" and add:
     * `OPENAI_API_KEY`: Your OpenAI API key
     * `S3_BUCKET_NAME`: Your AWS S3 bucket name for file uploads
     * `AWS_REGION`: The AWS region where your S3 bucket is located
     * `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`: Database connection details (if implementing the database feature)
   - Click "Apply" and wait for the environment to update

6. **Set Up IAM Permissions:**
   - In the AWS Console, go to IAM → Roles
   - Find the role associated with your Elastic Beanstalk EC2 instances (usually named like `aws-elasticbeanstalk-ec2-role`)
   - Attach policies allowing S3 access (S3FullAccess or a custom policy with more limited permissions)

7. **Deploy Your Application:**
   ```bash
   eb deploy
   ```
   This packages your application and deploys it to your environment.

8. **Verify Deployment:**
   - Use `eb status` to check the environment health (should be Green)
   - Use `eb open` to open the application URL
   - Access API documentation at `/docs` (Swagger UI)
   - Use `eb logs` to check application logs if issues occur

9. **HTTPS Configuration (Important for Secure Frontends):**
   - The current setup serves the API over HTTP
   - To use HTTPS, configure your Elastic Beanstalk environment:
     1. Ensure your environment uses an **Application Load Balancer (ALB)**
     2. Request or import an **SSL/TLS certificate** using **AWS Certificate Manager (ACM)**
     3. Configure an **HTTPS listener (port 443)** on your environment's Load Balancer

## ✅ Fulfilled Requirements & Bonus Points

Based on the project specification, this backend implementation achieves:

* **Requirement B (Backend):** Fully implemented.
  * REST API (`POST /analyze`)
  * Accepts text and file uploads (.txt, .docx)
  * Returns summary and nationalities using OpenAI
  * Utilizes prompt engineering for specific tasks
  * Handles invalid uploads
  * Manages configuration via environment variables

* **Requirement C (Cloud Deployment):** Fulfilled via AWS Elastic Beanstalk configuration.

* **Bonus Points Achieved:**
  * ✅ Detects Organizations and People involved
  * ✅ Saves uploaded articles (to S3)
  * ❌ Saves analysis results (PostgreSQL/RDS functionality not ready - ran out of time)
  * ✅ Uses AWS services for storage (S3)

## ⚠️ Limitations / Not Implemented

The following features are **not** included in this backend codebase:

* ❌ **User Authentication:** No login/signup or user management implemented. The API endpoint is currently public.
* ❌ **WebSocket Support:** No real-time updates are provided via WebSockets. The `/analyze` request is synchronous.
* **Multi-language Support:** While OpenAI models have multi-language capabilities, the prompts are specifically written in English. Performance on non-English articles might vary, and prompts may need tuning for optimal results in other languages.
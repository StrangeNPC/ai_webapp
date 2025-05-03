# Script Test Folder

This folder contains the scripts for both the initial backend_v1 (test_backend.py) and the update backend with RDS/S3 funcationality (test_backend_wRDS_S3.py).

## 🔗 Target API

These tests are configured to run against the deployed backend API:

- **Backend API:** `http://ai-news-analyzer-env.example.us-east-1.elasticbeanstalk.com`
  *(Note: This URL is hardcoded in the scripts; update the `BASE_URL` variable if your endpoint changes.)*

## 🧪 Technology Stack

- **Language:** Python 3
- **HTTP Client:** `requests` library
- **File Handling:** Standard Python `os` and file I/O

## 🚀 Running the Tests

### Prerequisites:
- Python 3 installed
- `pip` (Python package installer)
- The backend API must be deployed and accessible at the `BASE_URL` specified in the scripts.
- The following sample files must be present in the same directory as the test scripts:
    - `sample.txt`
    - `sample.docx` (You'll need to create a docx version of `sample.txt`'s content)
    - `sample_entities.txt`

### Installation and Setup:

1.  **Navigate to the Test Directory:**
    Ensure your terminal is in the directory containing `test_backend.py`, `test_backend_wRDS_S3.py`, and the sample files.

2.  **Install Dependencies:**
    ```bash
    pip install requests
    ```
    *(If you have other dependencies later, consider creating a `requirements-test.txt`)*

3.  **Configure Backend URL (If Necessary):**
    Open `test_backend.py` and `test_backend_wRDS_S3.py`. If your Elastic Beanstalk URL is different, update the `BASE_URL` variable at the top of both files.

4.  **Ensure Sample Files Exist:**
    Verify `sample.txt`, `sample.docx`, and `sample_entities.txt` are present.

### Executing the Tests:

1.  **Run the Core Functionality Tests:**
    ```bash
    python test_backend.py
    ```
    This script tests:
    *   Submitting text directly.
    *   Uploading a `.txt` file.
    *   Uploading a `.docx` file.
    *   Sending requests with no input (expects error).
    *   Sending requests with empty text input (expects error).
    *   Checks for `summary` and `nationalities` in successful responses.

2.  **Run the Extended Feature Tests (S3/Entities):**
    ```bash
    python test_backend_wRDS_S3.py
    ```
    This script tests:
    *   Submitting text and checking for `organizations` and `people`.
    *   Uploading a file (`sample_entities.txt`) and checking for `organizations`, `people`, *and* the presence/format of the `s3_object_key`.
    *   Verifies that the `filename` and `s3_object_key` fields are correctly populated (or `None`) based on the input type.

## ✅ Test Coverage Summary

*   **`test_backend.py` (Core Tests):**
    *   `test_analyze_text`: Verifies analysis via direct text submission. Checks summary/nationalities.
    *   `test_analyze_txt_upload`: Verifies analysis via `.txt` file upload. Checks summary/nationalities.
    *   `test_analyze_docx_upload`: Verifies analysis via `.docx` file upload. Checks summary/nationalities.
    *   `test_analyze_no_input`: Ensures the API returns an error (400) when no input is provided.
    *   `test_analyze_empty_text`: Ensures the API returns an error (400) for effectively empty text input.
*   **`test_backend_wRDS_S3.py` (Extended/Bonus Tests):**
    *   `test_analyze_text_with_entities`: Verifies analysis via text input, focusing on correct extraction of `organizations` and `people`. Checks that `s3_object_key` is `None`.
    *   `test_analyze_file_with_entities_and_s3`: Verifies analysis via file upload (`.txt`), checking for `organizations`, `people`, and validating the presence and format of the `s3_object_key`. Also checks the returned `filename`.

## 📝 Notes & Assumptions

*   These tests require the backend API to be running and accessible over the network.
*   The tests validate the *structure* and *presence* of expected data (summary, nationalities, orgs, people, S3 key) in the API response.
*   Due to the nature of Large Language Models (LLMs), the *exact wording* of summaries or the precise list/casing of extracted entities might vary slightly between runs. The tests include checks that are reasonably robust to minor variations (e.g., checking if expected items are *present* in the list).
*   You need to manually create `sample.docx` with the same content as `sample.txt` for the `test_analyze_docx_upload` test case to function correctly.
# test_backend.py
import requests
import os
import json

# --- Configuration ---
# Use http or https depending on your Beanstalk setup
BASE_URL = "http://ai-news-analyzer-env.eba-ny77vj8c.us-east-1.elasticbeanstalk.com"
ANALYZE_ENDPOINT = f"{BASE_URL}/analyze"
SAMPLE_TEXT_FILE = "sample.txt"
SAMPLE_DOCX_FILE = "sample.docx"

# --- Helper Functions ---
def print_status(test_name, success, message=""):
    status = "PASSED" if success else "FAILED"
    print(f"Test: {test_name:<30} Status: {status:<8} {message}")

def check_response(response, expected_status=200):
    """Checks basic response validity"""
    if response.status_code != expected_status:
        return False, f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
    try:
        data = response.json()
        if expected_status == 200:
            if "summary" not in data or "nationalities" not in data:
                return False, f"Missing 'summary' or 'nationalities' in response: {data}"
            if not isinstance(data["summary"], str):
                 return False, f"'summary' is not a string: {data['summary']}"
            if not isinstance(data["nationalities"], list):
                 return False, f"'nationalities' is not a list: {data['nationalities']}"
        return True, data # Return parsed data on success
    except json.JSONDecodeError:
        return False, f"Response is not valid JSON: {response.text}"
    except Exception as e:
        return False, f"Unexpected error checking response: {e}"

# --- Test Cases ---
def test_analyze_text():
    test_name = "Analyze via Text Input"
    payload = {
        'text_content': "London, UK - British politicians debated trade deals with Australian representatives. The discussions were observed by delegates from India."
    }
    try:
        response = requests.post(ANALYZE_ENDPOINT, data=payload)
        # --- Inside test_analyze_text() ---
        success, result = check_response(response)
        if success:
            # More robust check for LLM variability
            actual_nationalities = result.get("nationalities", [])
            expected_present = ["British", "Australian"] # Core ones
            # Check if either India or Indian is present
            india_present = any(n.lower() == "india" or n.lower() == "indian" for n in actual_nationalities)

            # Check if core expected ones are present AND India/Indian is present
            if all(exp in actual_nationalities for exp in expected_present) and india_present:
                print_status(test_name, True, f"Summary: '{result.get('summary', '')[:50]}...', Nationalities: {actual_nationalities}")
            else:
                missing = [exp for exp in expected_present if exp not in actual_nationalities]
                if not india_present: missing.append("India/Indian")
                print_status(test_name, False, f"Expected nationalities missing/incorrect. Missing: {missing}. Got: {actual_nationalities}")
        else:
            print_status(test_name, False, result) # result contains the error message
    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")

def test_analyze_txt_upload():
    test_name = "Analyze via TXT Upload"
    if not os.path.exists(SAMPLE_TEXT_FILE):
        print_status(test_name, False, f"Sample file not found: {SAMPLE_TEXT_FILE}")
        return

    try:
        with open(SAMPLE_TEXT_FILE, 'rb') as f:
            files = {'file_upload': (SAMPLE_TEXT_FILE, f, 'text/plain')}
            response = requests.post(ANALYZE_ENDPOINT, files=files)

        success, result = check_response(response)
        if success:
             # Basic content check
            expected = ["French", "Canadian", "Japanese", "German", "American"]
            actual = result.get("nationalities", [])
            if not all(nat in actual for nat in expected):
                 print_status(test_name, False, f"Nationalities might be incorrect. Expected approx: {expected}, Got: {actual}")
            else:
                print_status(test_name, True, f"Summary: '{result.get('summary', '')[:50]}...', Nationalities: {actual}")
        else:
            print_status(test_name, False, result)
    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")
    except Exception as e:
        print_status(test_name, False, f"An error occurred: {e}")

def test_analyze_docx_upload():
    test_name = "Analyze via DOCX Upload"
    if not os.path.exists(SAMPLE_DOCX_FILE):
        print_status(test_name, False, f"Sample file not found: {SAMPLE_DOCX_FILE}")
        return

    try:
        with open(SAMPLE_DOCX_FILE, 'rb') as f:
            files = {'file_upload': (SAMPLE_DOCX_FILE, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(ANALYZE_ENDPOINT, files=files)

        success, result = check_response(response)
        if success:
             # Basic content check (same as TXT)
            expected = ["French", "Canadian", "Japanese", "German", "American"]
            actual = result.get("nationalities", [])
            if not all(nat in actual for nat in expected):
                 print_status(test_name, False, f"Nationalities might be incorrect. Expected approx: {expected}, Got: {actual}")
            else:
                 print_status(test_name, True, f"Summary: '{result.get('summary', '')[:50]}...', Nationalities: {actual}")

        else:
            print_status(test_name, False, result)
    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")
    except Exception as e:
        print_status(test_name, False, f"An error occurred: {e}")

def test_analyze_no_input():
    test_name = "Analyze with No Input"
    try:
        response = requests.post(ANALYZE_ENDPOINT)
        # Expecting a 400 Bad Request or similar
        success, result = check_response(response, expected_status=400)
        print_status(test_name, success, f"Got expected status {response.status_code}")
        if not success:
             print(f"    Detail: {result}")
    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")

def test_analyze_empty_text():
    test_name = "Analyze with Empty Text"
    payload = {'text_content': '  '}
    try:
        response = requests.post(ANALYZE_ENDPOINT, data=payload)
        success, result = check_response(response, expected_status=400)
        print_status(test_name, success, f"Got expected status {response.status_code}")
        if not success:
            print(f"    Detail: {result}")
    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")

# --- Run Tests ---
if __name__ == "__main__":
    print(f"--- Testing Backend at {BASE_URL} ---")
    test_analyze_text()
    test_analyze_txt_upload()
    test_analyze_docx_upload()
    test_analyze_no_input()
    test_analyze_empty_text()
    print("--- Testing Complete ---")
# test_backend_extended.py
import requests
import os
import json
import time # For potential delays if needed

# --- Configuration ---
# Use http or https depending on your Beanstalk setup
BASE_URL = "http://ai-news-analyzer-env.example.us-east-1.elasticbeanstalk.com" # Make sure this is correct
ANALYZE_ENDPOINT = f"{BASE_URL}/analyze"
SAMPLE_ENTITIES_FILE = "sample_entities.txt" # New sample file

# --- Helper Functions ---
def print_status(test_name, success, message=""):
    status = "PASSED" if success else "FAILED"
    print(f"Test: {test_name:<45} Status: {status:<8} {message}")

def check_extended_response(response, expect_s3_key=False, expected_filename=None, expected_status=200):
    """Checks response validity including entities and optional S3 key."""
    if response.status_code != expected_status:
        return False, f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
    try:
        data = response.json()
        if expected_status == 200:
            # Check core fields exist
            required_fields = ["summary", "nationalities", "organizations", "people"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return False, f"Missing required fields {missing_fields} in response: {data}"

            # Check types
            if not isinstance(data.get("summary"), str):
                 return False, f"'summary' is not a string: {data.get('summary')}"
            if not isinstance(data.get("nationalities"), list):
                 return False, f"'nationalities' is not a list: {data.get('nationalities')}"
            if not isinstance(data.get("organizations"), list):
                 return False, f"'organizations' is not a list: {data.get('organizations')}"
            if not isinstance(data.get("people"), list):
                 return False, f"'people' is not a list: {data.get('people')}"

            # Check S3 key if expected
            s3_key = data.get("s3_object_key")
            if expect_s3_key:
                if not s3_key:
                    return False, f"Expected 's3_object_key' but it was missing or None. Response: {data}"
                if not isinstance(s3_key, str):
                    return False, f"Expected 's3_object_key' to be a string, got {type(s3_key)}. Response: {data}"
                if not s3_key.startswith("uploads/"):
                     return False, f"'s3_object_key' does not start with 'uploads/': {s3_key}"
                # Check extension matches uploaded file if filename provided
                if expected_filename:
                    expected_ext = os.path.splitext(expected_filename)[1].lower()
                    if not s3_key.lower().endswith(expected_ext):
                         return False, f"'s3_object_key' extension mismatch. Expected {expected_ext}, Key: {s3_key}"
            else:
                # If not expecting S3 key (e.g., text input), it should be None
                if s3_key is not None:
                    return False, f"Did not expect 's3_object_key', but got: {s3_key}. Response: {data}"

            # Check filename if expected
            if expected_filename:
                 if data.get("filename") != expected_filename:
                      return False, f"Expected filename '{expected_filename}', got '{data.get('filename')}'"

        return True, data # Return parsed data on success
    except json.JSONDecodeError:
        return False, f"Response is not valid JSON: {response.text}"
    except Exception as e:
        return False, f"Unexpected error checking response: {e}"

# --- Test Cases for Extended Features ---

def test_analyze_text_with_entities():
    """Tests text input, focusing on organization and people extraction."""
    test_name = "Analyze Text Input (Orgs & People)"
    payload = {
        'text_content': "Paris, France - The United Nations held a conference attended by President Macron and Dr. Evelyn Reed. Greenpeace and Acme Corp were mentioned."
    }
    # Expected items (LLM output can vary slightly, check for presence)
    expected_nationalities = ["French"] # Or France
    expected_orgs = ["United Nations", "Greenpeace", "Acme Corp"]
    expected_people = ["President Macron", "Dr. Evelyn Reed"] # Or just Macron, Evelyn Reed

    try:
        response = requests.post(ANALYZE_ENDPOINT, data=payload)
        success, result = check_extended_response(response, expect_s3_key=False) # No S3 key for text input

        if success:
            actual_nats = result.get("nationalities", [])
            actual_orgs = result.get("organizations", [])
            actual_people = result.get("people", [])

            # Check for presence of expected items (more robust for LLM variations)
            nats_ok = any(n.lower() in ["french", "france"] for n in actual_nats)
            orgs_ok = all(any(exp.lower() in act.lower() for act in actual_orgs) for exp in expected_orgs)
            people_ok = all(any(exp.lower() in act.lower() for act in actual_people) for exp in expected_people)

            if nats_ok and orgs_ok and people_ok:
                print_status(test_name, True, f"Orgs: {actual_orgs}, People: {actual_people}")
            else:
                error_msg = []
                if not nats_ok: error_msg.append(f"Nats Failed: Expected ~{expected_nationalities}, Got {actual_nats}")
                if not orgs_ok: error_msg.append(f"Orgs Failed: Expected ~{expected_orgs}, Got {actual_orgs}")
                if not people_ok: error_msg.append(f"People Failed: Expected ~{expected_people}, Got {actual_people}")
                print_status(test_name, False, "; ".join(error_msg))
        else:
            print_status(test_name, False, result) # result contains the error message

    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")
    except Exception as e:
         print_status(test_name, False, f"An error occurred: {e}")


def test_analyze_file_with_entities_and_s3():
    """Tests file upload, checking entities and S3 key presence."""
    test_name = "Analyze File Input (Entities & S3 Key)"
    if not os.path.exists(SAMPLE_ENTITIES_FILE):
        print_status(test_name, False, f"Sample file not found: {SAMPLE_ENTITIES_FILE}")
        return

    # Expected items from sample_entities.txt (adjust based on LLM results)
    expected_nationalities = ["French", "German", "American"] # Or France, Germany, USA etc.
    expected_orgs = ["United Nations", "Greenpeace", "World Wildlife Fund (WWF)", "Acme Corp", "Globex Corporation"]
    expected_people = ["President Macron", "Chancellor Scholz", "Dr. Evelyn Reed"] # Or Macron, Scholz, Evelyn Reed

    try:
        with open(SAMPLE_ENTITIES_FILE, 'rb') as f:
            files = {'file_upload': (SAMPLE_ENTITIES_FILE, f, 'text/plain')}
            response = requests.post(ANALYZE_ENDPOINT, files=files)

        # Expect S3 key for file uploads
        success, result = check_extended_response(response, expect_s3_key=True, expected_filename=SAMPLE_ENTITIES_FILE)

        if success:
            actual_nats = result.get("nationalities", [])
            actual_orgs = result.get("organizations", [])
            actual_people = result.get("people", [])

            nats_ok = all(exp in actual_nats for exp in expected_nationalities)
            orgs_ok = all(exp in actual_orgs for exp in expected_orgs)
            people_ok = all(exp in actual_people for exp in expected_people)


            if nats_ok and orgs_ok and people_ok: # Add 'and lengths_match' if you want stricter check
                print_status(test_name, True, f"Orgs: {actual_orgs}, People: {actual_people}, S3 Key: {result.get('s3_object_key')}")
            else:
                error_msg = []
                # Provide more detail on failure
                if not nats_ok:
                    missing_nats = [n for n in expected_nationalities if n not in actual_nats]
                    error_msg.append(f"Nats Failed: Missing {missing_nats}. Got {actual_nats}")
                if not orgs_ok:
                    missing_orgs = [o for o in expected_orgs if o not in actual_orgs]
                    error_msg.append(f"Orgs Failed: Missing {missing_orgs}. Got {actual_orgs}")
                if not people_ok:
                    missing_people = [p for p in expected_people if p not in actual_people]
                    error_msg.append(f"People Failed: Missing {missing_people}. Got {actual_people}")
                # if not lengths_match: error_msg.append("List lengths mismatch.")

                print_status(test_name, False, "; ".join(error_msg))
        else:
            print_status(test_name, False, result) # result contains the error message

    except requests.exceptions.RequestException as e:
        print_status(test_name, False, f"Request failed: {e}")
    except Exception as e:
         print_status(test_name, False, f"An error occurred: {e}")

# --- Run Tests ---
if __name__ == "__main__":
    print(f"--- Testing Extended Backend Features at {BASE_URL} ---")
    # Add a small delay in case the server needs a moment after deployment
    # time.sleep(2)
    test_analyze_text_with_entities()
    test_analyze_file_with_entities_and_s3()
    print("--- Extended Testing Complete ---")
import openai
from fastapi import HTTPException
from typing import List, Dict
from backend.core.config import settings

# Initialize OpenAI client 
client = None
if settings.OPENAI_API_KEY:
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
else:
    print("OpenAI API Key not found, client not initialized.")


def get_openai_completion(prompt_text: str, model: str = settings.OPENAI_MODEL) -> str:
    """Calls the OpenAI Chat Completion API."""
    if not client:
         raise HTTPException(status_code=500, detail="OpenAI client is not configured or initialized on the server.")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in analyzing news articles."},
                {"role": "user", "content": prompt_text}
            ]
        )
        if response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            if message and message.content:
                # Check finish reason for truncation
                finish_reason = response.choices[0].finish_reason
                if finish_reason == 'length':
                    print(f"Warning: OpenAI response truncated due to model's length limit for prompt: '{prompt_text[:100]}...'")
                return message.content.strip()

        # Handle unexpected response structure
        print(f"Warning: Could not extract content from OpenAI response. Response: {response}")
        finish_reason = response.choices[0].finish_reason if response.choices else "unknown"
        return f"Error: Could not extract valid content from OpenAI. Finish reason: {finish_reason}"

    except openai.APIError as e:
         print(f"OpenAI API returned an API Error: {e}")
         raise HTTPException(status_code=e.status_code or 500, detail=f"OpenAI API Error: {e.body.get('message', str(e)) if e.body else str(e)}")
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        raise HTTPException(status_code=503, detail=f"OpenAI Connection Error: Failed to connect.")
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        raise HTTPException(status_code=429, detail=f"OpenAI Rate Limit Exceeded: {e.body.get('message', 'Please try again later.') if e.body else 'Please try again later.'}")
    except openai.AuthenticationError as e:
        print(f"OpenAI Authentication Error: {e}")
        # Sensitive details not revealed in error message!
        raise HTTPException(status_code=401, detail="OpenAI Authentication Error: Invalid API Key or credentials.")
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI call: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred during OpenAI call.")


def summarize_text(text: str) -> str:
    """Generates a summary using OpenAI."""
    prompt = f"""
    Please summarize the following news article in 2-4 concise sentences. Focus on the main events and key entities involved.

    Article:
    \"\"\"
    {text}
    \"\"\"

    Concise Summary:
    """
    summary = get_openai_completion(prompt)
    # Basic check if the result looks like an error message itself
    if summary.startswith("Error:") or summary.startswith("OpenAI returned"):
         print(f"Warning: Summary generation might have failed. Result: {summary}")
         return "Could not generate summary due to an issue."
    return summary

def extract_nationalities(text: str) -> List[str]:
    """Extracts nationalities/countries using OpenAI."""
    prompt = f"""
    Analyze the following news article. List all explicitly mentioned nationalities (e.g., French, Canadian), countries (e.g., Germany, Japan), or demonyms referring to peoples of specific nations (e.g., the British, Americans).
    Provide the output ONLY as a comma-separated list.
    If no relevant terms are found, respond ONLY with the word "None". Do not add explanations.

    Article:
    \"\"\"
    {text}
    \"\"\"

    Nationalities/Countries mentioned (comma-separated list or None):
    """
    result = get_openai_completion(prompt)
    if result and isinstance(result, str) and not result.startswith("Error:"):
        result_lower = result.strip().lower()
        if result_lower == "none" or not result.strip():
            return []
        # Split and clean
        return sorted(list(set(item.strip() for item in result.split(',') if item.strip()))) # Unique, sorted list
    else:
        print(f"Warning/Error extracting nationalities: {result}")
        return []

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extracts Organizations and People using OpenAI."""
    prompt = f"""
    Analyze the news article below. Identify and extract:
    1.  Organizations: Companies, political parties, NGOs, government bodies, agencies (e.g., UN, NATO, FBI), specific military units if named.
    2.  People: Distinct individuals mentioned by full name or clearly identifiable name (e.g., President Biden, Ms. Ardern). Avoid generic titles without names.

    Provide the output STRICTLY in the following format, with each list comma-separated.
    If no entities are found for a category, write the word "None" for that category's list. Do not include any other text, labels, or explanations.

    Article:
    \"\"\"
    {text}
    \"\"\"

    Organizations: [Comma-separated list of organizations or None]
    People: [Comma-separated list of people or None]
    """
    result = get_openai_completion(prompt)
    entities = {"organizations": [], "people": []}

    if result and isinstance(result, str) and not result.startswith("Error:"):
        lines = result.split('\n')
        for line in lines:
            line_lower = line.lower()
            try:
                if line_lower.startswith("organizations:"):
                    content = line.split(":", 1)[1].strip()
                    if content.lower() != "none" and content:
                        entities["organizations"] = sorted(list(set(item.strip() for item in content.split(',') if item.strip())))
                elif line_lower.startswith("people:"):
                    content = line.split(":", 1)[1].strip()
                    if content.lower() != "none" and content:
                         entities["people"] = sorted(list(set(item.strip() for item in content.split(',') if item.strip())))
            except IndexError:
                print(f"Warning: Malformed line in entity extraction response: '{line}'")
                continue
        # Verify if parsing actually happened, maybe the response format was wrong
        if not entities["organizations"] and not entities["people"] and "none" not in result.lower():
             print(f"Warning: Could not parse entities from potentially valid response: {result}")

    else:
        print(f"Warning/Error extracting entities: {result}")

    return entities
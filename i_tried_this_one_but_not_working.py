import os
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
import vertexai.preview.generative_models as generative_models
from google.oauth2.credentials import Credentials

# Set up your Google Cloud credentials and Vertex AI
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/User/Music/learn/bilvantis-learning-portal-backend-e_learning_pre_prod/AI_Modle/service.json"

vertexai.init(project="fast-cascade-369003", location="us-central1")
model = GenerativeModel("gemini-1.5-flash-001")

# Define the generation config and safety settings globally
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.5,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def add_line_numbers(code_content):
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def prompt(code_content, previous_response):
    return f"""Please analyze the provided code snippet and provide the following information:
1. ** Syntax Errors :**
    - ** Identification **: Identify the exact error-causing line numbers and provide the exact syntax errors.
    - ** Explanation **: Provide a clear and concise explanation of each error.
    - ** Fix **: Suggest a specific fix for each identified error, providing only the necessary code to correct it without rewriting the entire code.

2. ** Code Bugs :**
    - ** Identification **: Identify potential logical or runtime errors in the code.
    - ** Explanation **: Provide a detailed explanation of why the identified code segment is problematic.
    - ** Fix **: Suggest the necessary code changes to fix the bugs without rewriting the entire code.

3. ** Security Vulnerabilities :**
    - ** Identification **: Highlight any potential security vulnerabilities in the code (e.g., SQL injection, XSS, insecure deserialization).
    - ** Explanation **: Provide a clear explanation of each identified vulnerability.
    - ** Fix **: Suggest code changes to mitigate the security risks without rewriting the entire code.

4. ** Duplicate Code :**
    - ** Identification **: Highlight sections of the code lines that are duplicated.
    - ** Suggestion **: Provide recommendations without rewriting the entire code.

5. ** Code Improvement Suggestions :**
    - ** Identification **: Highlight sections of the code that can be improved.
        - This could include:
        - Unnecessary complexity
        - Redundant code blocks
        - Potential for using more concise constructs (e.g., list comprehensions, loops)
    - ** Suggestion **: Provide specific points for improvement and the necessary code changes without rewriting the entire code.
    - ** Note **: If no code improvement suggestions are found, simply state "No Code Improvement Suggestions Found."

6. ** Compare with Previous Response: **
    - ** Previous Response **: {previous_response}
    - ** Unique Points **: Highlight any new or unique issues or suggestions compared to the previous response.

** The Code :**
{code_content}
"""

def generate_content_for_review(code_content, previous_response):
    response_text = ""
    try:
        responses = model.generate_content(
            [prompt(code_content, previous_response)],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )
        for response in responses:
            response_text += response.text

    except ValueError as e:
        if "SAFETY" in str(e):
            print(f"WARNING: Generated content blocked by safety filters: {e}")
            print(f"Response Details: {response}")
        else:
            raise e

    return response_text

def compare_responses(old_response, new_response):
    old_lines = set(old_response.split('\n'))
    new_lines = set(new_response.split('\n'))
    unique_lines = new_lines - old_lines
    return '\n'.join(unique_lines)

def process_directory(directory_path, old_sql_response_path, new_sql_response_path, final_sql_response_path):
    sql_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.sqlx')]

    # Read the old SQL response file
    if os.path.exists(old_sql_response_path):
        with open(old_sql_response_path, 'r') as old_file:
            old_sql_response = old_file.read()
    else:
        old_sql_response = ""

    with open(new_sql_response_path, 'w') as new_file:
        for file_path in sql_files:
            code_content = read_file_content(file_path)
            code_content_with_line_numbers = add_line_numbers(code_content)
            print(f"\n\nReviewing file: {file_path}")
            new_response_text = generate_content_for_review(code_content_with_line_numbers, old_sql_response)
            if new_response_text.strip():
                new_file.write(f"\n\nReview for file: {file_path}\n")
                new_file.write(new_response_text)
            else:
                new_file.write(f"\n\nReview for file: {file_path}\n")
                new_file.write("No response received from the AI model.")

    # Compare the old and new responses and write unique points to final_sql_response.txt
    if os.path.exists(new_sql_response_path):
        with open(new_sql_response_path, 'r') as new_file:
            new_sql_response = new_file.read()

        unique_points = compare_responses(old_sql_response, new_sql_response)
        with open(final_sql_response_path, 'w') as final_file:
            final_file.write(unique_points)

def main():
    # Directory paths
    sql_dir = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/sql/"
    old_sql_response_file = "C:/Users/User/PycharmProjects/Ai_Modle/code/old_sql_response.txt"
    new_sql_response_file = "C:/Users/User/PycharmProjects/Ai_Modle/code/new_sql_response.txt"
    final_sql_response_file = "C:/Users/User/PycharmProjects/Ai_Modle/code/final_sql_response.txt"

    # Processing directories
    process_directory(sql_dir, old_sql_response_file, new_sql_response_file, final_sql_response_file)

if __name__ == "__main__":
    main()

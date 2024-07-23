import os
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
import vertexai.preview.generative_models as generative_models
from google.oauth2.credentials import Credentials

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/User/Music/learn/bilvantis-learning-portal-backend-e_learning_pre_prod/AI_Modle/service.json"


# Function to read the content of the file
def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def add_line_numbers(code_content):
    lines = code_content.split('\n')
    numbered_lines = [f"Line {i + 1}: {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)


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


def generate_content_for_review(code_content):
    response_text = ""
    try:
        responses = model.generate_content(
            [prompt(code_content)],
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


def prompt(code_content):
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
6. ** Don't write any kind of code or code snippet in the output: **
    - They shouldn't be any code in the output.

** The Code :**
{code_content}
"""


def process_directory(directory_path, output_file_path):
    code_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if
                  file.endswith(('.py', '.sqlx', '.py'))]

    with open(output_file_path, 'w') as output_file:
        for file_path in code_files:
            code_content = read_file_content(file_path)
            code_content_with_line_numbers = add_line_numbers(code_content)
            print(f"\n\nReviewing file: {file_path}")
            response_text = generate_content_for_review(code_content_with_line_numbers)
            if response_text.strip():
                output_file.write(f"\n\nReview for file: {file_path}\n")
                output_file.write(response_text)
            else:
                output_file.write(f"\n\nReview for file: {file_path}\n")
                output_file.write("No response received from the AI model.")


def main():
    # Directory paths
    python_dir = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/python/"
    # Output file paths
    python_response_file = "C:/Users/User/PycharmProjects/Ai_Modle/code/dataform/Python_response.txt"

    # Processing directories
    process_directory(python_dir, python_response_file)


if __name__ == "__main__":
    main()

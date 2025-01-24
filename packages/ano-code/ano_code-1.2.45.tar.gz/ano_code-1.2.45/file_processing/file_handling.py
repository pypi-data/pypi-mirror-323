import os
import time
import requests
from transformers import GPT2Tokenizer
from yaspin import yaspin
from ai_assistant.llm_cli import groq_client
from ai_assistant.prompt_llm import AIAssistant
from ai_assistant.consts import COMMANDS
# Assuming you have already imported and set up `AIAssistant` and `COMMANDS`
# e.g., from your_module import AIAssistant, COMMANDS, openai_client
import tiktoken


import pathspec

def parse_gitignore(gitignore_path):
    """Parse .gitignore and return a PathSpec object."""
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
            patterns = gitignore_file.read().splitlines()
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    except FileNotFoundError:
        return None  # If .gitignore doesn't exist
    except Exception as e:
        print(f"Error reading .gitignore: {e}")
        return None

def process_file(file_path):
    """Reads the content of a file and returns it as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # Store file content in a string
            return content
    except Exception as e:
        return None

# Function to count tokens
# def count_tokens(text):
#     tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
#     tokens = tokenizer.encode(text, add_special_tokens=False)
#     return len(tokens)
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")  # Use the appropriate encoding for your model
    tokens = encoding.encode(text)
    return len(tokens)

# Function to read all files from a folder and combine their content
def read_folder_content(directory):
    """Read all files from a folder, ignoring those specified in .gitignore."""
    gitignore_path = os.path.join(directory, '.gitignore')
    spec = parse_gitignore(gitignore_path)

    fl = {".py", ".js", ".go", ".ts", ".tsx", ".jsx", ".dart", ".php", "Dockerfile", "docker-compose.yml"}
    combined_content = ""

    for root, dirs, files in os.walk(directory):
        # Filter directories based on .gitignore rules
        if spec:
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(root, d))]

        for filename in files:
            file_path = os.path.join(root, filename)
            
            # Ignore files based on .gitignore and extensions
            if spec and spec.match_file(file_path):
                continue
            if not filename.endswith(tuple(fl)):
                continue
            
            # Read and combine file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_content += f.read() + "\n"
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

    return combined_content
# Function to split content into chunks within the token limit
def split_content_into_chunks(content, max_tokens):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for line in content.splitlines():
        line_tokens = tokenizer.encode(line, add_special_tokens=False)
        if current_tokens + len(line_tokens) > max_tokens:
            # Save the current chunk and reset
            chunks.append(current_chunk.strip())
            current_chunk = ""
            current_tokens = 0
        # Add the line to the current chunk
        current_chunk += line + "\n"
        current_tokens += len(line_tokens)

    # Add the last chunk if it has any content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

# Your existing `prompt` function
def prompt(code: str):
    loader = yaspin()
    loader.start()
    assistant = AIAssistant(groq_client)
    result = assistant.run_assistant(code, COMMANDS["w_doc"])
    loader.stop()
    return result

# Function to send generated documentation to an API
def send_to_api(api_url, code_doc, repo_id):
    payload = {
        "code_doc": code_doc,
        "repo_id": repo_id,
    }
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"Successfully sent documentation to API for repo_id '{repo_id}'.")
        else:
            print(f"Failed to send documentation for repo_id '{repo_id}'. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending to API: {e}")

        # folders_to_ignore = {".pytest_cache", "__pycache__", "node_modules", "dist", "ano_code",".egg-info auto-code-env", ".git", ".vscode"}


def run_req(base_folder_path: str, api_url: str, repo_id: str):
    # Token limit for LLM
    max_tokens_per_request = 10_000

    for folder_name in os.listdir(base_folder_path):
        folder_path = os.path.join(base_folder_path, folder_name)
        
        # Skip ignored folders
        if folder_name in {".git", ".vscode", ".pytest_cache", "__pycache__", "node_modules", "dist", "venv", ".github", "ano_code",".egg-info auto-code-env", ".git", ".vscode", "auto_code.egg-info"}:
            continue

        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}...")

            # Read folder content
            folder_content = read_folder_content(folder_path)

            # Check token count
            num_tokens = count_tokens(folder_content)
            print(f"Folder '{folder_name}' has {num_tokens} tokens.")

            # Split content into chunks if needed
            if num_tokens > max_tokens_per_request:
                print(f"Splitting folder '{folder_name}' content into smaller chunks...")
                chunks = split_content_into_chunks(folder_content, max_tokens_per_request)
            else:
                chunks = [folder_content]

            # Generate and send documentation for each chunk
            responses = []
            for i, chunk in enumerate(chunks):
                print(f"Prompting LLM with chunk {i + 1}/{len(chunks)} of folder '{folder_name}'...")
                response = prompt(chunk)
                if response:
                    responses.append(response)
                else:
                    print(f"Failed to get response for chunk {i + 1}.")
                time.sleep(1)  # Avoid hitting rate limits

            # Combine responses and generate documentation
            combined_responses = "\n".join(responses)
            documentation_response = prompt(
                f"Based on the following responses from folder contents, generate a comprehensive code documentation:\n\n{combined_responses}"
            )

            if documentation_response:
                print(f"Generated code documentation for folder '{folder_name}'.")
                send_to_api(api_url, documentation_response, repo_id)
            else:
                print(f"Failed to generate documentation for folder '{folder_name}'.")

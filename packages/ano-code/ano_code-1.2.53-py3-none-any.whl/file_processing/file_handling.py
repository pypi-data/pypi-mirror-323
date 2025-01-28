import os
import time
import requests
from transformers import GPT2Tokenizer
from yaspin import yaspin
from ai_assistant.llm_cli import groq_client
from ai_assistant.prompt_llm import AIAssistant
from ai_assistant.consts import COMMANDS
import tiktoken
import pathspec

def parse_gitignore(gitignore_path):
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as gitignore_file:
            patterns = gitignore_file.read().splitlines()
            return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading .gitignore: {e}")
        return None

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except Exception as e:
        return None

# Count tokens using the appropriate tokenizer
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")  # Adjust this for your LLM
    tokens = encoding.encode(text)
    return len(tokens)

# Read folder content and respect .gitignore
def read_folder_content(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    spec = parse_gitignore(gitignore_path)

    extensions = {".py", ".js", ".go", ".ts", ".tsx", ".jsx", ".dart", ".php", "Dockerfile", "docker-compose.yml"}
    combined_content = ""

    for root, dirs, files in os.walk(directory):
        if spec:
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(root, d))]
        for filename in files:
            file_path = os.path.join(root, filename)
            if spec and spec.match_file(file_path):
                continue
            if not filename.endswith(tuple(extensions)):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_content += f.read() + "\n"
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")
    return combined_content

# Split content into chunks within token limits
def split_content_into_chunks(content, max_tokens):
    encoding = tiktoken.get_encoding("cl100k_base")  # Use appropriate encoding
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for line in content.splitlines():
        line_tokens = encoding.encode(line)
        if current_tokens + len(line_tokens) > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = ""
            current_tokens = 0
        current_chunk += line + "\n"
        current_tokens += len(line_tokens)

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks

# Prompt the LLM
def prompt(code):
    loader = yaspin()
    loader.start()
    assistant = AIAssistant(groq_client)
    result = assistant.run_assistant(code, COMMANDS["w_doc"])
    loader.stop()
    return result

# Send generated documentation to an API
def send_to_api(api_url, code_doc, repo_id):
    payload = {"code_doc": code_doc, "repo_id": repo_id}
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"Successfully sent documentation to API for repo_id '{repo_id}'.")
        else:
            print(f"Failed to send documentation for repo_id '{repo_id}'. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending to API: {e}")

# Main function with rate limiting
def run_req(base_folder_path, api_url, repo_id):
    max_tokens_per_request = 6000
    max_tokens_per_hour = 100000
    tokens_used = 0
    reset_interval = 3600  # 1 hour in seconds
    start_time = time.time()

    folder_responses = {}

    for folder_name in os.listdir(base_folder_path):
        folder_path = os.path.join(base_folder_path, folder_name)

        if folder_name in {".yarn", ".git", ".vscode", ".pytest_cache", "__pycache__", "node_modules", "auto-code-env", "dist", "venv", ".github", "ano_code", ".egg-info"}:
            continue

        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}...")

            folder_content = read_folder_content(folder_path)
            num_tokens = count_tokens(folder_content)
            if num_tokens == 0:
                print(f"Folder '{folder_name}' is empty or ignored.")
                continue
            print(f"Folder '{folder_name}' has {num_tokens} tokens.")

            if num_tokens > max_tokens_per_request:
                print(f"Splitting folder '{folder_name}' content into smaller chunks...")
                chunks = split_content_into_chunks(folder_content, max_tokens_per_request)
            else:
                chunks = [folder_content]

            responses = []
            for i, chunk in enumerate(chunks):
                while tokens_used + count_tokens(chunk) > max_tokens_per_hour:
                    elapsed_time = time.time() - start_time
                    if elapsed_time < reset_interval:
                        wait_time = reset_interval - elapsed_time
                        print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                        tokens_used = 0
                        start_time = time.time()
                    else:
                        tokens_used = 0
                        start_time = time.time()

                print(f"Prompting LLM with chunk {i + 1}/{len(chunks)} of folder '{folder_name}'...")
                response = prompt(chunk)
                if response:
                    responses.append(response)
                    tokens_used += count_tokens(chunk)
                else:
                    print(f"Failed to get response for chunk {i + 1}.")
                time.sleep(1)  # To avoid rapid requests

            combined_responses = "\n".join(responses)
            folder_responses[folder_name] = combined_responses

    all_responses_combined = ""
    for folder_name, responses in folder_responses.items():
        all_responses_combined += f"## Documentation for {folder_name}:\n{responses}\n\n"

    print("Generating comprehensive documentation for all folders...")
    final_documentation = prompt(
        f"Based on the following folder-specific responses, generate a comprehensive code documentation:\n\n{all_responses_combined}"
    )

    if final_documentation:
        print("Final documentation generated. Sending to API...")
        send_to_api(api_url, final_documentation, repo_id)
    else:
        print("Failed to generate the final documentation.")

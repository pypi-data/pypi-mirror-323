import os
import time
import requests
from transformers import GPT2Tokenizer
from yaspin import yaspin
from ai_assistant.llm_cli import openai_client
from ai_assistant.prompt_llm import AIAssistant
from ai_assistant.consts import COMMANDS
# Assuming you have already imported and set up `AIAssistant` and `COMMANDS`
# e.g., from your_module import AIAssistant, COMMANDS, openai_client

# Function to count tokens
def count_tokens(text):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens)

# Function to read all files from a folder and combine their content
def read_folder_content(folder_path):
    combined_content = ""
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_content += f.read() + "\n"  # Separate files with a newline
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
    assistant = AIAssistant(openai_client)
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

def run_req(base_folder_path: str, api_url: str, repo_id: str):

    # Token limit for LLM
    max_tokens_per_request = 10_000

    # Process each folder
    for folder_name in os.listdir(base_folder_path):
        folder_path = os.path.join(base_folder_path, folder_name)

        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_name}...")

            # Read the folder's content
            folder_content = read_folder_content(folder_path)

            # Check token count
            num_tokens = count_tokens(folder_content)
            print(f"Folder '{folder_name}' has {num_tokens} tokens.")

            # Split content if it exceeds the token limit
            if num_tokens > max_tokens_per_request:
                print(f"Splitting folder '{folder_name}' content into smaller chunks...")
                chunks = split_content_into_chunks(folder_content, max_tokens_per_request)
            else:
                chunks = [folder_content]

            # Prompt the LLM with each chunk and store responses
            responses = []
            for i, chunk in enumerate(chunks):
                print(f"Prompting LLM with chunk {i + 1}/{len(chunks)} of folder '{folder_name}'...")
                response = prompt(chunk)
                if response:
                    responses.append(response)
                    print(f"Response for chunk {i + 1} received.")
                else:
                    print(f"Failed to get response for chunk {i + 1}.")
                time.sleep(1)  # Small delay between requests to avoid hitting rate limits

            # Combine responses and generate code documentation
            combined_responses = "\n".join(responses)
            print(f"Generating code documentation for folder '{folder_name}'...")
            documentation_response = prompt(
                f"Based on the following responses from folder contents, generate a comprehensive code documentation:\n\n{combined_responses}"
            )

            if documentation_response:
                print(f"Generated code documentation for folder '{folder_name}':\n")
                print(documentation_response)

                # Send documentation to the API
                print(f"Sending code documentation for folder '{folder_name}' to the API...")
                send_to_api(api_url, documentation_response, repo_id)
            else:
                print(f"Failed to generate code documentation for folder '{folder_name}'.")


run_req("../", "http://localhost:3000/api/v1/docs/doc", "888986788")

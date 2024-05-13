#!/usr/bin/env python3

import subprocess
import re

def get_model_sha256(model_name):
    # Execute the ollama show command and capture its output
    result = subprocess.run(['ollama', 'show', model_name, '--modelfile'], capture_output=True, text=True)
    if result.returncode == 0:
        # Extract the SHA256 hash from the output
        match = re.search(r'(sha256-[a-f0-9]{64})', result.stdout)
        if match:
            return match.group(1)
    else:
        print(f"Error retrieving model info for {model_name}: {result.stderr}")
    return None

def create_symbolic_link(model_name, sha256):
    target_path = f"/usr/share/ollama/.ollama/models/blobs/{sha256}"
    link_name = model_name.replace(':', '_') + '.gguf'
    # Execute the ln command to create a symbolic link
    result = subprocess.run(['ln', '-s', target_path, link_name])
    if result.returncode == 0:
        print(f"Link created for {model_name} -> {link_name}")
    else:
        print(f"Error creating link for {model_name}")

def process_models(models_file):
    with open(models_file, 'r') as file:
        for line in file:
            model_name = line.strip().split()[0]  # Assumes model name is the first part of each line
            print(f"Processing model {model_name}.")
            sha256 = get_model_sha256(model_name)
            if sha256:
                print(f"Found hash for {model_name}: {sha256}.")
                create_symbolic_link(model_name, sha256)

if __name__ == "__main__":
    models_file = 'models.txt'  # The file where you've saved the output of `ollama list`
    process_models(models_file)

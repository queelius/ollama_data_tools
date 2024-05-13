


# i will create an `export` option, which creates two things:
#
# 1) a soft-link to the blob (normally a GGUF file). optionally can be a copy of the blob, but
#    they are large files, so soft-links are preferred.
# 2) a meta-data file, a JSON file, and typically has the same prefix as the filename.
#    it contains the following entries:
#    - 'filename': <soft-link to or copy of the model weights (e.g. GGUF) file>
#    - 'hash': <the hash of the model weights file>
#    - 'size': <the size of the model weights file>
#    - 'type': <the type of the model weight, e.g., GGUF>
#    - 'system_message': <the system message for the model>
#    - 'parameters': <the parameters of the model>
#    - 'name': <name of the model>
#    - 'template': <the model's template>
#    - 'modelfile': <path/filename of the modelfile, which resides in the same directory as the soft-link and meta-data file normally>
# 3) the modelfile, a text file, and typically and has the same prefix as the soft-link

import ollama_utils
import subprocess
import logging
import argparse
import json
import sys
import os

def export(model, name=None):
    target_path = f"/usr/share/ollama/.ollama/models/blobs/{model['hash']}"
    if name is None:
        name = model['name'].replace(':', '_')

    link_name = name + '.gguf'
    # Execute the ln command to create a symbolic link
    result = subprocess.run(['ln', '-s', target_path, link_name])
    if result.returncode != 0:
        logging.error(f"Error creating link for {model['name']}")
        return False
    
    model['file_link'] = link_name
    return model


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Export Ollama models.')
    parser.add_argument('--models', help='The model to export.', nargs='?')
    parser.add_argument('--models-file', help='The filename of the model list.', nargs='?')
    parser.add_argument("--outdir", help="The output directory.", default=".")
    # i want this to work with pipes, so i will not require a filename
    args = parser.parse_args()
    models = ollama_utils.generate_data()
    if args.models:
        models = [model for model in models if model['name'] == args.models]
    elif args.models_file:
        with open(args.models_file, 'r') as file:
            model_names = [line.strip().split()[0] for line in file]
            models = [model for model in models if model['name'] in model_names]
    else:
        model_names = [line.strip().split()[0] for line in sys.stdin]
        models = [model for model in models if model['name'] in model_names]
   
    for model in models:
        model = export(model, args.name)
        meta_file = model['file_link']
        # remove the extension if it exists
        # files can have multiple dots, so we need to be careful
        if '.' in meta_file:
            meta_file = meta_file[:meta_file.rindex('.')]
        meta_file += '.json'
        meta_file = os.path.join(args.outdir, meta_file)
        print(json.dumps(model, indent=4), file=meta_file)

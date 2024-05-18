#!/usr/bin/env python3

import os
import ollama_data as od
import subprocess
import logging
import argparse
import json
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def export_model(model, outdir, hash_length):
    """
    Exports a model to the specified output directory by creating soft links for the weights and saving the metadata.

    Args:
        model (dict): The model data.
        outdir (str): The output directory where the model will be exported.
    """
    link = os.path.join(outdir, model['name'])

    for weight in model['weights']:
        weight_link = link
        if hash_length > 0:
            weight_link += "_" + weight['hash'][:hash_length]
        result = subprocess.run(['ln', '-s', weight['file_path'], weight_link])
        if result.returncode != 0:
            logger.error(f"Error creating weight soft-link for {weight_link}")
        
        weight['soft-link'] = weight_link
        logger.debug(f"Model weight {weight['file_path']} exported to soft-link: {weight_link}")
    
    meta_link = link + '.json'
    with open(meta_link, 'w') as f:
        json.dump(model, f, indent=4)
    logger.debug(f"Model {model['name']} metadata exported to {meta_link}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Export Ollama models to a self-contained directory.')
    parser.add_argument('--models', help='Comma-separated list of models to export.', nargs='?')
    parser.add_argument("outdir", help="The output directory.", type=str)
    parser.add_argument("--cache-path", help="The cache path.", default="~/.ollama_data/cache")
    parser.add_argument("--cache-time", help="The cache time.", default='1 day')
    parser.add_argument("--debug", help="Enable debug logging.", action='store_true')
    parser.add_argument("--hash-length", help="The length of the hash to use for the weight soft-links.", default=8, type=int)
    args = parser.parse_args()

    # Set logging level to DEBUG if --debug flag is provided
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Initialize OllamaData
    ollama_data = od.OllamaData(cache_path=args.cache_path, cache_time=args.cache_time)

    # Determine model names to export
    if args.models:
        model_names = args.models.split(',')
    else:
        # Check if data is being piped into stdin
        if not sys.stdin.isatty():
            model_names = [line.strip() for line in sys.stdin]
        else:
            model_names = ollama_data.search("[*].name")

    # Check if the output directory already exists
    if os.path.exists(args.outdir):
        logger.error(f"Output directory {args.outdir} already exists.")
        sys.exit(1)

    logger.debug(f"Exporting {len(model_names)} models.")

    # Create the output directory
    os.makedirs(args.outdir)

    # Export each model
    for model_name in model_names:
        model = ollama_data.get_model(model_name)
        export_model(model, args.outdir, args.hash_length)

if __name__ == "__main__":
    main()

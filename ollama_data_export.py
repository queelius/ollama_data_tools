#!/usr/bin/env python3

import os
import ollama_data as od
import subprocess
import logging
import argparse
import json
import sys

def make_links(model, outdir):
    link_name = model['name'] + '.gguf'
    link_name.replace(' ', '_').replace(':', '_')
    link_name = os.path.join(outdir, link_name)

    print(link_name)
    return

    for weights in model['weights']:
        result = subprocess.run(['ln', '-s', model['weights']['file_path'], link_name])
        if result.returncode != 0:
            logging.error(f"Error creating link for {model['name']}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Export Ollama models to a self-contained directory.')
    parser.add_argument('--models', help='The models to export.', nargs='?')
    parser.add_argument("--outdir", help="The output directory.", default=".", type=str)
    parser.add_argument("--cache-path", help="The cache path.", default="~/.ollama_data/cache")
    parser.add_argument("--cache-time", help="The cache time.", default='1 day')

    args = parser.parse_args()

    ollama_data = od.OllamaData(cache_path=args.cache_path,
                                cache_time=args.cache_time)

    model_names = []
    if args.models:
        model_names = args.models.split(',')
    else:
        model_names = ollama_data.search("[*].name")
    
    # check for stdin
    #if not sys.stdin.isatty():
    #    model_names = [line.strip().split()[0] for line in sys.stdin] + model_names
   
    if os.path.exists(args.outdir):
        logging.error(f"Output directory {args.outdir} already exists.")
        sys.exit(1)
    
    os.makedirs(args.outdir)
    for model_name in model_names:
        model = ollama_data.get_model(model_name)
        make_links(model, args.outdir)
        with open(os.path.join(args.outdir, model_name + '.json'), 'w') as f:
            json.dump(model, f, indent=4)

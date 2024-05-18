#!/usr/bin/env python3

import re
from ollama_data_tools import ollama_data as od
import subprocess
import argparse
from typing import Dict, Any, List
import sys
import logging

def run(args: List[str]) -> str:
    """
    Runs the given subprocess with the specified arguments.

    Args:
        args (List[str]): The arguments to pass to the subprocess.

    Returns:
        str: The output from the subprocess.
    """
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(line.decode(), end='')

    process.stdout.close()
    process.wait()

    if process.returncode != 0:
        raise RuntimeError(f"Error: {process.stderr.read().decode()}")

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    script_name = sys.argv[0]
    parser = argparse.ArgumentParser(
        description='Adapts Ollama models for other engines (like `llamacpp`).',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example: " + script_name + " mistral llamacpp --engine-path /path/to/llamacpp --engine-args '--temp 0.5' '--n-gpu-layers 40' '--prompt \"[INST] You are a helpful AI assistant. [/INST]\"'")
    parser.add_argument('model', help='The model to run.', type=str, nargs='?')
    parser.add_argument('engine', help='The engine to use.', type=str, choices=['llamacpp'], default='llamacpp', nargs='?')
    parser.add_argument('--engine-path', help='The path to the engine.', type=str)
    parser.add_argument('--list-engines', help='List available engines.', action='store_true')
    parser.add_argument('--list-models', help='List available models.', action='store_true')
    parser.add_argument('--cache-path', help='The path to the cache file.', default='~/.ollama_data/cache')
    parser.add_argument('--cache-time', help='The time in seconds to keep the cache file.', type=str, default='1 day')
    parser.add_argument('--engine-args', help='Arguments to pass through to the engine.', nargs='*', default=[], type=str)
    parser.add_argument('--debug', help='Print debug information.', action='store_true')
    parser.add_argument('--show-template', help='Show the template for the model.', action='store_true')
    args = parser.parse_args()

    models = od.OllamaData(cache_path=args.cache_path, cache_time=args.cache_time)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    def _llamacpp_args(options: Dict[str, Any]) -> List[str]:
        """
        Returns the arguments compatible with the llamacpp engine.

        Args:
            options (Dict[str, Any]): The options to use.

        Returns:
            List[str]: The arguments for the llamacpp engine.
        """

        if 'engine_path' not in options:
            raise ValueError("Engine path is required.")
        
        args = [
            options['engine_path'],
            '--model',
            options['model_path'],
            '--instruct'
        ]

        if options['engine_args']:
            for arg in options['engine_args']:
                match = re.match(r'--\w+ ["\'].*["\']', arg)
                if match:
                    key, value = arg.split(' ', 1)
                    value = value.strip('\'"')
                    args.extend([key, value])
                else:
                    args.extend(arg.split())

        return args

    engines = {
        'llamacpp': _llamacpp_args
    }

    if args.list_engines:
        print("Available engines:")
        for engine in engines.keys():
            print(f"  - {engine}")
        exit(0)

    if args.list_models:
        print("Available models:")
        model_names = models.search(query='[*].name')
        for model in model_names:
            print(f"  - {model}")
        exit(0)

    if not args.model:
        print("Specify a model to run or show the template for.")
        exit(1)

    model = models.get_model(args.model)
    if not model:
        print(f"Model '{args.model}' not found.")
        exit(1)

    if args.show_template:
        print("The template for the model has the following forms:")
        for line in model['template']:
            print(f"  - {line}")
        exit(0)

    if args.engine not in engines:
        print(f"Engine '{args.engine}' not found.")
        exit(1)

    options = {
        'engine_path': args.engine_path,
        'model_path': model['weights'][0]['file_path'],
        'engine_args': args.engine_args,
    }

    try:
        run_args = engines[args.engine](options)

        logger.debug(f"Running model '{args.model}' with engine '{args.engine}' using the following engine-args:")
        for arg in run_args:
            logger.debug(" - " + arg)
        run(run_args)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()


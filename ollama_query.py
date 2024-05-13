#!/usr/bin/env python3

import logging
from time import time 
import argparse
import os
import sys
import json
from ollama_utils import get_spec, generate_data
import jmespath
import re

def get_args():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(description='Search over Ollama models.')

    parser.add_argument('--json-spec', help='Print the JSON specification.', action='store_true')

    parser.add_argument('--regex',
                        help='Regular expression to match on the top-level output.',
                        metavar='REGEX')

    parser.add_argument('--log-level', help='Set loggging level.',
                        metavar='LEVEL',
                        default=logging.INFO, type=int)
    

    parser.add_argument('query', help='The JMESPath query to filter results.', nargs='?', default='[*]')

    parser.add_argument('--cache-time',
                        help='Time in seconds to keep the cache file.',
                        metavar='SECONDS',
                        type=int, default=60 * 10)

    parser.add_argument('--exclude-keys',
                        help='Keys to exclude from the output.',
                        metavar='KEYS',
                        nargs='*')
    
    ex1 = f'''  ./{script_name} "max_by(@, &weights_size)" --exclude-keys modelfile template'''
    ex2 = f'''  ./{script_name} "[?weights_size > '4']" --exclude-keys modelfile'''
    ex3 = f'''  ./{script_name} "max_by(@, &weights_size) | [*].weights_license_type" --regex "MIT"'''
    ex4 = f'''  ./{script_name} "[3:7].[weights_size, name]"'''
    ex5 = f'''  ./{script_name} "[*]"'''

    # add a JMSEpath query example
    parser.epilog = "Examples:\n\n" + ex1 + '\n' + ex2 + '\n' + ex3 + '\n' + ex4 + '\n' + ex5

    # let's preserve newlines in the epilog
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    if args.json_spec:
        print(json.dumps(get_spec(), indent=4))
        sys.exit(0)

    cache = os.path.expanduser('~/.ollama_query_cache')
    if not os.path.exists(cache):
        logging.debug(f"{cache} file not found. Regenerating.")
        with open(cache, 'w') as file:
            models = generate_data()
            file.write(json.dumps(models))

    elapsed = time() - os.path.getmtime(cache)
    if elapsed > args.cache_time:
        logging.debug(f"{cache} is older than {args.cache_time} seconds. Regenerating.")
        models = generate_data()
        with open(cache, 'w') as file:
            file.write(json.dumps(models, indent=4))

    models = json.loads(open(cache, 'r').read())
    output = jmespath.search(args.query, models)
    if args.regex:
        regex = re.compile(args.regex)
        if isinstance(output, list):
            output = [m for m in output if regex.search(json.dumps(m, separators=(',', ':')))]
        elif isinstance(output, dict):
            output = {k: v for k, v in output.items() if regex.search(json.dumps(v, separators=(',', ':')))}
        elif not regex.search(json.dumps(output)):
                output = None

    if args.exclude_keys:
        if isinstance(output, list):
            for m in output:
                for key in args.exclude_keys:
                    m.pop(key, None)
        elif isinstance(output, dict):
            for key in args.exclude_keys:
                output.pop(key, None)
    print(json.dumps(output, indent=4))
#!/usr/bin/env python3

import logging
from time import time 
import argparse
import os
import sys
import json
import OllamaQuery as oq

def get_args():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(description='Search over Ollama models.')

    parser.add_argument('--schema',
                        help='Print the JSON schema.',
                        action='store_true')

    parser.add_argument('--regex',
                        help='Regular expression to match on the top-level of the output.',
                        metavar='REGEX')
    
    parser.add_argument('--regex-path',
                        help='The JMESPath query for the regex pattern to apply against.',
                        metavar='QUERY',
                        default='@')

    parser.add_argument('--log-level', help='Set loggging level.',
                        metavar='LEVEL',
                        default=logging.INFO, type=int)
    
    parser.add_argument('query',
                        help='The JMESPath query to filter results.',
                        nargs='?', default='[*]')

    parser.add_argument('--cache-time',
                        help='Time in seconds to keep the cache file.',
                        metavar='SECONDS',
                        type=int, default=60 * 10)

    parser.add_argument('--exclude-paths',
                        help='Paths to exclude from the output.',
                        metavar='PATH',
                        nargs='*')
    
    parser.add_argument('--olla-cache-file',
                        help='The path to the cache file.',
                        metavar='PATH',
                        default='~/.ollama_query_cache')
    
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

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)

    if args.schema:
        print(json.dumps(oq.OllamaQuery.get_schema(), indent=4))
        sys.exit(0)

    q = oq.OllamaQuery(cache_time=args.cache_time)
    output = q.search(
        query=args.query,
        regex=args.regex,
        regex_path=args.regex_path,
        exclude_paths=args.exclude_paths)

    print(json.dumps(output, indent=4))
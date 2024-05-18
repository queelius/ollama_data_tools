#!/usr/bin/env python3

import logging
import argparse
import os
import sys
import json
from ollama_data_tools import ollama_data as od

def get_args():
    """
    Parse and return command line arguments.

    :return: Parsed command line arguments.
    """
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        description='Search over Ollama models.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:

  The following JMESPath query (http://jmespath.org) shows the largest model:

    ./{script_name} "max_by(@, &total_weights_size).{{name: name, size: total_weights_size}}"

  The following example shows how to use a regex pattern to filter models:

    ./{script_name} --regex "mistral:latest" --regex-path name "[*].{{name: name, size: total_weights_size}}"

  You can also pipe a query from a file or another command:

    cat query.txt | ./{script_name}

  Using regex and regex-path with a piped query:

    echo "[*].{{info: {{ name: name, other: weights}}}}" | ./{script_name} --regex 14f2 --regex-path "info.other[*].file_name"
"""
    )

    parser.add_argument('--schema',
                        help='Print the JSON schema.',
                        action='store_true')

    parser.add_argument('--regex',
                        help='Regular expression to match.',
                        metavar='REGEX')
    
    parser.add_argument('--regex-path',
                        help='The JMESPath query for the regex pattern to apply against.',
                        metavar='QUERY',
                        default='@')

    parser.add_argument('--debug', 
                        help='Set logging level to DEBUG.',
                        action='store_true')
    
    parser.add_argument('query',
                        help='The JMESPath query to filter results.',
                        nargs='?', 
                        default=None)

    parser.add_argument('--cache-time',
                        help='Time to keep the cache file.',
                        metavar='STRING',
                        type=str, 
                        default="1 hour")

    parser.add_argument('--cache-path',
                        help='The path to the cache file.',
                        metavar='PATH',
                        default='~/.ollama_data/cache')

    return parser.parse_args()

def main():
    """
    Main function to execute the script.
    """
    args = get_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger(__name__)
    logger.debug(f"Arguments received: {args}")

    # If no query is provided as an argument, check if a query is being piped in
    query = args.query
    if not query and not sys.stdin.isatty():
        query = sys.stdin.read().strip()
        logger.debug(f"Piped query received: {query}")

    if not query and not args.schema:
        query = '[*]'

    if args.schema:
        print(json.dumps(od.OllamaData.get_schema(), indent=4))
        sys.exit(0)

    data = od.OllamaData(cache_path=args.cache_path,
                         cache_time=args.cache_time)
    output = data.search(
        query=query,
        regex=args.regex,
        regex_path=args.regex_path)

    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    main()

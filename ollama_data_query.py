#!/usr/bin/env python3

import logging
import argparse
import os
import sys
import json
import ollama_data as od

def get_args():
    """
    Parse and return command line arguments.

    :return: Parsed command line arguments.
    """
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

    parser.add_argument('--log-level', 
                        help='Set logging level.',
                        metavar='LEVEL',
                        default=logging.INFO, 
                        type=lambda x: getattr(logging, x.upper(), logging.INFO))
    
    parser.add_argument('query',
                        help='The JMESPath query to filter results.',
                        nargs='?', 
                        default='[*]')

    parser.add_argument('--cache-time',
                        help='Time to keep the cache file.',
                        metavar='STRING',
                        type=str, 
                        default="1 hour")

    parser.add_argument('--cache-path',
                        help='The path to the cache file.',
                        metavar='PATH',
                        default='~/.ollama_data/cache')
    
    ex = f'''    ./{script_name} "max_by(@, &total_weights_size).{{name: name, size: total_weights_size}}"'''
    parser.epilog = "Examples:\n\n  The following JMESPath query (http://jmespath.org) shows the largest model:\n\n" + ex
    parser.formatter_class = argparse.RawDescriptionHelpFormatter

    return parser.parse_args()

def main():
    """
    Main function to execute the script.
    """
    args = get_args()

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)

    logger.debug(f"Arguments received: {args}")

    if args.schema:
        print(json.dumps(od.OllamaData.get_schema(), indent=4))
        sys.exit(0)

    data = od.OllamaData(cache_path=args.cache_path,
                         cache_time=args.cache_time)
    output = data.search(
        query=args.query,
        regex=args.regex,
        regex_path=args.regex_path)

    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    main()

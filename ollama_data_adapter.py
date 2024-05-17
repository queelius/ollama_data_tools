import ollama_data as od
import subprocess
import argparse

def adapt_run(model_name, engine, prompt=None, options=None):
    """
    The models are from Ollama, but these models are in GGUF format. Ollama
    has information about their system messages, parameters, templates,
    etc. This function adapts the run command to use the GGUF models and
    Ollama information for other engines, like `llamacpp`.
    """

    if options is None:
        options = {
            'cache_path': '~/.ollama_data/cache',
            'cache_time': '1 hour'
        }

    ollama_data = od.OllamaData(cache_path=options["cache_path"],
                                cache_time=options["cache_time"])
        

    model = ollama_data.get_model(model_name)
    if engine not in engines:
        raise ValueError(f"Engine '{engine}' not supported.")

    engine = engines[engine]
    result = engine["run"](model, prompt, engine["path"])
    return result.stdout

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Adapts Ollama models for other engines (like `llamacpp`).')
    parser.add_argument('model', help='The model to run.', type=str, nargs='?')
    parser.add_argument('engine', help='The engine to use.', type=str, nargs='?')
    parser.add_argument('prompt', help='The prompt to use. If not specified, the model will be run interactively.', type=str, nargs='?')
    parser.add_argument("--system-message", help="The system message to use (overrides any defaults).", type=str)
    #parser.add_argument('add-engine', help='The path to the engine.', type=Dict)
    parser.add_argument("--list-engines", help="List available engines.", action="store_true")
    parser.add_argument("--list-models", help="List available models.", action="store_true")
    parser.add_argument('--cache-path', help='The path to the cache file.', default='~/.ollama_data/cache')
    parser.add_argument('--cache-time', help='The time in seconds to keep the cache file.', type=int, default=3600)
    args = parser.parse_args()

    engines = {
        'llamacpp': {
            "run" : lambda model, prompt, path: subprocess.run([path, '--model', f"{model['path']}/{model['filename']}", f"--{prompt}"], capture_output=True, text=True),
            "path": "llamagpu"
        }
    }

    print(args.model)

    if args.list_engines:
        print("Available engines:")
        for engine in engines:
            print(f"  {engine}")
        exit(0)

    data = od.OllamaData(cache_path=args.cache_path,
                            cache_time=args.cache_time)

    if args.list_models:
        print("Available models:")
        for model in data.get_models():
            print(f"  {model['name']}")
        exit(0)

    if args.engine not in engines:
        print(f"Engine '{args.engine}' not found.")
        print("Available engines:")
        for engine in engines:
            print(f"  {engine}")
        exit(1)

    if not args.model or not args.engine or not args.prompt:
        parser.print_help()
        exit(1)

    if args.model not in od.get_models():
        print(f"Model '{args.model}' not found.")
        print("Available models:")
        for model in data.get_models():
            print(f"  {model['name']}")
        exit(1)

    try:
        result = adapt_run(model_name=args.model,
                           engine=args.engine,
                           prompt=args.prompt,
                           options={'cache_path': args.cache_path, 'cache_time': args.cache_time})
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


    

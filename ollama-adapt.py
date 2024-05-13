def adapt_run(model_name, models, engine, query=None):
    """
    The models are from Ollama, but these models are in GGUF format. Ollama
    also has information about their system messages, parameters, templates,
    etc. This function adapts the run command to use the GGUF models and
    Ollama information for other engines, like `llamacpp`.
    """

    if model_name not in models:
        print(f"Error: Model '{model_name}' not found.")
        return

    model_info = models[model_name]
    if engine == 'llamacpp':
        print(f"llamacpp run --model {model_info['path']}/{model_info['filename']} --{query}")
    else:
        raise ValueError(f"Engine '{engine}' not supported.")

    return None

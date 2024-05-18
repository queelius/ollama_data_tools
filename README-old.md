# Ollama Data Toolkit

The `Ollama Data Toolkit` (https://github.com/queelius/ollama_data_kit)
is a set of command line tools, and a programming interface, that makes it
easier to work with a local Ollama installation, e.g., exporting the data
in the registry, advanced searches or views of the Ollama model registry,
and adapting the models to other inference engines like `llamacpp`.

## Requirements

- Python 3.x
- `ollama_data` module

## Installation

Clone the repository and install the necessary dependencies:

```sh
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
```

## Ollama Data Query

The `ollama_data_query.py` script allows users to search and filter Ollama models using JMESPath queries and regular expressions. This tool is designed to help users explore and retrieve specific information about the models in their Ollama registry.

### Features

- Perform JMESPath queries to filter model data.
- Use regular expressions to match specific patterns within the model data.
- Print the JSON schema of the models.
- Support for piped input queries.

### Arguments

- `query`: The JMESPath query to filter results.
- `--regex`: Regular expression to match.
- `--regex-path`: The JMESPath query for the regex pattern to apply against (default: `@`).
- `--schema`: Print the JSON schema.
- `--debug`: Set logging level to DEBUG.
- `--cache-time`: Time to keep the cache file (default: `1 hour`).
- `--cache-path`: The path to the cache file (default: `~/.ollama_data/cache`).

### Usage

To perform a JMESPath query:

```sh
./ollama_data_query.py "max_by(@, &total_weights_size).{name: name, size: total_weights_size}"
```

To use a regular expression to filter results:

```sh
./ollama_data_query.py --regex "mistral:latest" --regex-path name "[*].{name: name, size: total_weights_size}"
```

To pipe a query from a file or another command:

```sh
cat query.txt | ./ollama_data_query.py
```

Using regex and regex-path with a piped query:

```sh
echo "[*].{info: { name: name, other: weights}}" | ./ollama_data_query.py --regex 14f2 --regex-path "info.other[*].file_name"
```

### Examples

#### Query for the Largest Model

```sh
./ollama_data_query.py "max_by(@, &total_weights_size).{name: name, size: total_weights_size}"
```

#### Filter Models Using Regex

```sh
./ollama_data_query.py --regex "mistral:latest" --regex-path name "[*].{name: name, size: total_weights_size}"
```

#### Pipe a Query from a File

```sh
cat query.txt | ./ollama_data_query.py
```

#### Use Regex with a Piped Query

```sh
echo "[*].{info: { name: name, other: weights}}" | ./ollama_data_query.py --regex 14f2 --regex-path "info.other[*].file_name"
```

## Ollama Data Export

The `ollama_data_export.py` script allows users to export Ollama models to a specified directory. This tool creates soft links for the model weights and saves the model metadata in the output directory.

### Features

- Export specified models to a self-contained directory.
- Create soft links for model weights.
- Save model metadata in JSON format.
- Enable debug logging for detailed output.

### Arguments

- `outdir`: The output directory where the models will be exported.
- `--models`: Comma-separated list of models to export. If not specified, all models will be exported.
- `--cache-path`: The path to the cache file (default: `~/.ollama_data/cache`).
- `--cache-time`: The time to keep the cache file (default: `1 day`).
- `--debug`: Enable debug logging.
- `--hash-length`: The length of the hash to use for the weight soft-links (default: `8`).

### Usage

To export specified models to a directory:

```sh
./ollama_data_export.py --models model1,model2 --outdir /path/to/export
```

To export all models to a directory:

```sh
./ollama_data_export.py /path/to/export
```

### Examples

#### Export Specified Models

```sh
./ollama_data_export.py --models mistral:latest,llama3 --outdir /path/to/export
```

#### Export All Models

```sh
./ollama_data_export.py /path/to/export
```

#### Enable Debug Logging

```sh
./ollama_data_export.py --models mistral:latest --outdir /path/to/export --debug
```

#### Specify Hash Length for Soft Links

```sh
./ollama_data_export.py --models mistral:latest --outdir /path/to/export --hash-length 10
```

## Ollama Data Adapter

The `ollama_data_adapter.py` script adapts Ollama models for use with other inference engines, such as `llamacpp`. This tool is designed to reduce friction when experimenting with local LLM models and integrates with other tools for viewing, searching, and exporting Ollama models.

### Features

- List available engines and models.
- Run models with specified engines.
- Show the template for a given model.
- Pass additional arguments to the inference engine.
- Debugging information for advanced users.

### Arguments

- `model`: The model to run.
- `engine`: The engine to use.
- `--engine-path`: The path to the engine (required).
- `--list-engines`: List available engines.
- `--list-models`: List available models.
- `--cache-path`: The path to the cache file (default: `~/.ollama_data/cache`).
- `--cache-time`: The time to keep the cache file (default: `1 day`)
- `--engine-args`: Arguments to pass through to the engine.
- `--debug`: Print debug information.
- `--show-template`: Show the template for the model.


### Usage

To list all available engines:

```sh
./ollama_data_adapter.py --list-engines
```

To list all available models:

```sh
./ollama_data_adapter.py --list-models
```

To show the template for a specific model:

```sh
./ollama_data_adapter.py mistral --show-template

## The template for the model has the following forms:
## - [INST] {{ .System }} {{ .Prompt }} [/INST]
```

To run a specific model with an engine:

```sh
./ollama_data_adapter.py <model> <engine> --engine-path <path-to-engine> --engine-args '<additional-arguments>'
```

## Example

To use the `llamacpp` inference engine with the `mistral` model (assuming
it is available in your `Ollama` registry), you might use the following
arguments:

```sh
./ollama_data_adapter.py
    mistral                          # Also matches `mistral:latest`
    llamacpp                         # Use the llamacpp engine
    --engine-path /path/to/llamacpp  # Path to engine, e.g. ~/llamacpp/main
    --engine-args                    # Pass these arguments into the engine 
        '--n-gpu-layers 40'
        '--prompt "[INST] You are a helpful AI assistant. [/INST]"'
```

The `--prompt` engine pass-through argument follows the template shown by
the `./ollama_data_adapter.py mistral --show-template`.

We place a lot of burden on the end-user to get the formatting right. These
models are very sensitive to how you prompt them, so some experimentation
may be necessary.

You may also want to use `./ollama_data_query.py` to show the system message
or other properties of a model, so that you can further customize the
pass-through arguments to better fit its training data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

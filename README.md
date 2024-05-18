# Ollama Data Tools

## Requirements

- Python 3.x

## Installation

Clone the repository and install the necessary dependencies:

```sh
git clone https://github.com/queelius/ollama_data_tools.git
cd ollama_data_tools
pip install -r requirements.txt
```

## Ollama Data Toolkit

The `OllamaData` class is the core module of the Ollama Data Toolkit, allowing users to work programmatically with Ollama model data. This class provides methods to access, search, and filter model information.

### Features

- Retrieve the schema of the OllamaData object.
- Access models by name or index.
- List all available models.
- Perform JMESPath queries and apply regex filters on the model data.
- Cache model data for efficient repeated access.

### Class Methods

#### `OllamaData.get_schema() -> Dict[str, Any]`
Returns the schema of the `OllamaData` object.

#### `OllamaData.__init__(cache_path: str = '~/.ollama_data/cache', cache_time: str = '1 day')`
Initializes the `OllamaData` object.

- `cache_path`: The path to the cache file.
- `cache_time`: The duration the cache is valid.

#### `OllamaData.__len__() -> int`
Returns the number of models.

#### `OllamaData.__getitem__(index: int) -> Dict[str, Any]`
Gets a model by index.

- `index`: The index of the model.

#### `OllamaData.get_model(name: str) -> Dict[str, Any]`
Gets the model by name. Returns the most specific model that starts with the given name.

- `name`: The name of the model.

#### `OllamaData.get_models() -> Dict[str, Any]`
Gets the models. Caches the model data to avoid repeated regeneration.

#### `OllamaData.search(query: str = '[*]', regex: Optional[str] = None, regex_path: str = '@') -> Dict[str, Any]`
Queries, searches, and views the models using a JMESPath query, regex filter, and exclude keys.

- `query`: The JMESPath query to filter and provide a view of the models.
- `regex`: The regex pattern to match against the output.
- `regex_path`: The JMESPath query for the regex pattern.

### Usage Example

Here is an example of how to use the `OllamaData` class programmatically:

```python
import ollama_data as od

# Initialize the OllamaData object
models = od.OllamaData(cache_path='~/.ollama_data/cache', cache_time='1 day')

# Get the schema of the OllamaData object
print("Schema:", models.get_schema())

# List all models
print("Models:", ollama_data.get_models())

# Get a specific model by name
model = models.get_model('mistral')
print("Specific Model:", model['name'])

# Search models using a JMESPath query
query_result = models.search(query="[*].{name: name, size: total_weights_size}")
print("Query Result:", query_result)

# Search models using a JMESPath query and regex filter
query_regex_result = models.search(
    query="[*].{name: name, size: total_weights_size}",
    regex="mistral", regex_path="name")
print("Query Regex Result:", query_regex_result)
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
ollama_data_query "max_by(@, &total_weights_size).{name: name, size: total_weights_size}"
```

To use a regular expression to filter results:

```sh
ollama_data_query --regex "mistral:latest" --regex-path name "[*].{name: name, size: total_weights_size}"
```

To pipe a query from a file or another command:

```sh
cat query.txt | ollama_data_query
```

Using regex and regex-path with a piped query:

```sh
echo "[*].{info: { name: name, other: weights}}" | ollama_data_query --regex 14f2 --regex-path "info.other[*].file_name"
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
./ollama_data_export.py --models mistral,llama3 --outdir /path/to/export
```

#### Export All Models

```sh
./ollama_data_export.py /path/to/export --ourdir /path/to/export
```

#### Enable Debug Logging

```sh
./ollama_data_export.py --models mistral --outdir /path/to/export --debug
```

#### Specify Hash Length for Soft Links

```sh
./ollama_data_export.py --models mistral:latest --outdir /path/to/export --hash-length 2
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
- `--cache-time`: The time to keep the cache file (default: `1 day`).
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

### Example

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

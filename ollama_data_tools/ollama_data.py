import jmespath
from ollama_data_tools import ollama_data_utils as odu
from ollama_data_tools import regex_path_matcher
from typing import List, Dict, Any, Optional
from ollama_data_tools import json_cache as cm

class OllamaData:
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Returns the schema of the `OllamaData` object.

        :return: An object representing the schema.
        """
        return odu.get_schema()

    def __init__(self,
                 cache_path: str = '~/.ollama_data/cache',
                 cache_time: str = '1 day'):
        """
        Initialize the OllamaData object.

        :param cache_path: The path to the cache file.
        :param cache_time: The duration the cache is valid.
        """

        self.cache = cm.JsonCache(cache_path, cache_time)

    def __len__(self) -> int:
        """
        Get the number of models.

        :return: The number of models.
        """
        return len(self.get_models())

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """
        Get a model by index.

        :param index: The index of the model.
        :return: A dictionary representing the model.
        """
        models = self.get_models()
        if index < 0 or index >= len(models):
            raise IndexError("Index out of range")
        return models[index]

    def get_model(self, name: str) -> Dict[str, Any]:
        """
        Get the model by name (starts with the name and returns
        the most specific model). The total order is given by:

        1. The model with the shortest name that starts with the given name.
        2. If there are multiple models with the same length, we return the first one.
        3. If a model is named `<model_name>:latest`, we compute its length
           without the `:latest` suffix unless `name` is `<model_name>:latest`.

        :param name: The name of the model.
        :return: A dictionary representing the model.
        """
        
        models = [m for m in self.get_models() if m['name'].startswith(name)]
        if not models:
            raise ValueError(f"No model with name '{name}' found")
        
        def _len(m):
            if 'name' not in m:
                return int(1e9)
            l = len(m['name'])
            if m['name'].endswith(':latest'):
                l -= len(':latest')
            return l
        return min(models, key=_len)     


    def get_models(self) -> Dict[str, Any]:
        """
        Get the models. We either have it in memory and it has not expired,
        or it has expired or it is not already in memory and we regenerate the
        model data.

        :return: A dictionary representing the models. See `get_schema` for the schema.
        """
        if not self.cache.is_valid():
            self.cache.save(odu.get_models())

        return self.cache.load()

    def search(self,
               query: str = '[*]',
               regex: Optional[str] = None,
               regex_path: str = '@') -> Dict[str, Any]:
        """
        Query/search/view the models using a JMESPath query, regex filter, and
        exclude keys.

        :param query: The JMESPath query to filter and provide a view of the models.
        :param regex: The regex pattern to match against the output.
        :param regex_path: The JMESPath query for the regex pattern. See
                           `utils.regex_path_matcher` for more information.
        :return: JSON (dict) object representing some view of the models.
        """
        output = jmespath.search(query, self.get_models())
        if regex:
            output = regex_path_matcher.regex_path_matcher(output, regex, regex_path)
        return output

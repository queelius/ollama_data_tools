import os, json, jmespath, ollama_utils, utils
from time import time

class OllamaQuery:
    @staticmethod
    def get_schema():
        """
        Returns the schema of the OllamaQuery object.
        """
        return ollama_utils.get_schema()

    def __init__(self, cache_path='~/.ollama_query_cache', cache_time=3600):
        """
        Initialize the OllamaQuery object.

        :param cache_path: The path to the cache file.
        :param cache_time: The time in seconds to keep the cache file.
        """
        self.cache_path = os.path.expanduser(cache_path)
        self.cache_time = cache_time
        self.models = self.load_or_generate_data()

    def load_or_generate_data(self):
        if not os.path.exists(self.cache_path):
            return self.generate_and_cache_data()

        elapsed = time() - os.path.getmtime(self.cache_path)
        if elapsed > self.cache_time:
            return self.generate_and_cache_data()

        with open(self.cache_path, 'r') as file:
            return json.load(file)

    def generate_and_cache_data(self):
        models = ollama_utils.generate_data()
        with open(self.cache_path, 'w') as file:
            json.dump(models, file, indent=4)
        return models

    def search(self,
               query='[*]',
               regex=None,
               regex_path='@',
               exclude_paths=[]):
        """
        Query/search/view the models using a JMESPath query, regex filter, and
        exclude keys.

        :param query: The JMESPath query to filter and provide a view of the models.
        :param regex: The regex pattern to match against the output.
        :param regex_path: The JMESPath query for the regex pattern. See
                           `utils.regex_path_matcher` for more information.
        :param exclude_paths: The paths to exclude from the output.
    
        :return: JSON (dict) object representing some view of the models.
        """
        output = jmespath.search(query, self.models)
        if regex:
            output = utils.regex_path_matcher(output, regex, regex_path)

        if exclude_paths:
            output = utils.filter_paths(output, exclude_paths)

        return output
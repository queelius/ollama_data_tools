import os, json, jmespath, ollama_utils, utils
from time import time

class OllamaQuery:
    @staticmethod
    def get_schema():
        """
        Returns the schema of the OllamaQuery object.
        """
        return ollama_utils.get_spec()

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
               regex_query='@',
               exclude_paths=[]):
        """
        Query/search/view the models using a JMESPath query, regex filter, and
        exclude keys.

        :param query: The JMESPath query to filter and provide a view of the models.
        :param regex: The regex pattern to filter the output.
        :param regex_query: The JMESPath query for the regex pattern. See
                            `utils.regex_filter` for more information.
        :param exclude_paths: The paths to exclude from the output.
    
        :return: JSON (dict) object representing some view of the models.
        """
        output = jmespath.search(query, self.models)
        if regex:
            output = utils.regex_filter(output, regex, regex_query)

        if exclude_paths:
            output = utils.filter_paths(output, exclude_paths)

        return output

    # @staticmethod
    # def regex_filter_old(output, regex):
    #     """
    #     Filter JSON output using a regex pattern.
    #     """
    #     if isinstance(output, list):
    #         return [m for m in output if regex.search(json.dumps(m, separators=(',', ':')))]
    #     elif isinstance(output, dict):
    #         return {k: v for k, v in output.items() if regex.search(json.dumps(v, separators=(',', ':')))}
    #     elif not regex.search(json.dumps(output)):
    #         return None
    #     return output

        #  if exclude_paths:
        #     if isinstance(output, list):
        #         for o in output:
        #             for key in exclude_keys:
        #                 o.pop(key, None)
        #     elif isinstance(output, dict):
                
        #         for key in exclude_keys:
        #             output.pop(key, None)

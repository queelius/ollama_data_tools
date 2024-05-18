from setuptools import setup, find_packages

setup(
    name='ollama_data_tools',
    version='0.1.0',
    description='Tools for working with Ollama model data',
    author='Alex Towell',
    author_email='lex@metafunctor.com',
    url='https://github.com/queelius/ollama_data_tools',
    packages=find_packages(),
    install_requires=[
        'ollama_data',
        # other dependencies...
    ],
    entry_points={
        'console_scripts': [
            'ollama_data_export=ollama_data_tools.ollama_data_export:main',
            'ollama_data_adapter=ollama_data_tools.ollama_data_adapter:main',
            'ollama_data_query=ollama_data_tools.ollama_data_query:main',
            # other scripts...
        ],
    },
)

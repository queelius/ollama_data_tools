from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='ollama_data_tools',
    version='0.1.1',
    description='Tools for working with Ollama model data',
    author='Alex Towell',
    author_email='lex@metafunctor.com',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/queelius/ollama_data_tools',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
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

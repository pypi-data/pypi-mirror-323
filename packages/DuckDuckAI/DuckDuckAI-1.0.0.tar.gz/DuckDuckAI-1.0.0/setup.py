
#### `setup.py`

from setuptools import setup, find_packages

setup(
    name="DuckDuckAI",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    description="A Python package for interacting with DuckDuckGo's AI models.",
    author="Ramona-Flower",
    url="https://github.com/ramona-flower/DuckDuckAI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

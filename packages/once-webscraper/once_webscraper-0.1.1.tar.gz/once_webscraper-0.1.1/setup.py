from setuptools import setup, find_packages

setup(
    name="once-webscraper",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4>=4.9.3',
        'requests>=2.25.1',
        'lxml>=4.9.0',
        'urllib3>=1.26.0',
        'certifi>=2021.10.8',
        'charset-normalizer>=2.0.0',
        'idna>=3.3',
        'soupsieve>=2.3.1',
    ],
    author="Nyronous",
    description="Uma biblioteca simples para web scraping de fornecedores",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nyronous/once-webscraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 
from setuptools import setup, find_packages

setup(
    name="webscraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "requests>=2.25.0"
    ],
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Biblioteca de scraping para fornecedores",
    python_requires=">=3.7",
) 
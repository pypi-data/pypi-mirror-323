from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webscraper-once",
    version="0.2.2",
    author="Nyronous",
    author_email="seu.email@exemplo.com",
    description="Extrai dados de produtos de qualquer site",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/webscraper",
    packages=find_packages(),
    package_data={'': ['*.py']},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.9.0",
    ],
    keywords="web scraping, produtos",
) 
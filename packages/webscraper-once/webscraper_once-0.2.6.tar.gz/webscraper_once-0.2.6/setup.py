from setuptools import setup, find_packages

setup(
    name="webscraper-once",
    version="0.2.6",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.9.0",
    ]
) 
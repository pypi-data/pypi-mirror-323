from setuptools import setup, find_packages


setup(
    name="gnparser",
    version="0.1.1",
    description="Python wrapper for the gnparser Go library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pieter Provoost",
    author_email="pieterprovoost@gmail.com",
    url="https://github.com/pieterprovoost/gnparser-python",
    packages=find_packages(),
    package_data={
        "gnparser": [
            "libgnparser.dylib",
            "libgnparser.so"
        ]
    },
    python_requires=">=3.6"
)

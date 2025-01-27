from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="stringpairfinder",
    version="2.0.0",
    description="Package designed to match strings by similarity",
    author="Antoine PINTO",
    author_email="antoine.pinto1@outlook.fr",
    license="MIT",
    license_file="LICENSE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AntoinePinto/stringpairfinder",
    project_urls={
        "Source Code": "https://github.com/AntoinePinto/stringpairfinder",
    },
    keywords=["string", "string matching", "algorithm", "similarity"],
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.6"
    ],
    python_requires=">=3.7"
)

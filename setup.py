from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Function to parse requirements.txt
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(path.join(here, filename), encoding="utf-8") as f:
        lineiter = (line.strip() for line in f)
        return [line for line in lineiter if line and not line.startswith("#")]

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get requirements from requirements.txt
install_reqs = parse_requirements("requirements.txt")

setup(
    name="blog-vi",
    version="1.0.0",
    description="Simple blog with search and comments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LikaloLLC/BlogVi",
    author="Likalo Limited",
    author_email="hello@docsie.io",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="blog-vi(勝利)",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.5, <4",
    install_requires=install_reqs,
    entry_points={
        "console_scripts": [
            "blogvi=blog_vi._cli:_cli"
        ]
    },
)

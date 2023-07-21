from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="blog-vi",
    version="0.2.5",
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
    install_requires=[
        "Markdown>=3.0.0,<3.2.2",
        "click>=7.0,<8.0",
        "watchdog>=1.0.0,<2.0.0",
        "requests>=2.0.0,<2.22.0",
        "Jinja2>=2.0.0,<2.22.0",
        "jinja_markdown>=1.200000,<=1.200630",
        "feedgen>=0.6.0,<1.0.0",
        "python-slugify>=4.0.0,<4.0.1",
        "PyYAML>=5.0.0,<5.3.1",
        "deepl>=1.0.1,<2",
        "MarkupSafe==2.0.1"
    ],
    entry_points={
        "console_scripts": [
            "blogvi=blog_vi._cli:_cli"
        ]
    },
)

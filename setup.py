from setuptools import setup
from pathlib import Path

# Read the README file for long description
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="collect_code",
    version="1.0.0",  
    description="A CLI tool to collect source code from multiple directories into a single file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mikhail Onyanov",
    author_email="mihacool3@gmail.com",
    url="https://github.com/MikhailOnyanov/code_collecter",
    py_modules=["collect_code"],
    entry_points={
        "console_scripts": [
            "collect-code=collect_code:main",
        ],
    },
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="code-collection, cli, python, ai-assistant, code-analysis",
    project_urls={
        "Bug Reports": "https://github.com/MikhailOnyanov/code_collecter/issues",
        "Source": "https://github.com/MikhailOnyanov/code_collecter",
    },
)

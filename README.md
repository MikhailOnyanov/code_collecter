# Code collecter 

![code_collecter_logo](/assets/code_collecter_logo.png)

A script to collect source code from multiple directories into a single text file. Perfect for code analysis, sharing projects with AI chatbots, archiving, or creating context for refactoring!

## Features ✨

- Collects **Python, Java, C, and C++** files by default (option to include **all files** 🌐)
- Ignores common directories: `.idea`, `.venv`, `venv`, `__pycache__`, `.env` 🚫
- Add custom directories to exclude with `--exclude` 🛑
- Exclude specific file types/extensions with `--exclude-langs` 🚷
- Supports multiple input folders 🗂️
- Preserves file structure with relative paths 🧭
- Resilient to file read errors — continues even if some files fail 🔒
- User-friendly CLI with full argument support 🖥️

## Installation 🛠️

1. Make sure you have **Python 3.7+** installed 🐍
2. Clone this repo or copy the files

### Prefered: Install with pipx – CLI tools 🧰

```bash
pipx install .
```

> 💡 `pipx` ensures isolated, system-wide access to the CLI tool without polluting your global Python environment.

### Install with uv (recommended for .venv) ⚡

```bash
uv pip install .
```

### Install with pip

```bash
pip install .
```

After installation, use the `collect-code` command from anywhere! 🚀

## Usage 🚀

### Collect code files from one folder (Python, Java, C, C++ by default):

```bash
collect-code ./src
```

### Collect from multiple folders:

```bash
collect-code ./src ./tests ./utils
```

### Collect **all files** (not just default languages):

```bash
collect-code ./project --all-files
```

### Exclude additional directories:

```bash
collect-code ./src --exclude node_modules build dist
```

### Exclude specific file types/extensions:

```bash
# Exclude Python files
collect-code ./src --exclude-langs=py

# Exclude multiple file types (Java and C++)
collect-code ./src --exclude-langs=java,cpp,hpp

# Works with or without dots in extension names
collect-code ./src --exclude-langs=.py,.java
```

### Combine directory and file-type exclusions:

```bash
# Exclude 'build' directory and all Java files
collect-code ./src --exclude build --exclude-langs=java

# Exclude multiple directories and file types
collect-code ./project --exclude node_modules dist --exclude-langs=cpp,h
```

### Example Output 📄

The generated `collected_code.txt` will look like:

```
[project/src/main.py]
def hello():
    print("Hello, world!")

[project/src/utils/helper.py]
class Helper:
    def __init__(self):
        pass

...
```

## Output File 📂

Results are saved to `collected_code.txt` in your current working directory.

## Technical Details ⚙️

- **Language**: Python 3.7+
- **Dependencies**: Standard library only 🚫📦
- **License**: MIT 📜
- **Files**: `collect_code.py`, `setup.py`
- **Supported Languages by Default**: Python (`.py`), Java (`.java`), C (`.c`, `.h`), C++ (`.cpp`, `.cc`, `.cxx`, `.hpp`)

### Understanding the Flags

- **`--exclude`**: Excludes **directories** from being traversed (e.g., `node_modules`, `build`)
- **`--exclude-langs`**: Excludes **file types** based on their extensions (e.g., `py`, `java`)
- **`--all-files`**: Overrides default language filtering and collects all file types (but still respects `--exclude-langs`)

## Development 🛠️

### Setup Development Environment

Install with uv:

```bash
uv pip install -e .
```

Run directly without installation:

```bash
python collect_code.py ./src --all-files
```

### Running Tests 🧪

Run the test suite:

```bash
python -m unittest test_collect_code -v
```

Or with pytest (if installed):

```bash
pytest test_collect_code.py -v
```

### Code Quality

Format code with ruff:

```bash
uv tool run ruff format collect_code.py test_collect_code.py
```

Lint code:

```bash
uv tool run ruff check collect_code.py test_collect_code.py
```

The test suite includes:
- **Unit tests** for the `collect_files` function with detailed docstrings
- **Unit tests** for CLI argument parsing
- **Integration tests** for end-to-end scenarios
- **Test fixtures** to reduce code duplication

All tests run automatically on every push via GitHub Actions CI/CD pipeline.

## Author 👨‍💻
@MikhailOnyanov

Created to simplify code sharing with AI chat interfaces and streamline project analysis. 💬 


#!/usr/bin/env python3

import argparse
import logging
import os
from pathlib import Path

# Configure logging with ISO 8601 datetime format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger(__name__)

DEFAULT_EXCLUDE_DIRS = {".idea", ".venv", "venv", "__pycache__", ".env"}
DEFAULT_EXTENSIONS = {".py", ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"}


def collect_files(
    folder_path: Path,
    exclude_files: set,
    exclude_dirs: set,
    all_files: bool,
    include_extensions: set,
    exclude_extensions: set,
) -> str:
    """Collects content of files from a directory and its subdirectories.

    By default, collects files with extensions in `include_extensions` (Python, Java, C, C++).
    If `all_files` is True, collects all files. Files with extensions in `exclude_extensions`
    are always skipped. Skips files in `exclude_dirs` and files listed in `exclude_files`.
    Handles read errors gracefully by inserting an error message instead of crashing.

    Args:
        folder_path (Path): Root directory to start collecting files from.
        exclude_files (set): Set of Path objects representing files to exclude.
        exclude_dirs (set): Set of directory names to skip during traversal.
        all_files (bool): If True, include all files; if False, only files with included extensions.
        include_extensions (set): Set of file extensions to include (e.g., {'.py', '.java'}).
        exclude_extensions (set): Set of file extensions to exclude (takes precedence).

    Returns:
        str: Concatenated string with each file's content prefixed by its relative path
             in format: "[folder_name/relative/path/to/file.py]\n<content>\n\n"
    """
    output_parts = []
    for root, dirs, files in os.walk(folder_path):
        # Filter out excluded directories in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = Path(root) / file
            file_ext = file_path.suffix.lower()

            # Skip files with excluded extensions (takes precedence)
            if file_ext in exclude_extensions:
                continue

            # Skip files not matching included extensions unless all_files is True
            if not all_files and file_ext not in include_extensions:
                continue

            # Skip explicitly excluded files
            if file_path in exclude_files:
                continue

            # Compute relative path from the root folder
            rel_path = file_path.relative_to(folder_path)
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"Failed to read file {file_path}: {e}")
                content = f"<<Error reading file: {e}>>"

            output_parts.append(f"[{folder_path.name}/{rel_path}]\n{content}\n\n")

    return "".join(output_parts)


def main():
    """Main entry point for the collect-code CLI tool.

    Parses command-line arguments and collects code from one or more directories.
    Outputs a single file 'collected_code.txt' in the current working directory.
    Excludes the script itself and common system directories by default.
    """
    parser = argparse.ArgumentParser(
        description="Collect code from multiple directories (Python, Java, C, C++ by default; all files with --all-files)"
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more directory paths to collect code from (space-separated)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Directory names to exclude (beyond default: .idea, .venv, venv, __pycache__, .env)",
    )
    parser.add_argument(
        "--exclude-langs",
        type=str,
        default="",
        help="Comma-separated file extensions to exclude (e.g., 'py,java' or '.py,.java')",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include all files (not just default language files) in the output",
    )

    args = parser.parse_args()

    # Exclude the script itself and any output file that might exist
    current_script = Path(__file__).resolve()
    exclude_files = {current_script}

    # Combine default and user-provided excluded directories
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.union(set(args.exclude))

    # Parse excluded language extensions
    exclude_extensions = set()
    if args.exclude_langs:
        # Split by comma and normalize extensions (add leading dot if missing)
        raw_extensions = [ext.strip() for ext in args.exclude_langs.split(",")]
        exclude_extensions = {
            ext if ext.startswith(".") else f".{ext}" for ext in raw_extensions if ext.strip()
        }

    # Define output file path
    output_file = Path(os.getcwd()) / "collected_code.txt"
    output_content = []

    logger.info(f"Starting code collection from {len(args.folders)} directories...")
    logger.debug(f"Excluded directories: {exclude_dirs}")
    logger.debug(f"Excluded files: {exclude_files}")
    logger.debug(f"Excluded extensions: {exclude_extensions}")
    logger.debug(f"Collecting all files: {args.all_files}")

    # Process each provided folder
    for folder in args.folders:
        folder_path = Path(folder).resolve()
        if not folder_path.is_dir():
            logger.error(f"Error: {folder_path} is not a directory, skipping.")
            continue

        logger.info(f"Processing directory: {folder_path}")
        output_content.append(
            collect_files(
                folder_path,
                exclude_files,
                exclude_dirs,
                args.all_files,
                DEFAULT_EXTENSIONS,
                exclude_extensions,
            )
        )

    # Write all collected content to output file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(output_content))
        logger.info(f"Successfully created output file: {output_file}")
    except Exception as e:
        logger.error(f"Failed to write output file {output_file}: {e}")
        raise


if __name__ == "__main__":
    main()

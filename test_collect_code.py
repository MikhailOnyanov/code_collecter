"""
Unit and integration tests for collect_code.py
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Import the module to test
import collect_code


class TestCollectFiles(unittest.TestCase):
    """Unit tests for the collect_files function"""

    def setUp(self):
        """Create a temporary directory structure for testing"""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        
        # Create test files
        (self.test_path / "test.py").write_text("print('Python')")
        (self.test_path / "Test.java").write_text("class Test {}")
        (self.test_path / "program.c").write_text("int main() {}")
        (self.test_path / "program.cpp").write_text("int main() {}")
        (self.test_path / "header.h").write_text("#define TEST")
        (self.test_path / "header.hpp").write_text("#define TEST")
        (self.test_path / "readme.txt").write_text("readme")
        (self.test_path / "readme.md").write_text("# readme")
        
        # Create subdirectory
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "sub.py").write_text("# subdir python")
        
        # Create excluded directory
        excluded = self.test_path / "build"
        excluded.mkdir()
        (excluded / "output.o").write_text("binary")

    def tearDown(self):
        """Clean up temporary directory"""
        self.test_dir.cleanup()

    def test_collect_default_languages(self):
        """Test that default languages (py, java, c, cpp) are collected"""
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Should include Python, Java, C, C++, headers
        self.assertIn("test.py", result)
        self.assertIn("Test.java", result)
        self.assertIn("program.c", result)
        self.assertIn("program.cpp", result)
        self.assertIn("header.h", result)
        self.assertIn("header.hpp", result)
        self.assertIn("sub.py", result)
        
        # Should not include txt or md files
        self.assertNotIn("readme.txt", result)
        self.assertNotIn("readme.md", result)

    def test_collect_all_files(self):
        """Test that all_files=True collects all file types"""
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Should include all files
        self.assertIn("test.py", result)
        self.assertIn("readme.txt", result)
        self.assertIn("readme.md", result)

    def test_exclude_extensions(self):
        """Test that exclude_extensions filters out specified file types"""
        exclude_ext = {".py", ".java"}
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=exclude_ext
        )
        
        # Should not include Python or Java
        self.assertNotIn("test.py", result)
        self.assertNotIn("Test.java", result)
        self.assertNotIn("sub.py", result)
        
        # Should include C and C++
        self.assertIn("program.c", result)
        self.assertIn("program.cpp", result)

    def test_exclude_directories(self):
        """Test that exclude_dirs skips specified directories"""
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs={"build"},
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Should not include files from build directory
        self.assertNotIn("output.o", result)

    def test_exclude_specific_files(self):
        """Test that exclude_files skips specific file paths"""
        test_py_path = self.test_path / "test.py"
        result = collect_code.collect_files(
            self.test_path,
            exclude_files={test_py_path},
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Should not include the excluded file
        self.assertNotIn("print('Python')", result)
        
        # Should include other Python files
        self.assertIn("sub.py", result)

    def test_exclude_extensions_precedence(self):
        """Test that exclude_extensions takes precedence over all_files"""
        exclude_ext = {".txt"}
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=True,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=exclude_ext
        )
        
        # Should not include txt even with all_files=True
        self.assertNotIn("readme.txt", result)
        
        # Should include other files
        self.assertIn("test.py", result)
        self.assertIn("readme.md", result)

    def test_file_content_format(self):
        """Test that output format includes correct headers and content"""
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs={"build", "subdir"},
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Check for proper formatting
        self.assertIn(f"[{self.test_path.name}/test.py]", result)
        self.assertIn("print('Python')", result)

    def test_case_insensitive_extensions(self):
        """Test that file extension matching is case-insensitive"""
        # Create files with uppercase extensions
        (self.test_path / "Test.PY").write_text("uppercase py")
        (self.test_path / "Test.JAVA").write_text("uppercase java")
        
        result = collect_code.collect_files(
            self.test_path,
            exclude_files=set(),
            exclude_dirs=set(),
            all_files=False,
            include_extensions=collect_code.DEFAULT_EXTENSIONS,
            exclude_extensions=set()
        )
        
        # Should handle case-insensitive matching
        self.assertIn("uppercase py", result)
        self.assertIn("uppercase java", result)


class TestArgumentParsing(unittest.TestCase):
    """Unit tests for CLI argument parsing"""

    def test_exclude_langs_parsing_without_dots(self):
        """Test parsing --exclude-langs with extensions without dots"""
        with patch('sys.argv', ['collect_code.py', 'test', '--exclude-langs=py,java']):
            with patch('collect_code.Path.is_dir', return_value=True):
                with patch('collect_code.collect_files', return_value=""):
                    with patch('builtins.open', unittest.mock.mock_open()):
                        # Capture the parsed exclude_extensions
                        original_collect = collect_code.collect_files
                        captured_args = {}
                        
                        def capture_collect(*args, **kwargs):
                            captured_args['exclude_extensions'] = args[5] if len(args) > 5 else kwargs.get('exclude_extensions')
                            return ""
                        
                        with patch('collect_code.collect_files', side_effect=capture_collect):
                            collect_code.main()
                        
                        self.assertEqual(captured_args['exclude_extensions'], {'.py', '.java'})

    def test_exclude_langs_parsing_with_dots(self):
        """Test parsing --exclude-langs with extensions with dots"""
        with patch('sys.argv', ['collect_code.py', 'test', '--exclude-langs=.cpp,.h']):
            with patch('collect_code.Path.is_dir', return_value=True):
                with patch('collect_code.collect_files', return_value=""):
                    with patch('builtins.open', unittest.mock.mock_open()):
                        captured_args = {}
                        
                        def capture_collect(*args, **kwargs):
                            captured_args['exclude_extensions'] = args[5] if len(args) > 5 else kwargs.get('exclude_extensions')
                            return ""
                        
                        with patch('collect_code.collect_files', side_effect=capture_collect):
                            collect_code.main()
                        
                        self.assertEqual(captured_args['exclude_extensions'], {'.cpp', '.h'})

    def test_exclude_langs_with_whitespace(self):
        """Test that whitespace in --exclude-langs is handled correctly"""
        with patch('sys.argv', ['collect_code.py', 'test', '--exclude-langs=py,  , java  ']):
            with patch('collect_code.Path.is_dir', return_value=True):
                with patch('collect_code.collect_files', return_value=""):
                    with patch('builtins.open', unittest.mock.mock_open()):
                        captured_args = {}
                        
                        def capture_collect(*args, **kwargs):
                            captured_args['exclude_extensions'] = args[5] if len(args) > 5 else kwargs.get('exclude_extensions')
                            return ""
                        
                        with patch('collect_code.collect_files', side_effect=capture_collect):
                            collect_code.main()
                        
                        # Should filter out empty/whitespace entries
                        self.assertEqual(captured_args['exclude_extensions'], {'.py', '.java'})


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end scenarios"""

    def setUp(self):
        """Create a temporary directory structure for integration testing"""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        self.output_file = self.test_path / "collected_code.txt"
        
        # Create a realistic project structure
        src_dir = self.test_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("def main():\n    pass")
        (src_dir / "App.java").write_text("public class App {}")
        (src_dir / "util.c").write_text("int util() { return 0; }")
        (src_dir / "util.h").write_text("#ifndef UTIL_H\n#define UTIL_H\n#endif")
        
        tests_dir = self.test_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test():\n    pass")
        
        build_dir = self.test_path / "build"
        build_dir.mkdir()
        (build_dir / "output.o").write_text("binary")

    def tearDown(self):
        """Clean up temporary directory"""
        self.test_dir.cleanup()

    def test_default_collection(self):
        """Test default collection of multiple directories"""
        src_dir = str(self.test_path / "src")
        tests_dir = str(self.test_path / "tests")
        
        with patch('sys.argv', ['collect_code.py', src_dir, tests_dir]):
            with patch('os.getcwd', return_value=str(self.test_path)):
                collect_code.main()
        
        # Check output file exists
        self.assertTrue(self.output_file.exists())
        
        # Check content
        content = self.output_file.read_text()
        self.assertIn("main.py", content)
        self.assertIn("App.java", content)
        self.assertIn("util.c", content)
        self.assertIn("util.h", content)
        self.assertIn("test_main.py", content)

    def test_exclude_langs_integration(self):
        """Test --exclude-langs in real scenario"""
        src_dir = str(self.test_path / "src")
        
        with patch('sys.argv', ['collect_code.py', src_dir, '--exclude-langs=java,h']):
            with patch('os.getcwd', return_value=str(self.test_path)):
                collect_code.main()
        
        content = self.output_file.read_text()
        self.assertIn("main.py", content)
        self.assertIn("util.c", content)
        self.assertNotIn("App.java", content)
        self.assertNotIn("util.h", content)

    def test_exclude_directory_integration(self):
        """Test --exclude for directories"""
        with patch('sys.argv', ['collect_code.py', str(self.test_path), '--exclude', 'build', 'tests']):
            with patch('os.getcwd', return_value=str(self.test_path)):
                collect_code.main()
        
        content = self.output_file.read_text()
        # Should include src files
        self.assertIn("main.py", content)
        # Should not include test or build files
        self.assertNotIn("test_main.py", content)
        self.assertNotIn("output.o", content)

    def test_combined_exclusions(self):
        """Test combining --exclude and --exclude-langs"""
        with patch('sys.argv', ['collect_code.py', str(self.test_path), 
                                '--exclude', 'build', '--exclude-langs=py']):
            with patch('os.getcwd', return_value=str(self.test_path)):
                collect_code.main()
        
        content = self.output_file.read_text()
        # Should include Java and C
        self.assertIn("App.java", content)
        self.assertIn("util.c", content)
        # Should not include Python
        self.assertNotIn("main.py", content)
        self.assertNotIn("test_main.py", content)

    def test_all_files_with_exclusion(self):
        """Test --all-files with --exclude-langs"""
        # Add a non-code file
        (self.test_path / "src" / "README.md").write_text("# README")
        
        with patch('sys.argv', ['collect_code.py', str(self.test_path / "src"), 
                                '--all-files', '--exclude-langs=java']):
            with patch('os.getcwd', return_value=str(self.test_path)):
                collect_code.main()
        
        content = self.output_file.read_text()
        # Should include all files except Java
        self.assertIn("main.py", content)
        self.assertIn("util.c", content)
        self.assertIn("README.md", content)
        self.assertNotIn("App.java", content)


if __name__ == '__main__':
    unittest.main()

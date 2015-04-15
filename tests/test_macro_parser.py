import sublime
import unittest
from unittest.mock import patch, MagicMock
from Terminality.macro import Macro


def file_content(region):
    contents = """
    Hello, World!
    This might be a long file
    In which use to test something
    Blah blah blah...
    """

    return contents[region.begin():region.end()]


MockView = MagicMock(spec=sublime.View)
MockView.substr = MagicMock(side_effect=file_content)
MockView.file_name.return_value = "path/to/file.ext"

MockWindow = MagicMock(spec=sublime.Window)
MockWindow.active_view.return_value = MockView
MockWindow.folders.return_value = ["another/path/to/directory",
                                   "path/to"]


class TestMacroParser(unittest.TestCase):
    @patch('sublime.active_window', return_value=MockWindow)
    def test_none(self, active_window):
        macros = {
            "test": None,
            "expected": None,
            "required": None,
            "macros": None
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_empty(self, active_window):
        macros = {
            "test": "",
            "expected": "",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_predefined_macro1(self, active_window):
        macros = {
            "test": "",
            "expected": "",
            "required": ["file", "file_name"],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_predefined_macro2(self, active_window):
        macros = {
            "test": "$file_name",
            "expected": None,
            "required": ["required", "file_name"],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_predefined_macro3(self, active_window):
        macros = {
            "test": "$require ; $file",
            "expected": " ; path/to/file.ext",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_predefined_macro4(self, active_window):
        macros = {
            "test": "$parent$file$file_name",
            "expected": "path/topath/to/file.extfile.ext",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_predefined_macro5(self, active_window):
        macros = {
            "test": "$working$$$working_project$$$project",
            "expected": "path/to$path/to$another/path/to/directory",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro1(self, active_window):
        macros = {
            "test": "",
            "expected": None,
            "required": ["required"],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro2(self, active_window):
        macros = {
            "test": "",
            "expected": None,
            "required": ["required"],
            "macros": {
                "required": []
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro3(self, active_window):
        macros = {
            "test": "",
            "expected": None,
            "required": ["required"],
            "macros": {
                "required": [
                    1,
                    [1, 2],
                    None,
                    [None, None]
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro4(self, active_window):
        macros = {
            "test": "",
            "expected": "",
            "required": ["required"],
            "macros": {
                "required": [
                    1,
                    [1, 2],
                    None,
                    [None, None],
                    "macro_output"
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro5(self, active_window):
        macros = {
            "test": "$required",
            "expected": "",
            "required": [],
            "macros": {
                "required": [
                    1,
                    [1, 2],
                    None,
                    [None, None]
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro6(self, active_window):
        macros = {
            "test": "$selection",
            "expected": "",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro7(self, active_window):
        macros = {
            "test": "$selection",
            "expected": None,
            "required": ["selection"],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro8(self, active_window):
        MockView.sel.return_value = [sublime.Region(5, 10)]
        macros = {
            "test": "$selection",
            "expected": "Hello",
            "required": [],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro9(self, active_window):
        MockView.sel.return_value = [sublime.Region(5, 10)]
        macros = {
            "test": "$selection",
            "expected": "Hello",
            "required": ["selection"],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_required_macro10(self, active_window):
        macros = {
            "test": "",
            "expected": None,
            "required": [""],
            "macros": {}
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_recursion_macro(self, active_window):
        macros = {
            "test": "$required",
            "expected": "",
            "required": [],
            "macros": {
                "required": [
                    "$required"
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_recursion_macro2(self, active_window):
        macros = {
            "test": "$required",
            "expected": "",
            "required": [],
            "macros": {
                "required": [
                    "$required2"
                ],
                "required2": [
                    "$required"
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_recursion_macro3(self, active_window):
        macros = {
            "test": "$required$required2",
            "expected": "OutputOutput",
            "required": [],
            "macros": {
                "required": [
                    "$required2",
                    "Output"
                ],
                "required2": [
                    "$required"
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_substring_macro(self, active_window):
        macros = {
            "test": "$custom;$custom2;$custom3;$custom4",
            "expected": ".ext;.ext;.ext;.ext",
            "required": [],
            "macros": {
                "custom": [
                    "$file",
                    ["-4:"]
                ],
                "custom2": [
                    "$file_name",
                    ["-4:"]
                ],
                "custom3": [
                    ["$file", "-4:"]
                ],
                "custom4": [
                    ["$file_name", "-4:"]
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_regex_macro(self, active_window):
        macros = {
            "test": "$custom;$custom2;$custom3;$custom4",
            "expected": ".ext;.ext;.ext;.ext",
            "required": [],
            "macros": {
                "custom": [
                    "$file",
                    ["\\.\\w+$"]
                ],
                "custom2": [
                    "$file_name",
                    ["\\.\\w+$"]
                ],
                "custom3": [
                    ["$file", "\\.\\w+$"]
                ],
                "custom4": [
                    ["$file_name", "\\.\\w+$"]
                ]
            }
        }

        self.assertEqual(
            Macro.parse_macro(
                string=macros["test"],
                custom_macros=macros["macros"],
                required=macros["required"]
            ),
            macros["expected"]
        )

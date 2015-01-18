import sublime
import unittest
from unittest.mock import patch, MagicMock
from Terminality.macro import Macro


MockView = MagicMock(spec=sublime.View)
MockView.file_name.return_value = "path/to/file.ext"

MockView2 = MagicMock(spec=sublime.View)
MockView2.file_name.return_value = None

MockWindow = MagicMock(spec=sublime.Window)
MockWindow.active_view.return_value = MockView
MockWindow.folders.return_value = ["another/path/to/directory",
                                   "path/to"]

MockWindow2 = MagicMock(spec=sublime.Window)
MockWindow2.active_view.return_value = MockView2
MockWindow2.folders.return_value = ["another/path/to/directory",
                                    "more/path/to/directory"]


class TestMacroInternal(unittest.TestCase):
    def test_internal(self):
        self.assertEqual(not True, False)
        self.assertEqual(not None, True)
        self.assertEqual(not not None, False)

    @patch('sublime.active_window', return_value=MockWindow)
    def test_working_dir(self, active_window):
        self.assertEqual(
            Macro.get_working_dir(),
            "path/to"
        )
        self.assertEqual(
            Macro.get_working_name(),
            "to"
        )

    @patch('sublime.active_window', return_value=MockWindow2)
    def test_working_dir2(self, active_window):
        self.assertEqual(
            Macro.get_working_dir(),
            "another/path/to/directory"
        )
        self.assertEqual(
            Macro.get_working_name(),
            "directory"
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_working_project_dir(self, active_window):
        self.assertEqual(
            Macro.get_working_project_dir(),
            "path/to"
        )
        self.assertEqual(
            Macro.get_working_project_name(),
            "to"
        )

    @patch('sublime.active_window', return_value=MockWindow2)
    def test_working_project_dir2(self, active_window):
        self.assertEqual(
            Macro.get_working_project_dir(),
            None
        )
        self.assertEqual(
            Macro.get_working_project_name(),
            None
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_project_dir(self, active_window):
        self.assertEqual(
            Macro.get_project_dir(),
            "another/path/to/directory"
        )
        self.assertEqual(
            Macro.get_project_name(),
            "directory"
        )

    @patch('sublime.active_window', return_value=MockWindow2)
    def test_project_dir2(self, active_window):
        self.assertEqual(
            Macro.get_project_dir(),
            "another/path/to/directory"
        )
        self.assertEqual(
            Macro.get_project_name(),
            "directory"
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_parent_dir(self, active_window):
        self.assertEqual(
            Macro.get_parent_dir(),
            "path/to"
        )
        self.assertEqual(
            Macro.get_parent_name(),
            "to"
        )

    @patch('sublime.active_window', return_value=MockWindow2)
    def test_parent_dir2(self, active_window):
        self.assertEqual(
            Macro.get_parent_dir(),
            None
        )
        self.assertEqual(
            Macro.get_parent_name(),
            None
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_file_path(self, active_window):
        self.assertEqual(
            Macro.get_file_path(),
            "path/to/file.ext"
        )
        self.assertEqual(
            Macro.get_file_name(),
            "file.ext"
        )

    @patch('sublime.active_window', return_value=MockWindow2)
    def test_file_path2(self, active_window):
        self.assertEqual(
            Macro.get_file_path(),
            None
        )
        self.assertEqual(
            Macro.get_file_name(),
            None
        )

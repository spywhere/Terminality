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

MockView2 = MagicMock(spec=sublime.View)
MockView2.substr = MagicMock(side_effect=file_content)
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
    def test_selection(self, active_window):
        self.assertEqual(
            Macro.get_selection(raw=False),
            None
        )
        self.assertEqual(
            Macro.get_selection(raw=True),
            None
        )
        MockView.sel.return_value = []
        self.assertEqual(
            Macro.get_selection(raw=False),
            None
        )
        self.assertEqual(
            Macro.get_selection(raw=True),
            None
        )
        MockView.sel.return_value = [sublime.Region(11, 11)]
        self.assertEqual(
            Macro.get_selection(raw=False),
            None
        )
        self.assertEqual(
            Macro.get_selection(raw=True),
            None
        )
        MockView.sel.return_value = [sublime.Region(11, 12)]
        self.assertEqual(
            Macro.get_selection(raw=False),
            None
        )
        self.assertEqual(
            Macro.get_selection(raw=True),
            " "
        )

    @patch('sublime.active_window', return_value=MockWindow)
    def test_selection2(self, active_window):
        MockView.sel.return_value = [sublime.Region(5, 10)]
        self.assertEqual(
            Macro.get_selection(raw=False),
            "Hello"
        )

        MockView.sel.return_value = [
            sublime.Region(5, 10),
            sublime.Region(12, 17)
        ]
        self.assertEqual(
            Macro.get_selection(raw=False),
            "World"
        )

        MockView.sel.return_value = [
            sublime.Region(5, 10),
            sublime.Region(12, 17),
            sublime.Region(11, 17)
        ]
        self.assertEqual(
            Macro.get_selection(raw=False),
            "World"
        )
        self.assertEqual(
            Macro.get_selection(raw=True),
            " World"
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

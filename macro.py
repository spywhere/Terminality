import sublime
import os
import shlex


class Macro:
    @staticmethod
    def parse_macro(string, custom_macros=None, required=None):
        macros = {
            "file": shlex.quote(Macro.get_file_path()),
            "file_name": shlex.quote(Macro.get_file_name()),
            "working": shlex.quote(Macro.get_working_dir()),
            "working_project": shlex.quote(Macro.get_working_project_dir()),
            "project": shlex.quote(Macro.get_project_dir()),
            "parent": shlex.quote(Macro.get_parent_dir()),
            "parent_name": shlex.quote(Macro.get_parent_name()),
            "packages_path": shlex.quote(Macro.get_packages_path()),
            "sep": Macro.get_separator(),
            "$": "$"
        }
        required = required or []
        custom_macros = custom_macros or {}
        for macro_name in custom_macros:
            for macro in custom_macros[macro_name]:
                if macro.startswith("$") and macro[1:] in macros:
                    macros[macro_name] = macros[macro[1:]]
        for macro in macros:
            string = string.replace(
                "$"+macro, macros[macro] if macro in macros and macros[macro] else ""
            )
        for macro_name in required:
            if macro_name not in macros or not macros[macro_name]:
                return None
        return string

    @staticmethod
    def get_working_dir():
        return (Macro.get_working_project_dir() or
                Macro.get_project_dir() or
                Macro.get_parent_dir())

    @staticmethod
    def get_working_project_dir():
        folders = sublime.active_window().folders()
        for folder in folders:
            if Macro.contains_file(folder, Macro.get_file_path()):
                return folder
        return None

    @staticmethod
    def get_project_dir():
        folders = sublime.active_window().folders()
        if len(folders) > 0:
            return folders[0]
        return None

    @staticmethod
    def get_parent_dir():
        file_path = Macro.get_file_path()
        return os.path.dirname(file_path) if file_path else None

    @staticmethod
    def get_parent_name():
        parent_path = Macro.get_parent_dir()
        return os.path.basename(parent_path) if parent_path else None

    @staticmethod
    def get_packages_path():
        return sublime.packages_path()

    @staticmethod
    def get_file_path():
        return sublime.active_window().active_view().file_name()

    @staticmethod
    def get_file_name():
        file_path = Macro.get_file_path()
        return os.path.basename(file_path) if file_path else None

    @staticmethod
    def get_separator():
        return os.sep

    @staticmethod
    def contains_file(directory, file_path):
        if file_path is None:
            return False
        return os.path.normcase(
            os.path.normpath(file_path)
        ).startswith(
            os.path.normcase(os.path.normpath(directory))
        )

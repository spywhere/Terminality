import sublime
import os
import shlex


class Macro:
    @staticmethod
    def parse_macro(string, custom_macros=None, required=None, escaped=True):
        macros = {
            "file": Macro.escape_string(Macro.get_file_path(), escaped),
            "file_name": Macro.escape_string(Macro.get_file_name(), escaped),
            "working": Macro.escape_string(Macro.get_working_dir(), escaped),
            "working_project": Macro.escape_string(Macro.get_working_project_dir(), escaped),
            "project": Macro.escape_string(Macro.get_project_dir(), escaped),
            "parent": Macro.escape_string(Macro.get_parent_dir(), escaped),
            "parent_name": Macro.escape_string(Macro.get_parent_name(), escaped),
            "packages_path": Macro.escape_string(Macro.get_packages_path(), escaped),
            "sep": Macro.get_separator(),
            "$": "$"
        }
        required = required or []
        custom_macros = custom_macros or {}
        for macro_name in custom_macros:
            for macro in custom_macros[macro_name]:
                if macro.startswith("$") and macro[1:] in macros:
                    macros[macro_name] = macros[macro[1:]]

        for macro_name in required:
            if macro_name not in macros or not macros[macro_name]:
                return None

        out_string = []
        string = string.split(" ")

        while string:
            substr = string[0]
            string = string[1:]
            parsed = False
            for macro in macros:
                if substr == "$"+macro and macros[macro]:
                    parsed = True
                    out_string.append(macros[macro])
                    break
            if not parsed:
                out_string.append(substr)
        return " ".join(out_string)

    @staticmethod
    def escape_string(string, escaped=True):
        return shlex.quote(string) if escaped else string

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

import sublime
import os
import shlex
import re


MACRO_PATTERN = re.compile("\\$(\\w+|\\$)")
SUBSTR_PATTERN = re.compile("^(-?\\d+)?:(-?\\d+)?$")
MatchObject = type(re.search("", ""))


class Macro:
    @staticmethod
    def get_macros(macros=None, custom_macros=None, required=None,
                   restricted=None, arguments=None):
        if arguments is not None:
            arguments = str(arguments)
        macros = macros or {
            "file": Macro.get_file_path(
                relative=False
            ),
            "file_relative": Macro.get_file_path(
                relative=True
            ),
            "file_name": Macro.get_file_name(),
            "working": Macro.get_working_dir(
                relative=False
            ),
            "working_relative": Macro.get_working_dir(
                relative=True
            ),
            "working_name": Macro.get_working_name(),
            "working_project": Macro.get_working_project_dir(
                relative=False
            ),
            "working_project_relative": Macro.get_working_project_dir(
                relative=True
            ),
            "working_project_name": Macro.get_working_project_name(),
            "project": Macro.get_project_dir(
                relative=False
            ),
            "project_relative": Macro.get_project_dir(
                relative=True
            ),
            "project_name": Macro.get_project_name(),
            "parent": Macro.get_parent_dir(
                relative=False
            ),
            "parent_relative": Macro.get_parent_dir(
                relative=True
            ),
            "parent_name": Macro.get_parent_name(),
            "packages_path": Macro.get_packages_path(),
            "raw_selection": Macro.get_selection(raw=True),
            "selection": Macro.get_selection(raw=False),
            "arguments": arguments,
            "sep": Macro.get_separator(),
            "$": "$"
        }
        custom_macros = custom_macros or {}
        required = required or []
        restricted = restricted or []

        restricted = [x.lower() for x in restricted]

        for custom_macro_name in custom_macros:
            if custom_macro_name.lower() in restricted:
                continue
            macro_output = None
            macro_type = None
            for macro in custom_macros[custom_macro_name]:
                if isinstance(macro, str):
                    if (macro_output is not None and
                            macro_type and macro_type == "macro"):
                        break
                    macro_type = "macro"
                    macro_output = Macro.parse_macro(
                        string=macro,
                        macros=macros,
                        custom_macros=custom_macros,
                        required=required,
                        restricted=restricted+[custom_macro_name],
                        arguments=arguments,
                        internal=True
                    )
                elif isinstance(macro, list) or isinstance(macro, tuple):
                    # Macro Type: Element Type (str, int, pattern)
                    types = {
                        "substr_reg": "p",
                        "regex_reg": "s",
                        "substr_dyn": "sp",
                        "regex_dyn": "ss"
                    }

                    longest_matched = -1
                    for m_type in types:
                        macro_req = types[m_type]
                        if len(macro) < len(macro_req):
                            continue
                        matched = True
                        for i in range(len(macro_req)):
                            req_type = macro_req[i]
                            value = macro[i]
                            if (req_type == "p" and
                               (not isinstance(value, str) or
                                   not SUBSTR_PATTERN.match(value))):
                                matched = False
                                break
                            elif (req_type == "s" and
                                 (not isinstance(value, str) or
                                    SUBSTR_PATTERN.match(value))):
                                matched = False
                                break
                            elif (req_type == "i" and
                                    not isinstance(value, int)):
                                matched = False
                                break
                        if matched and longest_matched < len(macro_req):
                            macro_type = m_type
                            longest_matched = len(macro_req)

                    if macro_output is None:
                        if macro_type and macro_type.endswith("_reg"):
                            continue
                    else:
                        if macro_type and macro_type.endswith("_dyn"):
                            break

                    if macro_type:
                        if macro_type.endswith("_dyn"):
                            output = Macro.parse_macro(
                                string=macro[0],
                                macros=macros,
                                custom_macros=custom_macros,
                                required=required,
                                restricted=restricted+[custom_macro_name],
                                arguments=arguments,
                                internal=True
                            )
                            macro = macro[1:]
                        else:
                            output = macro_output

                        if output is None:
                            continue
                        if macro_type.startswith("regex_"):
                            matches = re.search(macro[0], output)
                            if matches:
                                capture = 0
                                if len(macro) > 1 and isinstance(macro[1], int):
                                    capture = int(macro[1])
                                if (capture == 0 or
                                        (matches.lastindex and
                                         capture <= matches.lastindex)):
                                    macro_output = matches.group(capture)
                        elif macro_type.startswith("substr_"):
                            substr = SUBSTR_PATTERN.match(macro[0])
                            start = int(substr.group(1) or 0)
                            end = int(substr.group(2) or len(output))
                            macro_output = output[start:end]

            if macro_output is not None:
                macros[custom_macro_name.lower()] = macro_output
        return macros

    @staticmethod
    def parse_macro(string, macros=None, custom_macros=None, required=None,
                    restricted=None, arguments=None, escaped=False,
                    internal=False):
        if isinstance(string, str):
            required = required or []
            macros_list = Macro.get_macros(
                macros=macros,
                custom_macros=custom_macros,
                required=required,
                restricted=restricted,
                arguments=arguments
            )

            if internal:
                for macro_name in [
                        x for x in re.findall(MACRO_PATTERN, string)]:
                    if (macro_name not in macros_list or
                            macros_list[macro_name] is None):
                        return None
            else:
                for macro_name in required:
                    if (macro_name not in macros_list or
                            macros_list[macro_name] is None):
                        return None

            if macros_list:
                return MACRO_PATTERN.sub(
                    lambda m: Macro.escape_string(
                        Macro.parse_macro(
                            string=m,
                            macros=macros_list,
                            custom_macros=custom_macros,
                            required=required,
                            restricted=restricted,
                            arguments=arguments
                        ) or "",
                        escaped
                    ),
                    string
                )
            else:
                return None
        elif isinstance(string, MatchObject):
            macro_name = string.group(1).lower()
            return macros[macro_name] if macro_name in macros else ""
        else:
            return None

    @staticmethod
    def escape_string(string, escaped=True):
        return shlex.quote(string) if escaped else string

    @staticmethod
    def get_working_dir(relative=False):
        if relative:
            return "." if Macro.get_working_dir(relative=False) else None
        return (Macro.get_working_project_dir(relative=False) or
                Macro.get_project_dir(relative=False) or
                Macro.get_parent_dir(relative=False))

    @staticmethod
    def get_working_name():
        working = Macro.get_working_dir(relative=False)
        return os.path.basename(working) if working else None

    @staticmethod
    def get_working_project_dir(relative=False):
        if relative:
            return ("." if Macro.get_working_project_dir(relative=False)
                    else None)
        folders = sublime.active_window().folders()
        for folder in folders:
            if Macro.contains_file(folder, Macro.get_file_path(relative=False)):
                return folder
        return None

    @staticmethod
    def get_working_project_name():
        working_project = Macro.get_working_project_dir(relative=False)
        return os.path.basename(working_project) if working_project else None

    @staticmethod
    def get_project_dir(relative=False):
        if relative:
            return "." if Macro.get_project_dir(relative=False) else None
        folders = sublime.active_window().folders()
        if len(folders) > 0:
            return folders[0]
        return None

    @staticmethod
    def get_project_name():
        project = Macro.get_project_dir(relative=False)
        return os.path.basename(project) if project else None

    @staticmethod
    def get_parent_dir(relative=False):
        if relative:
            parent_dir = Macro.get_parent_dir(relative=False)
            working_dir = Macro.get_working_dir(relative=False)
            return os.path.relpath(
                parent_dir,
                working_dir
            ) if parent_dir and working_dir else None
        file_path = Macro.get_file_path(relative=False)
        return os.path.dirname(file_path) if file_path else None

    @staticmethod
    def get_parent_name():
        parent_path = Macro.get_parent_dir(relative=False)
        return os.path.basename(parent_path) if parent_path else None

    @staticmethod
    def get_selection(raw=False):
        view = sublime.active_window().active_view()
        selections = view.sel()
        if len(selections) <= 0:
            return None
        elif raw and view.substr(selections[-1]) == "":
            return None
        elif not raw and view.substr(selections[-1]).strip() == "":
            return None
        return (view.substr(selections[-1]) if raw
                else view.substr(selections[-1]).strip())

    @staticmethod
    def get_packages_path():
        return sublime.packages_path()

    @staticmethod
    def get_file_path(relative=False):
        if relative:
            file_path = Macro.get_file_path(relative=False)
            working_dir = Macro.get_working_dir(relative=False)
            return os.path.relpath(
                file_path,
                working_dir
            ) if file_path and working_dir else None
        return sublime.active_window().active_view().file_name()

    @staticmethod
    def get_file_name():
        file_path = Macro.get_file_path(relative=False)
        return os.path.basename(file_path) if file_path else None

    @staticmethod
    def get_separator():
        return os.sep

    @staticmethod
    def contains_file(directory, file_path):
        if not file_path:
            return False
        return os.path.normcase(
            os.path.normpath(file_path)
        ).startswith(
            os.path.normcase(os.path.normpath(directory))
        )

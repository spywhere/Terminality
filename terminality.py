import sublime
import sublime_plugin
from .generic_shell import GenericShell
from .QuickMenu.QuickMenu import QuickMenu
from .macro import Macro
from .progress import ThreadProgress
from .settings import Settings
from .unit_collections import UnitCollections


TERMINALITY_VERSION = "0.3.10"


def plugin_loaded():
    Settings.reset()
    Settings.startup()
    print("[Terminality] v%s" % (TERMINALITY_VERSION))


class TerminalityRunCommand(sublime_plugin.WindowCommand):
    def parse_list(self, in_list, macros):
        out_list = []
        for value in in_list:
            if isinstance(value, str):
                value = Macro.parse_macro(
                    string=value,
                    custom_macros=macros
                )
            elif (isinstance(value, list) or
                    isinstance(value, tuple)):
                value = self.parse_list(value, macros)
            elif isinstance(value, dict):
                value = self.parse_dict(value, macros)
            out_list.append(value)
        return out_list

    def parse_dict(self, in_dict, macros):
        for key in in_dict:
            if isinstance(in_dict[key], str):
                in_dict[key] = Macro.parse_macro(
                    string=in_dict[key],
                    custom_macros=macros
                )
            elif (isinstance(in_dict[key], list) or
                    isinstance(in_dict[key], tuple)):
                in_dict[key] = self.parse_list(in_dict[key], macros)
            elif isinstance(in_dict[key], dict):
                in_dict[key] = self.parse_dict(in_dict[key], macros)
        return in_dict

    def run(self, selector=None, action=None, arguments_title=None):
        if arguments_title is None or arguments_title == "":
            self.run_command(selector, action)
            return
        self.window.show_input_panel(
            caption=arguments_title + ":",
            initial_text="",
            on_done=lambda args: self.run_command(
                selector=selector,
                action=action,
                arguments=args
            ),
            on_change=None,
            on_cancel=None
        )

    def run_command(self, selector=None, action=None, arguments=None):
        execution_unit = None
        execution_units = UnitCollections.load_default_collections()
        # Global
        additional_execution_units = Settings.get_global(
            "execution_units",
            default=Settings.get_global(
                "additional_execution_units",
                default={}
            )
        )
        for sel in [x for x in ["*", selector] if x is not None]:
            if (sel in additional_execution_units and
                    action in additional_execution_units[sel]):
                execution_unit = additional_execution_units[sel][action]
                if not isinstance(execution_unit, dict):
                    continue
        # Local
        additional_execution_units = Settings.get_local(
            "execution_units",
            default=Settings.get_local(
                "additional_execution_units",
                default={}
            )
        )
        for sel in [x for x in ["*", selector] if x is not None]:
            if (sel in additional_execution_units and
                    action in additional_execution_units[sel]):
                execution_unit = additional_execution_units[sel][action]
                if not isinstance(execution_unit, dict):
                    continue
            elif (sel in execution_units and
                    action in execution_units[sel]):
                execution_unit = execution_units[sel][action]
                if not isinstance(execution_unit, dict):
                    continue
        if execution_unit is None:
            sublime.error_message("There is no such execution unit")
            return
        if not isinstance(execution_unit, dict):
            if Settings.get("debug"):
                print("Execution unit is ignored [%s][%s]" % (selector, action))
            return
        command = None
        command_type = None
        for key in ["command", "window_command", "view_command"]:
            if key in execution_unit:
                command_type = key
                command = execution_unit[key]
                break
        if not command:
            sublime.error_message("No command to run")
            return

        custom_macros = {}
        required_macros = []
        if "macros" in execution_unit:
            custom_macros = execution_unit["macros"]
        if "required" in execution_unit:
            required_macros = execution_unit["required"]
        if "location" not in execution_unit:
            execution_unit["location"] = "$working"

        is_not_windows = sublime.platform() != "windows"
        command_script = [Macro.parse_macro(
            string=cmd,
            custom_macros=custom_macros,
            required=required_macros,
            escaped=is_not_windows,
            arguments=arguments
        ) for cmd in command.split(" ")]

        if command_type == "window_command" or command_type == "view_command":
            args = {}
            if "args" in execution_unit:
                args = execution_unit["args"]
            args = self.parse_dict(args, custom_macros)
            if command_type == "window_command":
                self.window.run_command(" ".join(command_script), args)
            else:
                self.window.active_view().run_command(
                    " ".join(command_script),
                    args
                )
        elif command_type == "command":
            working_dir = Macro.parse_macro(
                string=execution_unit["location"],
                custom_macros=custom_macros,
                required=required_macros,
                arguments=arguments
            )
            if working_dir is None:
                sublime.error_message(
                    "Working directory is invalid"
                )
                return

            if Settings.get("debug"):
                print("Running \"%s\"" % (" ".join(command_script)))
                print("Working dir is \"%s\"" % (working_dir))

            self.view = self.window.new_file()
            self.view.set_name("Running...")
            self.view.set_scratch(True)
            if is_not_windows:
                command_script = " ".join(command_script)
            shell = GenericShell(
                cmds=command_script,
                view=self.view,
                on_complete=lambda e, r, p: self.on_complete(
                    e, r, p, execution_unit
                ),
                no_echo=("no_echo" in execution_unit and
                         execution_unit["no_echo"]),
                read_only=("read_only" in execution_unit and
                           execution_unit["read_only"])
            )
            shell.set_cwd(working_dir)
            shell.start()
            ThreadProgress(
                thread=shell,
                message="Running",
                success_message="Terminal has been stopped",
                set_status=self.set_status,
                view=self.view
            )
        elif Settings.get("debug"):
            print("Invalid command type")

    def on_complete(self, elapse_time, return_code, params, execution_unit):
        if return_code is not None:
            self.view.set_name(
                "Terminal Ended (Return: {0}) [{1:.2f}s]".format(
                    return_code, elapse_time
                )
            )
            if ("close_on_exit" in execution_unit and
                    execution_unit["close_on_exit"]):
                self.view.window().focus_view(self.view)
                self.view.window().run_command("close")
            sublime.set_timeout(lambda: self.set_status(), 3000)

    def set_status(self, status=None):
        for window in sublime.windows():
            for view in window.views():
                if status is None:
                    view.erase_status("Terminality")
                else:
                    view.set_status("Terminality", status)


class TerminalityCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to run another command
    """

    qm = None
    ready_retry = 0

    main_menu = {
        "items": [["Terminality", "v" + TERMINALITY_VERSION]],
        "actions": [""]
    }

    def get_execution_units(self, execution_units_map, selector):
        execution_units = {}
        #  Default Execution Units
        for selector_name in [x for x in ["*", selector] if x is not None]:
            if selector_name in execution_units_map:
                for action in execution_units_map[selector_name]:
                    execution_units[action] = execution_units_map[
                        selector_name
                    ][action]
        for selector_name in [x for x in ["*", selector] if x is not None]:
            # Global
            additional_execution_units = Settings.get_global(
                "execution_units",
                default=Settings.get_global(
                    "additional_execution_units",
                    default={}
                )
            )
            if selector_name in additional_execution_units:
                additional_execution_units = additional_execution_units[
                    selector_name
                ]
                for key in additional_execution_units:
                    if (key in execution_units and
                            isinstance(additional_execution_units[key], dict)):
                        for sub_key in additional_execution_units[key]:
                            execution_units[key][
                                sub_key
                            ] = additional_execution_units[key][sub_key]
                    else:
                        execution_units[key] = additional_execution_units[key]
                    if isinstance(additional_execution_units[key], dict):
                        execution_units[key]["selector"] = selector
            # Local
            additional_execution_units = Settings.get_local(
                "execution_units",
                default=Settings.get_local(
                    "additional_execution_units",
                    default={}
                )
            )
            if selector_name in additional_execution_units:
                additional_execution_units = additional_execution_units[
                    selector_name
                ]
                for key in additional_execution_units:
                    if (key in execution_units and
                            isinstance(additional_execution_units[key], dict)):
                        for sub_key in additional_execution_units[key]:
                            execution_units[key][
                                sub_key
                            ] = additional_execution_units[key][sub_key]
                    else:
                        execution_units[key] = additional_execution_units[key]
                    if isinstance(additional_execution_units[key], dict):
                        execution_units[key]["selector"] = selector
        if Settings.get("debug") and not execution_units:
            print("Execution units is empty")
        return execution_units

    def generate_menu(self, ask_arguments=False):
        menu = {
            "items": [], "actions": [],
            "unsort_items": []
        }
        execution_units_map = UnitCollections.load_default_collections()
        sel_name = None
        for selector in execution_units_map:
            if (len(self.window.active_view().find_by_selector(
                    selector)) > 0):
                sel_name = selector
                break
        if not sel_name:
            for selector in Settings.get("execution_units", {}):
                if (len(self.window.active_view().find_by_selector(
                        selector)) > 0):
                    sel_name = selector
                    break
            for selector in Settings.get("additional_execution_units", {}):
                if (len(self.window.active_view().find_by_selector(
                        selector)) > 0):
                    sel_name = selector
                    break
        if Settings.get("debug") and not sel_name:
            print("Selector is not found")
        execution_units = self.get_execution_units(
            execution_units_map,
            sel_name
        )
        # Generate menu
        for action in execution_units:
            execution_unit = execution_units[action]
            if not isinstance(execution_unit, dict):
                continue
            if "selector" in execution_unit:
                selector_name = execution_unit["selector"]
            else:
                selector_name = sel_name
            custom_macros = {}
            required_macros = []
            platforms = None
            arguments_title = None
            if ask_arguments:
                arguments_title = "Arguments"
                if "arguments" in execution_unit:
                    arguments_title = execution_unit["arguments"]
            if "macros" in execution_unit:
                custom_macros = execution_unit["macros"]
            if "required" in execution_unit:
                required_macros = execution_unit["required"]
            if "platforms" in execution_unit:
                platforms = execution_unit["platforms"]
            action_name = Macro.parse_macro(
                string=action,
                custom_macros=custom_macros,
                required=required_macros,
                arguments="<Arguments>" if ask_arguments else None
            )
            if platforms:
                matched = False
                current_platforms = [
                    sublime.platform() + "-" + sublime.arch(),
                    sublime.platform(),
                    sublime.arch()
                ]
                for platform in current_platforms:
                    if platform in platforms:
                        matched = True
                        break
                if not matched:
                    continue
            if action_name is None:
                if Settings.get("debug"):
                    print("Required params is not completed")
                continue
            if "name" in execution_unit:
                action_name = Macro.parse_macro(
                    string=execution_unit["name"],
                    custom_macros=custom_macros,
                    required=required_macros,
                    arguments="<Arguments>" if ask_arguments else None
                )
            order = action_name
            if "order" in execution_unit:
                order = execution_unit["order"]
            dest = action_name + " command"
            if "description" in execution_unit:
                dest = Macro.parse_macro(
                    string=execution_unit["description"],
                    custom_macros=custom_macros,
                    required=required_macros,
                    arguments="<Arguments>" if ask_arguments else None
                )
            menu["unsort_items"] += [[
                action_name,
                dest,
                {
                    "command": "terminality_run",
                    "args": {
                        "selector": selector_name,
                        "action": action,
                        "arguments_title": arguments_title
                    }
                },
                order
            ]]
        menu["unsort_items"] = sorted(menu["unsort_items"], key=lambda x: x[3])
        while menu["unsort_items"]:
            menu["items"].append(menu["unsort_items"][0][:-2])
            menu["actions"].append(menu["unsort_items"][0][2])
            menu["unsort_items"] = menu["unsort_items"][1:]

        if (Settings.get("run_if_only_one_available") and
                len(menu["items"]) == 1):
            self.window.run_command(
                "terminality_run",
                menu["actions"][0]["args"]
            )
            return None
        if len(menu["items"]) <= 0 and Settings.get("show_nothing_if_nothing"):
            return None
        menu["items"] += self.main_menu["items"]
        menu["actions"] += self.main_menu["actions"]
        return menu

    def run(self, arguments=False, menu=None, action=None, replaceMenu=None):
        """
        Show menu to user, if ready
        """
        if not Settings.ready():
            if self.ready_retry > 2:
                sublime.message_dialog(
                    "Terminality is starting up..." +
                    "Please wait a few seconds and try again."
                )
            else:
                sublime.status_message(
                    "Terminality is starting up..." +
                    "Please wait a few seconds and try again..."
                )
            self.ready_retry += 1
            return
        if self.qm is None:
            self.qm = QuickMenu()
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        menu = self.generate_menu(arguments)
        if menu is None:
            return
        self.qm.setMenu("main", menu)
        self.qm.show(window=self.window, menu=menu, action=action)

import sublime
import sublime_plugin
from .generic_shell import GenericShell
from .QuickMenu.QuickMenu import QuickMenu
from .macro import Macro
from .progress import ThreadProgress
from .settings import Settings


TERMINALITY_VERSION = "0.2.0"


def plugin_loaded():
    Settings.reset()
    Settings.startup()
    print("[Terminality] v%s" % (TERMINALITY_VERSION))


class TerminalityRunCommand(sublime_plugin.WindowCommand):
    def run(self, selector=None, action=None):
        if selector is None:
            return

        execution_unit = None
        execution_units = Settings.get("execution_units")
        additional_execution_units = Settings.get("additional_execution_units")
        if (selector in additional_execution_units and
                action in additional_execution_units[selector]):
            execution_unit = additional_execution_units[selector][action]
        elif (selector in execution_units and
                action in execution_units[selector]):
            execution_unit = execution_units[selector][action]
        if execution_unit is None:
            sublime.error_message("There is no such execution unit")
            return
        if "command" not in execution_unit:
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

        command_script = Macro.parse_macro(
            string=execution_unit["command"],
            custom_macros=custom_macros,
            required=required_macros,
            escaped=True
        )
        working_dir = Macro.parse_macro(
            string=execution_unit["location"],
            custom_macros=custom_macros,
            required=required_macros
        )
        if command_script is None or working_dir is None:
            sublime.error_message("Required macros are missing")
            return

        self.view = self.window.new_file()
        self.view.set_name("Running...")
        self.view.set_scratch(True)
        shell = GenericShell(
            cmds=command_script,
            view=self.view,
            on_complete=lambda e, r, p: self.on_complete(
                e, r, p, execution_unit
            ),
            read_only=("read_only" in execution_unit and
                       execution_unit["read_only"])
        )
        shell.set_cwd(working_dir)
        shell.start()
        ThreadProgress(
            thread=shell,
            message="Running",
            success_message="Terminal has been stopped",
            set_status=self.set_status
        )

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

    def generate_menu(self):
        menu = {"items": [], "actions": []}
        execution_units = Settings.get("execution_units")
        additional_execution_units = Settings.get("additional_execution_units")
        selector_name = None
        for selector in execution_units:
            if len(self.window.active_view().find_by_selector(selector)) > 0:
                selector_name = selector
                break
        if selector_name is None:
            if Settings.get("show_nothing_if_nothing"):
                return None
            else:
                return self.main_menu
        # Fetch and Merge execution units
        execution_units = execution_units[selector_name]
        if selector_name in additional_execution_units:
            additional_execution_units = additional_execution_units[selector_name]
        else:
            additional_execution_units = {}
        for key in additional_execution_units:
            if key in execution_units:
                for sub_key in additional_execution_units[key]:
                    execution_units[key][sub_key] = additional_execution_units[key][sub_key]
            else:
                execution_units[key] = additional_execution_units[key]
        if (Settings.get("show_nothing_if_nothing") and
                len(execution_units) == 0):
            return None
        # Generate menu
        for action in execution_units:
            execution_unit = execution_units[action]
            custom_macros = {}
            required_macros = []
            platforms = None
            if "macros" in execution_unit:
                custom_macros = execution_unit["macros"]
            if "required" in execution_unit:
                required_macros = execution_unit["required"]
            if "platforms" in execution_unit:
                platforms = execution_unit["platforms"]
            action_name = Macro.parse_macro(
                string=action,
                custom_macros=custom_macros,
                required=required_macros
            )
            if platforms and sublime.platform() not in platforms:
                continue
            if action_name is None:
                continue
            dest = action_name + " command"
            if "description" in execution_unit:
                dest = Macro.parse_macro(
                    string=execution_unit["description"],
                    custom_macros=custom_macros,
                    required=required_macros
                )
            menu["items"] += [[action_name, dest]]
            menu["actions"] += [{
                "command": "terminality_run",
                "args": {
                    "selector": selector_name,
                    "action": action
                }
            }]
        if (Settings.get("run_if_only_one_available") and
                len(execution_units) == 1):
            self.window.run_command(
                "terminality_run",
                {"selector": selector_name, "action": action}
            )
            return None
        menu["items"] += self.main_menu["items"]
        menu["actions"] += self.main_menu["actions"]
        return menu

    def run(self, menu=None, action=None, replaceMenu=None):
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
        menu = self.generate_menu()
        if menu is None:
            return
        self.qm.setMenu("main", menu)
        self.qm.show(window=self.window, menu=menu, action=action)

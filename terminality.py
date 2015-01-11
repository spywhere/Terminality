import sublime
import sublime_plugin
from .QuickMenu.QuickMenu import QuickMenu
from .macro import Macro
from .settings import Settings


def plugin_loaded():
    Settings.reset()
    Settings.startup()


class TerminalityRunCommand(sublime_plugin.WindowCommand):
    def run(self, selector=None, action=None):
        if selector is None:
            return

        execution_unit = None
        execution_units = Settings.get("execution_units")
        additional_execution_units = Settings.get("additional_execution_units")
        if selector in additional_execution_units:
            execution_unit = additional_execution_units[selector]
        elif selector in execution_units:
            execution_unit = execution_units[selector]
        if execution_unit is None:
            sublime.error_message("There is no such execution unit")
            return
        if action not in execution_unit:
            sublime.error_message("There is no such action on execution unit")
            return
        execution_action = execution_unit[action]
        if "command" not in execution_action:
            sublime.error_message("No command to run")
            return

        custom_macros = {}
        required_macros = []
        if "macros" in execution_action:
            custom_macros = execution_action["macros"]
        if "required" in execution_action:
            required_macros = execution_action["required"]

        print(Macro.parse_macro(execution_action["command"], custom_macros, required_macros))


class TerminalityCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to run another command
    """

    qm = None
    ready_retry = 0

    main_menu = {
        "items": [["Terminality", "v0.1"]],
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
            return self.main_menu
        # Fetch and Merge execution units
        execution_units = execution_units[selector_name]
        if selector_name in additional_execution_units:
            additional_execution_units = additional_execution_units[selector_name]
        else:
            additional_execution_units = {}
        for key in additional_execution_units:
            execution_units[key] = additional_execution_units[key]
        # Generate menu
        for action in execution_units:
            execution_unit = execution_units[action]
            custom_macros = {}
            required_macros = []
            if "macros" in execution_unit:
                custom_macros = execution_unit["macros"]
            if "required" in execution_unit:
                required_macros = execution_unit["required"]
            action_name = Macro.parse_macro(
                action, custom_macros, required_macros
            )
            if action_name is None:
                continue
            dest = action_name + " command"
            if "description" in execution_unit:
                dest = Macro.parse_macro(
                    execution_unit["description"],
                    custom_macros, required_macros
                )
            menu["items"] += [[action_name, dest]]
            menu["actions"] += [{
                "command": "terminality_run",
                "args": {
                    "selector": selector_name,
                    "action": action
                }
            }]
        menu["items"] += self.main_menu["items"]
        menu["actions"] += self.main_menu["actions"]
        return menu

    def run(self, menu=None, action=None, replaceMenu=None):
        """
        Show menu to user, if ready
        """
        if not Settings.ready():
            if self.ready_retry > 2:
                sublime.message_dialog("Terminality is starting up... Please wait a few seconds and try again.")
            else:
                sublime.status_message("Terminality is starting up... Please wait a few seconds and try again...")
            self.ready_retry += 1
            return
        if self.qm is None:
            self.qm = QuickMenu()
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        self.qm.setMenu("main", self.generate_menu())
        self.qm.show(window=self.window, menu=menu, action=action)

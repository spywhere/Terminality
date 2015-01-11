import sublime
import sublime_plugin
from ..QuickMenu.QuickMenu import QuickMenu
from .settings import Settings


def plugin_loaded():
    Settings.reset()
    Settings.startup()


class TerminalityCommand(sublime_plugin.WindowCommand):

    """
    Command to show menu which use to run another command
    """

    qm = None
    ready_retry = 0

    main_menu = {
        "main": {
            "items": ["Terminality", "v0.1"],
            "actions": [""]
        }

    }

    def run(self, menu=None, action=None, replaceMenu=None):
        """
        Show menu to user, if ready
        """
        if not Settings.ready():
            if self.ready_retry > 2:
                sublime.message_dialog("Javatar is starting up... Please wait a few seconds and try again.")
            else:
                sublime.status_message("Javatar is starting up... Please wait a few seconds and try again...")
            self.ready_retry += 1
            return
        if self.qm is None:
            # from ..utils import get_snippet_list
            self.qm = QuickMenu(self.main_menu)

            # Generate action for Create menu
            # actions = []
            # for snippet in get_snippet_list():
            #     actions += [{"command": "javatar_create", "args": {"create_type": snippet[0]}}]
            # self.qm.addItems("creates", get_snippet_list(), actions)
            # self.qm.setSelectedIndex("creates", 3 if len(actions) > 0 else 2)

            # Always add Help and Support at the end
            self.qm.addItems("main", [["Help and Support...", "Utilities for Help and Support on Javatar"]], [{"name": "help"}])
        if replaceMenu is not None:
            self.qm.setMenu(replaceMenu["name"], replaceMenu["menu"])
            return
        self.qm.show(self.window, self.select, menu, action)

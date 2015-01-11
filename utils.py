import sublime
import sublime_plugin


class TerminalityUtilsCommand(sublime_plugin.TextCommand):
    def run(self, edit, util_type="", text="", region=None, dest=None):
        if util_type == "insert":
            self.view.insert(edit, 0, text)
        elif util_type == "add":
            self.view.insert(edit, self.view.size(), text)
        elif util_type == "replace":
            self.view.insert(edit, region, text)
        elif util_type == "clear":
            self.view.erase(edit, sublime.Region(0, self.view.size()))
        elif util_type == "set_read_only":
            self.view.set_read_only(True)
        elif util_type == "clear_read_only":
            self.view.set_read_only(False)

    def description(self, util_type="", text="", region=None, dest=None):
        return dest

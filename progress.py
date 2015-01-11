import sublime


class ThreadProgress():
    def __init__(self, thread, message, success_message=None, anim_fx=None,
                 set_status=None):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        if anim_fx is not None:
            self.anim_fx = anim_fx
        if set_status is not None:
            self.set_status = set_status
        sublime.set_timeout(lambda: self.run(0), 100)

    def anim_fx(self, i, message, thread):
        return {"i": (i + 1) % 3, "message": "%s %s" % (self.message, "." * (i + 1)), "delay": 300}

    def set_status(self, status=""):
        sublime.status_message(status)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, "result") and not self.thread.result:
                if hasattr(self.thread, "result_message"):
                    self.set_status(self.thread.result_message)
                else:
                    self.set_status()
                return
            if self.success_message is not None:
                self.set_status(self.success_message)
            return
        info = self.anim_fx(i, self.message, self.thread)
        tmsg = ""
        if hasattr(self.thread, "msg"):
            tmsg = self.thread.msg
        self.set_status(info["message"] + tmsg)
        sublime.set_timeout(lambda: self.run(info["i"]), info["delay"])

from handlers.handler import AbstractHandler

class HomeHandler(AbstractHandler):
    def get(self):
        self.render_template("home.html")

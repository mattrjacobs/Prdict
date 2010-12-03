from handlers.handler import AbstractHandler

class HomeHandler(AbstractHandler):
    def get(self):
        current_user = self.get_prdict_user()
        self.render_template("home.html",
                             { 'current_user' : current_user})

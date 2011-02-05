"""Handles a requset for the Prdict API version"""
from handlers.handler import AbstractHandler

class VersionHandler(AbstractHandler):
    """Builds a model of the Prdict API version"""

    def get(self):
        """Renders XML with the build number and version number"""
        self.render_template('xml/version.xml',
                             { 'build_number' : self.get_build_number(),
                               'release_number' : self.get_release_number() })

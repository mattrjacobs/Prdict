"""Handlers for web requests"""

import os

from google.appengine.dist import use_library

use_library('django', '1.2')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

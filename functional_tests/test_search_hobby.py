import os
import poplib
import re
import time
from django.core import mail
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest

class SearchHobbyTest(FunctionalTest):

    def test_search_hobby(self):
        self.browser.get(self.live_server_url)
        time.sleep(10)
        self.browser.find_element_by_name('something').send_keys()

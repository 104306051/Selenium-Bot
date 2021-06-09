# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from scrapy.http import HtmlResponse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import conf
import os

# class SingletonMetaClass(type):
#     def __init__(cls, name, bases, dict):
#         super(SingletonMetaClass, cls) \
#             .__init__(name, bases, dict)
#         original_new = cls.__new__
#
#         def my_new(cls, *args, **kwds):
#             if cls.instance == None:
#                 cls.instance = \
#                     original_new(cls, *args, **kwds)
#             return cls.instance
#
#         cls.instance = None
#         cls.__new__ = staticmethod(my_new)


class ObsDriver(RemoteWebDriver):
    """
        The driver object that adds additional method helper around selenium webdriver
        """
    # __metaclass__ = SingletonMetaClass
    SHORT_TIMEOUT = 100
    LONG_TIMEOUT = 200
    #__instance = None

    def __init__(self):
        """
            We use firefox driver by default. always use incogenito mode
        """
    #if ObsDriver.__instance is None:
        # option = webdriver.ChromeOptions()
        # option.add_argument('incognito')

        option = webdriver.FirefoxOptions()
        # option.add_argument("--headless")
        option.add_argument("--private")
        option.add_argument("--window-size=900,700")
        option.add_argument("--window-position=200,200")

        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True
        # WebDriver.__init__(self, executable_path=conf.DRIVER_PATH, firefox_profile=profile, firefox_options=option)
        RemoteWebDriver.__init__(self, command_executor="http://selenium_hub:4444/wd/hub",desired_capabilities=DesiredCapabilities.FIREFOX,options=option,browser_profile=profile)

    #@classmethod
    #def get_instance(cls):
    #    if cls.__instance is None:
    #        cls.__instance = ObsDriver()
    #    return cls.__instance

    def get_html_source(self, wait_loading=False):
        """ Return html response"""

        if wait_loading:
            WebDriverWait(self, self.SHORT_TIMEOUT) \
                .until(EC.presence_of_element_located((By.ID, "loadIndicator")))

            # Wait for indicator to disappear
            WebDriverWait(self, self.LONG_TIMEOUT) \
                .until_not(EC.presence_of_element_located((By.ID, "loadIndicator")))

        return HtmlResponse(url=self.current_url, body=self.page_source, encoding='utf-8')

    def switch_iframe(self, frame_name=None):
        if frame_name is not None:
            self.switch_to.frame(frame_name)

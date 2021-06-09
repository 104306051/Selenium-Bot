# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
import time


config = configparser.ConfigParser()
config.read('conf.ini')


class HpSSO:
    SHORT_TIMEOUT = 100

    def __init__(self, driver):
        self.driver = driver

    def get_landing_page(self, url):

        #########FOR FIREFOX##########
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, 'username')))
        self.login()

        retry_times = 5
        retry = 0
        while retry <= retry_times:
            time.sleep(20)
            try:
                if len(self.driver.find_elements_by_id('Observations')) > 0:
                    break

                else:
                    raise Exception("xxx")
            except:
                retry += 1
                self.driver.get(url)
                if len(self.driver.find_elements_by_id('username')) > 0:
                    self.login()
                continue

    def first_login(self):
        username = self.driver.find_element_by_id("inputEmailAddress")
        submit = self.driver.find_elements_by_css_selector("input.btn-primary")[0]

        username.send_keys(config['default']['SI_USERNAME'])
        submit.click()
        return self.driver.get_html_source()

    def login(self):
        username = self.driver.find_element_by_id("username")
        pwd = self.driver.find_element_by_id("password")
        submit = self.driver.find_elements_by_css_selector("input.btn-primary")[0]

        username.send_keys(config['default']['SI_USERNAME'])
        pwd.send_keys(config['default']['SI_PWD'])
        submit.click()
        return self.driver.get_html_source()

    def find_and_click_email_login(self, body):
        link_extractor = LinkExtractor()

        links = link_extractor.extract_links(body)

        for link in links:
            if link.text.strip() == 'Email & Computer Password':
                self.driver.get(link.url)
                try:
                    self.driver.find_element_by_id("username")
                    return self.login()
                except NoSuchElementException:
                    pass

        src = self.driver.get_html_source()
        return src

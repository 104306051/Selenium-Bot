# -*- coding: utf-8 -*-
from obscreator.hpsso import HpSSO
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import re
from logger import logger
import time


class Obs:
    SHORT_TIMEOUT = 100
    LONG_TIMEOUT = 100

    def __init__(self, driver):
        self.driver = driver
        # self.sqs = boto3.resource('sqs', region_name=conf.SQS_REGION_NAME,
        #                           aws_access_key_id=conf.SQS_ACCESS_KEY_ID,
        #                           aws_secret_access_key=conf.SQS_SECRET_ACCESS_KEY)

    def login_si(self, url):
        sso = HpSSO(self.driver)
        sso.get_landing_page(url)

    def create_obs(self, msg):
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, 'Observations')))

        click_new_obs = self.driver.find_element_by_link_text('Observations')
        click_new_obs.click()

        # SI page is iframed..hence we need to find mainContent page to work on it
        self.driver.switch_iframe(frame_name="mainContent")


        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'ctl00_subNavMain_subMenu')))

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'btnNew')))

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))

        time.sleep(20)

        link_new_obs = self.driver.find_element_by_link_text('New Observation')
        # link_new_obs = self.driver.find_elements_by_xpath("//*[contains(text(), 'New Observation')]")
        link_new_obs.click()

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_rblWorkGroups')))

        # select work group
        self.select_group(msg['Workgroup'])

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_ucObservation_ucPlatformComponent1_panPrimaryProduct')))


        # select primary product
        self.select_product_dropdown('ddlPrimaryProduct', msg['PrimaryProduct'],
                                     (By.XPATH, "//select[@class='ddlPrimaryProduct']/option[2]"))

        # select product version
        self.select_product_dropdown('ddlProductVersion', msg['ProductVersion'],
                                     (By.XPATH, "//select[@class='ddlProductVersion']/option[2]"))

        # select component type
        self.select_product_dropdown('ddlComponentType', msg['ComponentType'],
                                     (By.XPATH, "//select[@class='ddlComponentType']/option[2]"))

        # select sub system
        self.select_product_dropdown('ddlSubSystem', msg['SubSystem'],
                                     (By.XPATH, "//select[@class='ddlSubSystem']/option[2]"))

        # select Component
        self.select_product_dropdown('ddlComponent', msg['Component'],
                                     (By.XPATH, "//select[@class='ddlComponent']/option[2]"))
        # select Component Version
        self.select_product_dropdown('ddlLevelSix', msg['ComponentVersion'],
                                     (By.XPATH, "//select[@class='ddlLevelSix']/option[2]"))

        # select Component Locale
        self.select_product_dropdown('ddlLevelSeven', msg['ComponentLocalization'],
                                     (By.XPATH, "//select[@class='ddlLevelSeven']/option[2]"))

        # select Component Part Number
        self.select_product_dropdown('ddlLevelEight', msg['ComponentPartNo'],
                                     (By.XPATH, "//select[@class='ddlLevelEight']/option[2]"))

        btn_next = self.driver.find_element_by_link_text('Next')
        btn_next.click()

        # Wait for Component text to be loaded on page
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(
            EC.text_to_be_present_in_element((By.XPATH, "//table[@class='dvMain']//span[contains(@id,'_lblPlatform')]"),
                                             msg['PrimaryProduct']))

        # Select frequency
        ddl_frequency = self.driver.find_element_by_xpath("//select[contains(@id,'ddlFrequency')]")
        Select(ddl_frequency).select_by_visible_text(msg['Frequency'])

        # Select Gating Milestone
        ddl_gating_milestone = self.driver.find_element_by_xpath("//select[contains(@id, '_ddlGatingMilestone')]")
        Select(ddl_gating_milestone).select_by_visible_text(msg['GatingMilestone'])

        # Select Test Escape
        ddl_test_escape = self.driver.find_element_by_xpath("//select[contains(@id, '_dllTestEscape')]")
        Select(ddl_test_escape).select_by_visible_text(msg['TestEscape'])

        # Select Severity
        ddl_severity = self.driver.find_element_by_xpath("//select[contains(@id, '_ddlSeverity')]")
        Select(ddl_severity).select_by_visible_text(msg['Severity'])

        # Select Impacts
        ddl_severity = self.driver.find_element_by_xpath("//select[contains(@id, '_ddlImpactedBy')]")
        Select(ddl_severity).select_by_visible_text(msg['Impacts'])

        # fill in short description
        txt_short_descrip = self.driver.find_element_by_xpath("//textarea[contains(@name, 'txtShortDescription')]")
        txt_short_descrip.click()
        txt_short_descrip.send_keys(msg['ShortDescription'])

        # fill in Long Description
        txt_long_descrip = self.driver.find_element_by_xpath(
            "//iframe[contains(@id, '_txtLongDescription_ifr')]")
        txt_long_descrip.click()
        txt_long_descrip.send_keys(" ")  # so tinymce won't eat our text

        txt_long_descrip.send_keys(msg['LongDescription'] + '\n')
        # for adding attach download url
        txt_long_descrip.send_keys("###############" + '\n')
        if msg['AttachInfo']:
            for url in msg['AttachInfo']:
                txt_long_descrip.send_keys('Download Attachment: ' + url.get('Url') + '\n')
        txt_long_descrip.send_keys("###############")

        # fill in Steps to Reproduce
        txt_reprosteps_descrip = self.driver.find_element_by_xpath("//iframe[contains(@id, '_txtReproSteps_ifr')]")
        txt_reprosteps_descrip.click()
        txt_reprosteps_descrip.send_keys(" ")  # so tinymce won't eat our text
        txt_reprosteps_descrip.send_keys(msg['Steps'])

        # fill in customer impact
        txt_cust_impact_descrip = self.driver.find_element_by_xpath("//iframe[contains(@id, '_txtCustomerImpact_ifr')]")
        txt_cust_impact_descrip.click()
        txt_cust_impact_descrip.send_keys(" ")  # so tinymce won't eat our text
        txt_cust_impact_descrip.send_keys(msg['CustomerImpact'])

        # Sve OBS
        btn_save = self.driver.find_element_by_xpath("//a[@class='btnSave']")
        btn_save.click()

        # Extract ObsId
        obs_id = self.extract_obs_id()
        return obs_id

    def select_product_dropdown(self, class_name, visual_text, wait_by):
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(
            EC.presence_of_element_located(wait_by)
        )

        element = Select(self.driver.find_element_by_class_name(class_name))
        element.select_by_visible_text(visual_text)

    # assign bot to use the right workgroup same as the tester at the beginning (radio)
    def select_group(self, group_name):
        try:
            WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
                .until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, '_rblWorkGroups')]")))

            WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
                .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))

            WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
                .until(EC.element_to_be_clickable(
                (By.ID, 'ctl00_ContentPlaceHolder1_rblWorkGroups_0')))

            radio = self.driver.find_element_by_xpath(f"//label[contains(., '{group_name}')]")
            radio.click()

            retry_times = 30
            retry = 0
            while retry <= retry_times:
                #print(retry)
                if len(self.driver.find_elements_by_xpath(f"//label[contains(., '{group_name}')]")) > 0:
                    radio.click()
                    #print('radio btn retry succeed')
                    break
                retry += 1
                time.sleep(1)
        except NoSuchElementException:
            print("no that workgroup for Bot")

    # for changing the assign tester to the right workgroup (checkbox)
    def select_user_workgroup(self, group_name):
        try:
            check_box = self.driver.find_element_by_xpath(f"//span[contains(., '{group_name}')]//preceding-sibling::input[@type='checkbox']")

            if check_box.get_attribute('checked'):
                print("checked already")
            else:
                check_box.click()

        except NoSuchElementException:
            print("user is not in the workgroup or not assigned tester")
            logger.info("user is not in the workgroup or not assigned tester")

    def extract_obs_id(self):
        WebDriverWait(self.driver, self.LONG_TIMEOUT) \
            .until(
            EC.visibility_of_element_located((By.XPATH,
                                            "//span[contains(@id, '_PageOptionsHead_lblTitle') and contains(., 'Observation Id:')]")))

        lbl_obs_id = self.driver.find_element_by_xpath("//span[contains(@id, '_PageOptionsHead_lblTitle')]")
        return re.compile('Observation Id:\s(?P<obsid>.*)').match(lbl_obs_id.text).group('obsid')

    def change_owner(self, owner, work_group):
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucObservation_dvObservation_txtStepstoReproduceframe")))
        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))

        actors = self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_PageOptionsHead_btnAction')
        actors.click()

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))

        self.driver.switch_iframe(frame_name="iActors")

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ucActors1_gvActors_ctl02_btnSelectOwner")))

        # change assigned tester
        old_assigned_tester = self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ucActors1_gvActors_ctl02_btnSelectOwner")
        old_assigned_tester.click()

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "ctl00_ucUser_txtSearch")))

        new_assigned_tester = self.driver.find_element_by_id("ctl00_ucUser_txtSearch")
        new_assigned_tester.send_keys(owner)

        search_user = self.driver.find_element_by_id("ctl00_ucUser_btnUserSearch")
        search_user.click()

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.visibility_of_element_located((By.XPATH,
                                                     "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                                                     "'abcdefghijklmnopqrstuvwxyz'),'" + owner + "')]")))

        # select work group
        self.select_user_workgroup(work_group)

        submit = self.driver.find_element_by_id("ctl00_ucUser_gvUsers_ctl02_btnSelectUser")
        submit.click()

        WebDriverWait(self.driver, self.SHORT_TIMEOUT) \
            .until(EC.invisibility_of_element_located((By.XPATH, "//div[@id='loadIndicator']")))



# -*- coding: utf-8 -*-
import platform
import os

os.chdir(os.path.dirname(__file__))
dir_path = os.getcwd()
DRIVER_PATH = dir_path + '/drivers/geckodriver_linux' if platform.system() == 'Linux' else dir_path + '\drivers\geckodriver.exe'

LOGDIR = './logs'
REQUEST_DROPBOX = './requests'



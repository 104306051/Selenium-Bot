from obscreator.obs import Obs
from drivers.driver import ObsDriver
from logger import logger
import requests
import configparser
import pymssql
import threading
from multiprocessing.pool import ThreadPool
import traceback
import signal
import os
from html import unescape

env = os.getenv('ENV', 'testing')
config = configparser.ConfigParser()
config.read('conf.ini')

print("==========Sherlock Sibot " + env + " ==========")

threadLocal = threading.local()


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("SIGINT/SIGTERM captured")
        self.kill_now = True


def transform_message(msg):
    return {
        "RequestId": msg['RequestId'],
        "Originator": "wen-hao.lee@hp.com",
        "Workgroup": msg['Workgroup'],
        # "Workgroup": "obs-partner-Pegatron-ODM",
        "PrimaryProduct": "Func Tst - Test Tools",
        "ProductVersion": "Test Tools - HP",
        "ComponentType": "SW",
        "SubSystem": "Internal Tool",
        "Component": "sw test - please ignore it",
        "ComponentVersion": "1,0,0 || XX",
        "ComponentLocalization": "XX",
        "ComponentPartNo": "289504",
        "Frequency": "Intermittent: <1%",
        "GatingMilestone": msg['GatingMilestone'],
        "TestEscape": msg['TestEscape'],
        "Severity": "4 - Low",
        "Impacts": msg['Impacts'],
        "ShortDescription": "Test Only",
        "LongDescription": msg['LongDescription'],
        "Steps": "steps",
        "CustomerImpact": msg['CustomerImpact'],
        "ModelName": msg['ModelName'],
        "ModelVersion": msg['ModelVersion'],
        "AiPredBucketTop3": msg['AiPredBucketTop3'],
        "AiPredEncodedBucketTop3": msg['AiPredEncodedBucketTop3'],
        "AttachInfo": msg['AttachInfo']
    }


def sibotTask(msg):
    retry_times = 5
    retry = 0
    int_obs_id = None
    ownerUpdated = False
    expMsg = ''
    while int_obs_id is None and retry <= retry_times:
        try:
            driver = None
            driver = ObsDriver()
            driver.get(config['default']['SI_URL'])
            obs = Obs(driver)
            obs.login_si(config['default']['SI_URL'])
            obs_id = obs.create_obs(msg)
            int_obs_id = obs_id[3:]
            print("RequestID:" + msg['RequestId'] + ", OBS:" + int_obs_id)

            owner = msg['Originator']
            work_group = msg['Workgroup']
            obs.change_owner(owner, work_group)
            ownerUpdated = True

        except Exception as e:
            traceback.print_exc()
            expMsg = str(e)
        finally:
            if driver != None:
                # print("quiting driver")
                driver.quit()
            retry += 1

    owner_retry_times = 5
    owner_retry = 0
    while int_obs_id is not None and not ownerUpdated and owner_retry <= owner_retry_times:
        try:
            driver = None
            driver = ObsDriver()
            print("retry change owner: " + int_obs_id)
            driver.get(config['default']['SI_OBS_URL'] + int_obs_id)
            obs = Obs(driver)
            obs.login_si(config['default']['SI_OBS_URL'] + int_obs_id)
            owner = msg['Originator']
            work_group = msg['Workgroup']
            driver.switch_iframe(frame_name="mainContent")
            obs.change_owner(owner, work_group)
            ownerUpdated = True
        except Exception as e:
            traceback.print_exc()
            expMsg = str(e)
        finally:
            if driver != None:
                driver.quit()
            owner_retry += 1


    auth_token = config[env]['TOKEN']
    url = config[env]['URL'] + 'UpdateObservationCreationRequest'
    hed = {'Authorization': 'Bearer ' + auth_token}
    obsCreaReqUpdated = False
    if int_obs_id:
        try:
            # write in Nebula DB
            server = 'housireport01.auth.hpicorp.net'
            database = 'SIO'
            username = 'Sherlock'
            password = 'jck.mha-17'
            conn = None
            conn = pymssql.connect(server=server,
                                   user=username,
                                   password=password,
                                   database=database)
            cursor = conn.cursor()
            obsInfo = [(int(int_obs_id), msg['ModelName'], msg['ModelVersion'], msg['AiPredEncodedBucketTop3'],
                        msg['Originator'])]
            cursor.executemany("INSERT INTO [SIO].[dbo].[AutoCreatedObs] VALUES (%d,NULL,0,%s,%s,%s,%s)", obsInfo)
            conn.commit()
        except Exception as e:
            traceback.print_exc()
            n_data = {'requestId': msg['RequestId'], 'processStatus': 'Succeeded', 'observationId': int_obs_id,
                      'FailedReason': str(e)}
            response = requests.post(url, json=n_data, headers=hed)
            logger.error(n_data)
            obsCreaReqUpdated = True
        finally:
            if conn != None:
                conn.close()
    try:
        if int_obs_id and not obsCreaReqUpdated:
            data = {'requestId': msg['RequestId'], 'processStatus': 'Succeeded', 'observationId': int_obs_id,
                    'FailedReason': ''}
            response = requests.post(url, json=data, headers=hed)
            logger.info(data)
            print(data)
        elif not int_obs_id and not obsCreaReqUpdated:
            data = {'requestId': msg['RequestId'], 'processStatus': 'Failed', 'observationId': '',
                    'FailedReason': expMsg}
            response = requests.post(url, json=data, headers=hed)
            logger.error(data)
    except Exception as e:
        traceback.print_exc()


killer = GracefulKiller()
pool = ThreadPool(4)
while not killer.kill_now:
    try:
        auth_token = config[env]['TOKEN']
        url = config[env]['URL'] + 'GetObservationCreationRequestFromQueue'
        hed = {'Authorization': 'Bearer ' + auth_token}
        data = {'maxNumberOfMessages': '2', 'waitTimeSeconds': '5'}
        proxies = {'http': 'http://web-proxy.jp.hpicorp.net:8080', 'https': 'http://web-proxy.jp.hpicorp.net:8080'}
        response = requests.post(url, json=data, headers=hed)
        initial_msgs = response.json()
        if initial_msgs:
            print(initial_msgs)
            logger.info(initial_msgs)
        msgs = [transform_message(msg) for msg in initial_msgs] if env != "prod" else initial_msgs
        for i, msg in enumerate(msgs):
            for key, value in msg.items():
                if value == 'NA':
                    msg[key] = ' ' if key == "CustomerImpact" else 'Select'
                elif key == 'ShortDescription' or key == 'LongDescription' or key == 'Steps' or key == 'CustomerImpact':
                    msg[key] = unescape(value)

        pool.map(sibotTask, msgs)

    except Exception:
        traceback.print_exc()

pool.close()
pool.join()

print("exiting gracefully..")

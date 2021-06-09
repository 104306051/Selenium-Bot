import os

import docker
from docker.types import ServiceMode
import logging


def scaling_out_policy(ratio):
    if ratio > 2:
        return 3
    if ratio > 1.5:
        return 2
    if ratio > 1:
        return 1


class OnPremiseAutoScaler(object):

    def __init__(self, image_name, app_name, min_size):
        self.image_name = image_name
        self.app_name = app_name
        self.min_size = min_size
        self.dock = docker.DockerClient()
        self.current_size = self.check_current_size()
        self.desired_size = self.current_size

    def get_service(self):
        service_list = self.dock.services.list(filters={'name': self.app_name})
        if len(service_list) != 0:
            return service_list[0]
        return None

    def check_current_size(self):
        service = self.get_service()
        if service is None:
            return 0
        return len(service.tasks({'desired-state': 'running'}))

    def scale(self, ratio, access_key, secrete_key):
        logging.info(f'Current size: {self.current_size}')
        if self.current_size == 0:
            logging.info(f'{self.app_name} is not existed, start to create service')
            self.dock.services.create(image=self.image_name,
                                      name=self.app_name,
                                      # constraints=['node.role == manager'],
                                      mode=ServiceMode(mode='replicated', replicas=self.min_size),
                                      networks=[os.environ.get("SWARM_NETWORK", "host")],
                                      env=[#f'AWS_ACCESS_KEY_ID={access_key}',
                                           #f'AWS_SECRET_ACCESS_KEY={secrete_key}',
                                           #f'AWS_REGION={os.environ.get("AWS_REGION", "us-east-2")}',
                                           f'XRAY_DAEMON_ADDRESS={os.environ.get("XRAY_DAEMON_ADDRESS", "localhost:2000")}',
                                           f'ENV={os.environ.get("ENV", "testing")}'
                                           ])

        else:
            service = self.get_service()
            if ratio <= 1:
                if self.current_size > self.min_size:
                    logging.info('Execute scale in')
                    self.desired_size -= 1
                    logging.info(f'Desired size: {self.desired_size}')
                else:
                    logging.info('Desired size not changed')
                    logging.info('Not execute scaling')
            else:
                logging.info('Execute scale out')
                self.desired_size += scaling_out_policy(ratio)
                logging.info(f'Desired size: {self.desired_size}')
            service.scale(self.desired_size)
